# exam_test_screen.py
import customtkinter as ctk
from tkinter import messagebox
import time
import random
import os
import tempfile
import shutil
from PIL import Image

import app.core.config as cfg
from app.ui.widgets.buttons import StyledButton
from app.ui.widgets.cards import StyledLabel, StyledFrame
from app.core.database import save_exam_result
from app.core.constants import SUBTYPES_BY_TASK, TOTAL_TASKS
from app.repositories.task_repository import TaskLoader
from app.services.game_service import add_xp, add_bytes
from app.utils.toast import Toast
from app.utils.confetti import Confetti


class ExamTestScreen(ctk.CTkFrame):
    """Экран прохождения теста: таймер, навигация, поля ответов + геймификация."""

    def __init__(self, master, user_id, username, first_name, last_name, class_name, on_finish_callback=None, **kwargs):
        super().__init__(master, fg_color=cfg.BG_COLOR, **kwargs)
        self.master = master
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.class_name = class_name
        self.on_finish_callback = on_finish_callback

        self.total_questions = TOTAL_TASKS
        self.questions = []
        self.user_answers = {}
        self.start_time = None
        self.time_limit = cfg.EXAM_TIME_LIMIT
        self.timer_running = False
        self.completed = False
        self.test_active = False

        self.setup_ui()
        self.start_exam()

    def setup_ui(self):
        top_frame = StyledFrame(self)
        top_frame.pack(fill="x", padx=10, pady=10)

        self.timer_label = StyledLabel(top_frame, text="Осталось: 235:00", font=("Noto Sans Condensed", 18, "bold"))
        self.timer_label.pack(side="left", padx=20)

        self.finish_btn = ctk.CTkButton(top_frame, text="Завершить досрочно", command=self.confirm_finish,
                                        fg_color="#d9534f", hover_color="#c9302c", text_color=cfg.TEXT_COLOR,
                                        width=150)
        self.finish_btn.pack(side="right", padx=20)

        self.main_frame = StyledFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def start_exam(self):
        self.generate_variant()
        self.test_active = True
        self.completed = False
        self.user_answers = {}
        self.start_time = time.time()
        self.timer_running = True
        self.build_test_interface()
        self.update_timer()

    def generate_variant(self):
        self.questions = []
        subtypes_19_21 = SUBTYPES_BY_TASK[19]
        chosen_subtype_19_21 = random.choice(subtypes_19_21)

        blocks_19_data = TaskLoader.load_all().get("19", {}).get("subtypes", {}).get(chosen_subtype_19_21, [])
        chosen_block = random.choice(blocks_19_data) if blocks_19_data else None

        for num in range(1, TOTAL_TASKS + 1):
            if num in (19, 20, 21):
                if chosen_block is not None:
                    task = chosen_block.copy()
                else:
                    task = {"question": f"Заглушка {num}", "answer": "0", "hint": ""}
            else:
                subtype = random.choice(SUBTYPES_BY_TASK.get(num, ["Задания для подготовки"]))
                tasks = TaskLoader.get_tasks(num, subtype)
                task = random.choice(tasks) if tasks else {"question": f"Заглушка {num}", "answer": "0", "hint": ""}

            self.questions.append({
                'number': num,
                'question': task['question'],
                'answer': task['answer'],
                'hint': task.get('hint', ''),
                'image': task.get('image'),
                'file': task.get('file')
            })

    def build_test_interface(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Динамический цвет боковой панели
        left_frame = ctk.CTkScrollableFrame(self.main_frame, width=120,
                                            fg_color=cfg.COLORS[cfg.current_theme]["muted"])
        left_frame.pack(side="left", fill="y", padx=(5, 0), pady=5)

        StyledLabel(left_frame, text="Задания", font=("Noto Sans Condensed", 14, "bold")).pack(pady=5)

        self.nav_buttons = {}
        for i in range(1, TOTAL_TASKS + 1):
            btn = ctk.CTkButton(
                left_frame,
                text=f"№{i}",
                width=90,
                height=30,
                corner_radius=8,
                fg_color=cfg.BTN_COLOR,
                hover_color=cfg.BTN_HOVER,
                text_color=cfg.TEXT_COLOR,
                font=("Noto Sans Condensed", 12, "bold"),
                command=lambda n=i: self.show_question(n)
            )
            btn.pack(pady=2, padx=5)
            self.nav_buttons[i] = btn

        self.question_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color=cfg.BG_COLOR)
        self.question_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        self.current_q_number = 1
        self.show_question(1)

    def show_question(self, number):
        self.current_q_number = number
        for widget in self.question_frame.winfo_children():
            widget.destroy()

        task = self.questions[number - 1]

        StyledLabel(self.question_frame, text=f"Задание №{number}",
                    font=("Noto Sans Condensed", 18, "bold")).pack(pady=10)

        if "image" in task and task["image"]:
            img_path = os.path.join(cfg.IMAGES_DIR, task["image"])
            if os.path.exists(img_path):
                try:
                    pil_img = Image.open(img_path)
                    max_w = 500
                    if pil_img.width > max_w:
                        ratio = max_w / pil_img.width
                        pil_img = pil_img.resize((max_w, int(pil_img.height * ratio)),
                                                 Image.Resampling.LANCZOS)
                    ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
                    img_lbl = ctk.CTkLabel(self.question_frame, image=ctk_img, text="")
                    img_lbl.image = ctk_img
                    img_lbl.pack(pady=5)
                except Exception as e:
                    StyledLabel(self.question_frame, text=f"⚠ Ошибка загрузки изображения: {e}",
                                font=("Noto Sans Condensed", 12)).pack(pady=5)

        StyledLabel(self.question_frame, text=task['question'],
                    font=("Noto Sans Condensed", 14), wraplength=700, justify="left").pack(pady=10)

        if "file" in task and task["file"]:
            file_names = [f.strip() for f in task["file"].split(",") if f.strip()]
            for file_name in file_names:
                original_path = os.path.join(cfg.FILES_DIR, file_name)

                if not os.path.exists(original_path):
                    base_name = os.path.splitext(file_name)[0]
                    for f in os.listdir(cfg.FILES_DIR):
                        if f.startswith(base_name + "."):
                            original_path = os.path.join(cfg.FILES_DIR, f)
                            break
                    else:
                        bare = os.path.join(cfg.FILES_DIR, base_name)
                        if os.path.exists(bare):
                            original_path = bare

                if os.path.exists(original_path):
                    temp_dir = tempfile.mkdtemp()
                    temp_path = os.path.join(temp_dir, os.path.basename(original_path))
                    shutil.copy2(original_path, temp_path)

                    def open_temp_file(p=temp_path):
                        try:
                            os.startfile(p)
                        except Exception:
                            import subprocess
                            subprocess.Popen(["xdg-open", p])

                    StyledButton(self.question_frame, text=f"📎 {os.path.basename(file_name)}",
                                 command=open_temp_file, width=250).pack(pady=2, anchor="w")
                else:
                    StyledLabel(self.question_frame, text=f"⚠ Файл {file_name} не найден",
                                font=("Noto Sans Condensed", 12)).pack(pady=2, anchor="w")

        answer_frame = StyledFrame(self.question_frame)
        answer_frame.pack(fill="x", pady=10)
        StyledLabel(answer_frame, text="Ваш ответ:").pack(side="left", padx=5)
        self.answer_entry = ctk.CTkEntry(answer_frame, width=200, text_color=cfg.TEXT_COLOR)
        self.answer_entry.pack(side="left", padx=5)
        if number in self.user_answers:
            self.answer_entry.insert(0, self.user_answers[number])

        save_btn = StyledButton(answer_frame, text="Сохранить ответ",
                                command=lambda n=number: self.save_answer(n), width=120)
        save_btn.pack(side="left", padx=10)

        nav_btns_frame = StyledFrame(self.question_frame)
        nav_btns_frame.pack(pady=10)

        if number > 1:
            StyledButton(nav_btns_frame, text="← Предыдущее",
                         command=lambda: self.show_question(number - 1), width=120).pack(side="left", padx=5)
        if number < self.total_questions:
            StyledButton(nav_btns_frame, text="Следующее →",
                         command=lambda: self.show_question(number + 1), width=120).pack(side="left", padx=5)

        self.update_nav_button_style()

    def save_answer(self, number):
        answer = self.answer_entry.get().strip()
        self.user_answers[number] = answer
        self.update_nav_button_style()
        if hasattr(self, 'answer_entry'):
            self.answer_entry.configure(border_color=cfg.SUCCESS_COLOR)

    def update_nav_button_style(self):
        for num, btn in self.nav_buttons.items():
            if num == self.current_q_number:
                btn.configure(fg_color=cfg.BTN_HOVER)
            elif num in self.user_answers and self.user_answers[num] != "":
                btn.configure(fg_color="#5cb85c")
            else:
                btn.configure(fg_color=cfg.BTN_COLOR)

    def update_timer(self):
        if not self.timer_running or self.completed or not self.test_active:
            return
        elapsed = time.time() - self.start_time
        remaining = max(0, self.time_limit - elapsed)
        if remaining <= 0:
            self.timer_label.configure(text="Время вышло!")
            self.finish_exam()
            return
        mins, secs = divmod(int(remaining), 60)
        hours, mins = divmod(mins, 60)
        self.timer_label.configure(text=f"Осталось: {hours:02d}:{mins:02d}:{secs:02d}")
        self.after(1000, self.update_timer)

    def confirm_finish(self):
        if self.test_active and not self.completed:
            if messagebox.askyesno("Досрочное завершение",
                                   "Вы уверены, что хотите завершить тест досрочно?\nНесохранённые ответы будут сохранены."):
                self.finish_exam()
        else:
            self.finish_exam()

    def finish_exam(self):
        if self.completed or not self.test_active:
            return
        self.completed = True
        self.timer_running = False

        if hasattr(self, 'answer_entry'):
            current_answer = self.answer_entry.get().strip()
            if current_answer:
                self.user_answers[self.current_q_number] = current_answer

        correct_count = 0
        details = []
        for i, task in enumerate(self.questions, start=1):
            user_ans = self.user_answers.get(i, "").strip()
            correct_ans = task['answer']
            is_correct = (user_ans == correct_ans)
            if is_correct:
                correct_count += 1
            details.append({
                'number': i,
                'user': user_ans,
                'correct': correct_ans,
                'is_correct': is_correct
            })

        duration = int(time.time() - self.start_time)
        total = len(self.questions)

        # === ГЕЙМИФИКАЦИЯ: награда за экзамен ===
        xp_gain = correct_count * 20
        bytes_gain = correct_count * 10
        level_up, bytes_earned = add_xp(self.user_id, xp_gain, master=self.winfo_toplevel())
        add_bytes(self.user_id, bytes_gain)

        Toast(self.winfo_toplevel(), f"Экзамен завершён! +{xp_gain} XP, +{bytes_gain} байтов", is_success=True)
        if level_up:
            Toast(self.winfo_toplevel(), f"🎉 НОВЫЙ УРОВЕНЬ {level_up}! +{bytes_earned} байтов", is_success=True)
            Confetti(self.winfo_toplevel())

        save_exam_result(self.user_id, correct_count, total, duration, details)

        if self.on_finish_callback:
            self.on_finish_callback(correct_count, total, details, duration)
        else:
            self.show_result_window(correct_count, total, details)
            self.destroy()

    def show_result_window(self, score, total, details):
        """Fallback: отдельное окно результатов (если нет родительского экрана)."""
        messagebox.showinfo("Результат", f"Первичный балл: {score} из {total}")
