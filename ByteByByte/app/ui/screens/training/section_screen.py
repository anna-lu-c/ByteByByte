# section_screen.py
import customtkinter as ctk
from tkinter import messagebox
import app.core.config as cfg
from app.ui.widgets.buttons import StyledButton
from app.ui.widgets.cards import StyledLabel, StyledFrame
from app.core.database import load_progress
from app.core.constants import SUBTYPES_BY_TASK, TASK_NAMES
from app.repositories.task_repository import TaskLoader
from app.repositories.theory_repository import TheoryLoader
from app.services.game_service import add_xp, add_bytes
from app.utils.toast import Toast
from app.utils.confetti import Confetti
import os
from PIL import Image
import tempfile
import shutil

class SectionFrame(ctk.CTkFrame):
    def __init__(self, master, task_number, update_progress_callback, user_id, go_back_callback):
        super().__init__(master, fg_color=cfg.BG_COLOR)
        self.master = master
        self.task_number = task_number
        self.update_progress_callback = update_progress_callback
        self.user_id = user_id
        self.go_back_callback = go_back_callback

        self.subtypes = SUBTYPES_BY_TASK.get(task_number, ["Задания для подготовки"])
        section_name = TASK_NAMES.get(task_number, f"Задание {task_number}")

        self.subtype_task_counts = {}
        total = 0
        for st in self.subtypes:
            tasks = TaskLoader.get_tasks(task_number, st)
            cnt = len(tasks)
            self.subtype_task_counts[st] = cnt
            total += cnt
        self.total_tasks_in_section = total

        self.current_subtype = None
        self.tasks = []
        self.subtype_progress = {}
        self.solved_status = {}
        self.task_buttons = {}

        header = StyledLabel(self, text=f"Задание №{task_number}: {section_name}",
                             font=("Noto Sans Condensed", 22, "bold"))
        header.pack(pady=15)

        self.tabview = ctk.CTkTabview(
            self,
            fg_color=cfg.BG_COLOR,
            segmented_button_fg_color=cfg.BTN_COLOR,
            segmented_button_selected_color=cfg.BTN_HOVER,
            segmented_button_unselected_color=cfg.BTN_COLOR,
            segmented_button_unselected_hover_color=cfg.BTN_HOVER,
            text_color=cfg.TEXT_COLOR
        )
        self.tabview.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.tab_theory = self.tabview.add("📘 Теория")
        self.tab_practice = self.tabview.add("📝 Практика")
        self.tab_analytics = self.tabview.add("📊 Аналитика")

        self.setup_theory_tab()
        self.setup_practice_tab()
        self.setup_analytics_tab()

        back_btn = StyledButton(self, text="← Назад к разделам", command=self.go_back, width=180)
        back_btn.pack(pady=10)

    def go_back(self):
        self.go_back_callback()

    def setup_theory_tab(self):
        frame = ctk.CTkScrollableFrame(self.tab_theory, fg_color=cfg.BG_COLOR)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        theory_data = TheoryLoader.load_task_theory(self.task_number)
        title = theory_data.get("title", TASK_NAMES.get(self.task_number, f"Задание {self.task_number}"))
        content = theory_data.get("content", "Теория для этого задания пока не добавлена.")

        textbox = ctk.CTkTextbox(frame, wrap="word", font=("Noto Sans Condensed", 14),
                                 fg_color=cfg.BG_COLOR, text_color=cfg.TEXT_COLOR)
        textbox.pack(fill="both", expand=True)
        textbox.insert("0.0", f"{title}\n\n{content}")
        textbox.configure(state="disabled")

    def setup_practice_tab(self):
        control_frame = StyledFrame(self.tab_practice)
        control_frame.pack(fill="x", padx=10, pady=10)

        StyledLabel(control_frame, text="Подтип задания:",
                    font=("Noto Sans Condensed", 14, "bold")).pack(side="left", padx=5)

        self.subtype_var = ctk.StringVar(value=self.subtypes[0] if self.subtypes else "")
        self.subtype_menu = ctk.CTkOptionMenu(
            control_frame, values=self.subtypes,
            variable=self.subtype_var, width=300,
            fg_color=cfg.BTN_COLOR, button_color=cfg.BTN_HOVER,
            text_color=cfg.TEXT_COLOR,
            command=self.on_subtype_changed
        )
        self.subtype_menu.pack(side="left", padx=10)

        self.tasks_container = StyledFrame(self.tab_practice)
        self.tasks_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.show_task_list()

    def on_subtype_changed(self, value):
        self.show_task_list()

    def show_task_list(self):
        self.current_subtype = self.subtype_var.get()
        self.tasks = TaskLoader.get_tasks(self.task_number, self.current_subtype)
        self.solved_status = {i: False for i in range(len(self.tasks))}
        self.task_buttons = {}

        for widget in self.tasks_container.winfo_children():
            widget.destroy()

        content_area = StyledFrame(self.tasks_container)
        content_area.pack(fill="both", expand=True, padx=5, pady=5)

        left_frame = ctk.CTkScrollableFrame(content_area, width=130,
                                            fg_color=cfg.COLORS[cfg.current_theme]["muted"])
        left_frame.pack(side="left", fill="y", padx=(0, 5))

        StyledLabel(left_frame, text="Задачи",
                    font=("Noto Sans Condensed", 14, "bold")).pack(pady=5, anchor="center")

        for i in range(len(self.tasks)):
            btn = ctk.CTkButton(
                left_frame, text=str(i+1), width=100, height=35, corner_radius=8,
                fg_color=cfg.BTN_COLOR, hover_color=cfg.BTN_HOVER, text_color=cfg.TEXT_COLOR,
                font=("Noto Sans Condensed", 14, "bold"),
                command=lambda idx=i: self.display_task_detail(idx)
            )
            btn.pack(pady=2, padx=10)
            self.task_buttons[i] = btn

        self.detail_frame = ctk.CTkScrollableFrame(content_area, fg_color=cfg.BG_COLOR)
        self.detail_frame.pack(side="right", fill="both", expand=True)

        if self.tasks:
            self.display_task_detail(0)

    def display_task_detail(self, task_index):
        for widget in self.detail_frame.winfo_children():
            widget.destroy()

        if task_index >= len(self.tasks):
            return

        self.current_task_index = task_index
        task = self.tasks[task_index]

        StyledLabel(self.detail_frame,
                    text=f"Задача {task_index+1} из {len(self.tasks)}",
                    font=("Noto Sans Condensed", 14, "bold")).pack(pady=(5, 10), anchor="w")

        if "image" in task and task["image"]:
            img_path = os.path.join(cfg.IMAGES_DIR, task["image"])
            if os.path.exists(img_path):
                try:
                    pil_img = Image.open(img_path)
                    w, h = pil_img.size
                    max_w = 500
                    if w > max_w:
                        ratio = max_w / w
                        new_size = (max_w, int(h * ratio))
                        pil_img = pil_img.resize(new_size, Image.Resampling.LANCZOS)
                    ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img,
                                           size=pil_img.size)
                    img_label = ctk.CTkLabel(self.detail_frame, image=ctk_img, text="")
                    img_label.image = ctk_img
                    img_label.pack(pady=5, anchor="w")
                except Exception as e:
                    StyledLabel(self.detail_frame,
                                text=f"⚠ Ошибка загрузки изображения: {e}",
                                font=("Noto Sans Condensed", 12)).pack(pady=5, anchor="w")

        StyledLabel(self.detail_frame, text=task['question'],
                    font=("Noto Sans Condensed", 14), wraplength=700, justify="left").pack(pady=10, anchor="w")

        if "file" in task and task["file"]:
            file_names = [f.strip() for f in task["file"].split(",") if f.strip()]
            for file_name in file_names:
                original_path = os.path.join(cfg.FILES_DIR, file_name)
                real_path = original_path
                if not os.path.exists(original_path):
                    base_name = os.path.splitext(file_name)[0]
                    for f in os.listdir(cfg.FILES_DIR):
                        if f.startswith(base_name + "."):
                            real_path = os.path.join(cfg.FILES_DIR, f)
                            break
                    else:
                        bare = os.path.join(cfg.FILES_DIR, base_name)
                        if os.path.exists(bare):
                            real_path = bare
                if os.path.exists(real_path):
                    temp_dir = tempfile.mkdtemp()
                    temp_path = os.path.join(temp_dir, os.path.basename(real_path))
                    shutil.copy2(real_path, temp_path)
                    def open_temp_file(p=temp_path):
                        try:
                            os.startfile(p)
                        except:
                            import subprocess
                            subprocess.Popen(["xdg-open", p])
                    StyledButton(self.detail_frame, text=f"📎 {os.path.basename(file_name)}",
                                 command=open_temp_file, width=250).pack(pady=2, anchor="w")
                else:
                    StyledLabel(self.detail_frame,
                                text=f"⚠ Файл {file_name} не найден",
                                font=("Noto Sans Condensed", 12)).pack(pady=2, anchor="w")

        self.answer_entry = ctk.CTkEntry(self.detail_frame, placeholder_text="Ваш ответ",
                                         width=300, text_color=cfg.TEXT_COLOR)
        self.answer_entry.pack(pady=10, anchor="w")

        btn_frame = StyledFrame(self.detail_frame)
        btn_frame.pack(pady=10, anchor="w")

        check_btn = StyledButton(btn_frame, text="✅ Проверить",
                                 command=lambda idx=task_index: self.check_answer(idx), width=120)
        check_btn.pack(side="left", padx=10)

        sol_btn = StyledButton(btn_frame, text="💡 Показать решение",
                               command=lambda idx=task_index: self.show_solution(idx),
                               width=150)
        sol_btn.pack(side="left", padx=10)

        self.feedback_label = StyledLabel(self.detail_frame, text="")
        self.feedback_label.pack(pady=5, anchor="w")

        self.highlight_task_button(task_index)

    def highlight_task_button(self, index):
        for i, btn in self.task_buttons.items():
            if i == index:
                btn.configure(fg_color=cfg.BTN_HOVER)
            else:
                if self.solved_status.get(i, False):
                    btn.configure(fg_color=cfg.SUCCESS_COLOR)
                else:
                    btn.configure(fg_color=cfg.BTN_COLOR)

    def check_answer(self, task_index):
        task = self.tasks[task_index]
        user_answer = self.answer_entry.get().strip()
        correct = task['answer']

        was_solved = self.solved_status.get(task_index, False)
        is_correct = (user_answer == correct)

        if is_correct:
            if not was_solved:
                xp_gain = 10
                bytes_gain = 5
                level_up, bytes_earned = add_xp(self.user_id, xp_gain, master=self.winfo_toplevel())
                add_bytes(self.user_id, bytes_gain)
                Toast(self.winfo_toplevel(), f"Правильно! +{xp_gain} XP, +{bytes_gain} байтов", is_success=True)
                if level_up:
                    Toast(self.winfo_toplevel(), f"🎉 УРОВЕНЬ {level_up}! +{bytes_earned} байтов", is_success=True)
                    Confetti(self.winfo_toplevel())

                self.solved_status[task_index] = True
                self.subtype_progress[self.current_subtype] = self.subtype_progress.get(self.current_subtype, 0) + 1
                self.update_task_button(task_index, True)
                delta = 1 / self.total_tasks_in_section if self.total_tasks_in_section > 0 else 0
                self.update_progress_callback(self.task_number, delta)
            self.feedback_label.configure(text="✅ Верно! Отлично!", text_color=cfg.SUCCESS_COLOR)
        else:
            if was_solved:
                self.solved_status[task_index] = False
                self.subtype_progress[self.current_subtype] = max(0, self.subtype_progress.get(self.current_subtype, 0) - 1)
                self.update_task_button(task_index, False)
                delta = -1 / self.total_tasks_in_section if self.total_tasks_in_section > 0 else 0
                self.update_progress_callback(self.task_number, delta)
            else:
                self.update_task_button(task_index, False)
            self.feedback_label.configure(text="❌ Неверно. Попробуйте ещё раз.", text_color=cfg.ERROR_COLOR)

    def update_task_button(self, task_index, is_correct):
        if task_index in self.task_buttons:
            btn = self.task_buttons[task_index]
            btn.configure(fg_color=cfg.SUCCESS_COLOR if is_correct else cfg.ERROR_COLOR)

    def show_solution(self, task_index):
        if task_index < len(self.tasks):
            hint = self.tasks[task_index].get('hint', 'Решение пока не добавлено.')
            messagebox.showinfo("Решение", hint)

    def setup_analytics_tab(self):
        self.analytics_frame = ctk.CTkScrollableFrame(self.tab_analytics, fg_color=cfg.BG_COLOR)
        self.analytics_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.update_analytics_display()

    def update_analytics_display(self):
        for widget in self.analytics_frame.winfo_children():
            widget.destroy()

        current_progress = load_progress(self.user_id).get(self.task_number, 0.0)

        progress_frame = StyledFrame(self.analytics_frame)
        progress_frame.pack(fill="x", pady=10)
        StyledLabel(progress_frame, text="Общий прогресс раздела:",
                    font=("Noto Sans Condensed", 14, "bold")).pack(side="left", padx=5)
        progress_bar = ctk.CTkProgressBar(progress_frame, width=300, progress_color=cfg.BTN_COLOR)
        progress_bar.pack(side="left", padx=5)
        progress_bar.set(current_progress)
        percent_label = StyledLabel(progress_frame, text=f"{int(current_progress*100)}%")
        percent_label.pack(side="left", padx=5)

        subtypes_frame = StyledFrame(self.analytics_frame)
        subtypes_frame.pack(fill="x", pady=10)
        StyledLabel(subtypes_frame, text="Освоение подтипов:",
                    font=("Noto Sans Condensed", 14, "bold")).pack(anchor="w", pady=5)

        for st in self.subtypes:
            solved = self.subtype_progress.get(st, 0)
            total_st = self.subtype_task_counts.get(st, 5)
            ratio = solved / total_st if total_st > 0 else 0
            if ratio == 1.0:
                color = cfg.SUCCESS_COLOR
                status = "освоен"
            elif ratio > 0:
                color = cfg.PARTIAL_COLOR
                status = f"частично ({solved}/{total_st})"
            else:
                color = cfg.ERROR_COLOR
                status = f"не решено (0/{total_st})"

            row = StyledFrame(subtypes_frame)
            row.pack(fill="x", pady=2)
            StyledLabel(row, text=st, width=250, anchor="w").pack(side="left")
            status_label = StyledLabel(row, text=status, text_color=color)
            status_label.pack(side="left", padx=10)
