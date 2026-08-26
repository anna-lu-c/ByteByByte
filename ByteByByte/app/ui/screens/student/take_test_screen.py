# take_test_screen.py
import customtkinter as ctk
from tkinter import messagebox
import time
import random
import json
import os
import tempfile
import shutil
from PIL import Image

import app.core.config as cfg
from app.ui.widgets.buttons import StyledButton
from app.ui.widgets.cards import StyledLabel, StyledFrame
from app.core.database import save_test_answers, start_test_assignment
from app.core.constants import SUBTYPES_BY_TASK
from app.repositories.task_repository import TaskLoader
from app.services.game_service import add_xp, add_bytes
from app.utils.toast import Toast
from app.utils.confetti import Confetti


class TakeTestScreen(ctk.CTkFrame):
    def __init__(self, master, dashboard, assignment_id, test_title, tasks_dict, time_limit, **kwargs):
        super().__init__(master, fg_color=cfg.BG_COLOR, **kwargs)
        self.dashboard = dashboard
        self.user_id = dashboard.user_id
        self.assignment_id = assignment_id
        self.test_title = test_title
        self.tasks_dict = tasks_dict
        self.time_limit = time_limit * 60

        self.questions = []
        self.user_answers = {}
        self.start_time = None
        self.timer_running = False
        self.completed = False

        self.setup_ui()
        self.generate_questions()
        self.build_interface()
        self.start_test()

    def setup_ui(self):
        top = StyledFrame(self)
        top.pack(fill="x", padx=10, pady=10)
        self.timer_label = StyledLabel(top, text=f"Осталось: {self.time_limit//60:02d}:00",
                                       font=("Noto Sans Condensed", 18, "bold"))
        self.timer_label.pack(side="left", padx=20)
        StyledButton(top, text="Завершить", command=self.confirm_finish, fg_color="#d9534f",
                     width=120).pack(side="right", padx=20)

        self.main_frame = StyledFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def generate_questions(self):
        for num, count in self.tasks_dict.items():
            num = int(num)
            subtypes = SUBTYPES_BY_TASK.get(num, ["Задания для подготовки"])
            all_tasks = []
            for st in subtypes:
                tasks = TaskLoader.get_tasks(num, st)
                all_tasks.extend(tasks)
            if not all_tasks:
                continue
            chosen = random.choices(all_tasks, k=min(count, len(all_tasks)))
            while len(chosen) < count:
                chosen.append(random.choice(all_tasks))
            for task in chosen:
                self.questions.append({
                    'number': num,
                    'question': task['question'],
                    'answer': task['answer'],
                    'hint': task.get('hint', ''),
                    'image': task.get('image'),
                    'file': task.get('file')
                })
        random.shuffle(self.questions)

    def build_interface(self):
        for w in self.main_frame.winfo_children():
            w.destroy()

        left = ctk.CTkScrollableFrame(self.main_frame, width=120,
                                      fg_color=cfg.COLORS[cfg.current_theme]["muted"])
        left.pack(side="left", fill="y", padx=(5,0), pady=5)
        StyledLabel(left, text="Задания", font=("Noto Sans Condensed", 14, "bold")).pack(pady=5)

        self.nav_buttons = {}
        for i, q in enumerate(self.questions):
            btn = ctk.CTkButton(left, text=f"№{q['number']}", width=90, height=30,
                                corner_radius=8, fg_color=cfg.BTN_COLOR, hover_color=cfg.BTN_HOVER,
                                text_color=cfg.TEXT_COLOR, command=lambda idx=i: self.show_question(idx))
            btn.pack(pady=2, padx=5)
            self.nav_buttons[i] = btn

        self.question_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color=cfg.BG_COLOR)
        self.question_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        self.show_question(0)

    def show_question(self, idx):
        self.current_q = idx
        for w in self.question_frame.winfo_children():
            w.destroy()

        q = self.questions[idx]
        StyledLabel(self.question_frame, text=f"Задание №{q['number']}",
                    font=("Noto Sans Condensed", 18, "bold")).pack(pady=10)

        if q.get('image'):
            img_path = os.path.join(cfg.IMAGES_DIR, q['image'])
            if os.path.exists(img_path):
                try:
                    pil_img = Image.open(img_path)
                    max_w = 500
                    if pil_img.width > max_w:
                        ratio = max_w / pil_img.width
                        pil_img = pil_img.resize((max_w, int(pil_img.height*ratio)), Image.Resampling.LANCZOS)
                    ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
                    img_lbl = ctk.CTkLabel(self.question_frame, image=ctk_img, text="")
                    img_lbl.image = ctk_img
                    img_lbl.pack(pady=5)
                except Exception as e:
                    StyledLabel(self.question_frame, text=f"⚠ Ошибка изображения: {e}").pack()

        StyledLabel(self.question_frame, text=q['question'], wraplength=700, justify="left").pack(pady=10)

        if q.get('file'):
            file_names = [f.strip() for f in q['file'].split(",") if f.strip()]
            for fn in file_names:
                fp = os.path.join(cfg.FILES_DIR, fn)
                if os.path.exists(fp):
                    def make_open_callback(path):
                        return lambda: os.startfile(path)
                    StyledButton(self.question_frame, text=f"📎 {os.path.basename(fn)}",
                                 command=make_open_callback(fp), width=250).pack(pady=2, anchor="w")

        ans_frame = StyledFrame(self.question_frame)
        ans_frame.pack(fill="x", pady=10)
        StyledLabel(ans_frame, text="Ваш ответ:").pack(side="left", padx=5)
        self.answer_entry = ctk.CTkEntry(ans_frame, width=200, text_color=cfg.TEXT_COLOR)
        self.answer_entry.pack(side="left", padx=5)
        if idx in self.user_answers:
            self.answer_entry.insert(0, self.user_answers[idx])

        StyledButton(ans_frame, text="Сохранить", command=lambda: self.save_answer(idx), width=100).pack(side="left", padx=10)

        nav = StyledFrame(self.question_frame)
        nav.pack(pady=10)
        if idx > 0:
            StyledButton(nav, text="← Предыдущее", command=lambda: self.show_question(idx-1), width=120).pack(side="left", padx=5)
        if idx < len(self.questions)-1:
            StyledButton(nav, text="Следующее →", command=lambda: self.show_question(idx+1), width=120).pack(side="left", padx=5)

        self.update_nav_style()

    def save_answer(self, idx):
        ans = self.answer_entry.get().strip()
        self.user_answers[idx] = ans
        self.update_nav_style()
        if hasattr(self, 'answer_entry'):
            self.answer_entry.configure(border_color=cfg.SUCCESS_COLOR)

    def update_nav_style(self):
        for i, btn in self.nav_buttons.items():
            if i == self.current_q:
                btn.configure(fg_color=cfg.BTN_HOVER)
            elif i in self.user_answers and self.user_answers[i]:
                btn.configure(fg_color="#5cb85c")
            else:
                btn.configure(fg_color=cfg.BTN_COLOR)

    def start_test(self):
        self.start_time = time.time()
        self.timer_running = True
        start_test_assignment(self.assignment_id)
        self.update_timer()

    def update_timer(self):
        if not self.timer_running or self.completed:
            return
        elapsed = time.time() - self.start_time
        remaining = max(0, self.time_limit - elapsed)
        if remaining <= 0:
            self.finish_test()
            return
        mins, secs = divmod(int(remaining), 60)
        self.timer_label.configure(text=f"Осталось: {mins:02d}:{secs:02d}")
        self.after(1000, self.update_timer)

    def confirm_finish(self):
        if messagebox.askyesno("Завершить", "Вы уверены, что хотите завершить тест?"):
            self.finish_test()

    def finish_test(self):
        if self.completed:
            return
        self.completed = True
        self.timer_running = False

        if hasattr(self, 'answer_entry'):
            self.save_answer(self.current_q)

        score = 0
        answers_record = {}
        for i, q in enumerate(self.questions):
            user_ans = self.user_answers.get(i, "").strip()
            correct = q['answer']
            is_correct = (user_ans == correct)
            if is_correct:
                score += 1
            answers_record[q['number']] = {'user': user_ans, 'correct': correct, 'is_correct': is_correct}

        save_test_answers(self.assignment_id, answers_record, score)

        xp_gain = score * 10
        bytes_gain = score * 5
        level_up, bytes_earned = add_xp(self.user_id, xp_gain, master=self.winfo_toplevel())
        add_bytes(self.user_id, bytes_gain)

        Toast(self.winfo_toplevel(), f"Тест завершён! +{xp_gain} XP, +{bytes_gain} байтов", is_success=True)
        if level_up:
            Toast(self.winfo_toplevel(), f"🎉 Уровень {level_up}! +{bytes_earned} байтов", is_success=True)
            Confetti(self.winfo_toplevel())

        self.dashboard.restore_center()
