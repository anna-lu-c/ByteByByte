# combined_game_screen.py
import customtkinter as ctk
from tkinter import messagebox
import app.core.config as cfg
from app.ui.widgets.buttons import StyledButton
from app.ui.widgets.cards import StyledLabel, StyledFrame
from app.core.database import load_progress
from app.core.constants import SUBTYPES_BY_TASK, TASK_NAMES
from app.repositories.task_repository import TaskLoader
from app.services.game_service import add_xp, add_bytes
from app.utils.toast import Toast
from app.utils.confetti import Confetti
import os
from PIL import Image

class CombinedGameFrame(ctk.CTkFrame):
    """
    Фрейм для тренировки по заданиям 19–21 (теория игр).
    Отображает блоки (каждый блок объединяет задания 19, 20, 21) слева,
    а справа — условия и поля для ответов трёх заданий выбранного блока.
    """
    def __init__(self, master, start_task_num, update_progress_callback, user_id, go_back_callback):
        super().__init__(master, fg_color=cfg.BG_COLOR)
        self.master = master
        self.start_task_num = start_task_num
        self.update_progress_callback = update_progress_callback
        self.user_id = user_id
        self.go_back_callback = go_back_callback

        self.subtypes = SUBTYPES_BY_TASK.get(19, ["Одна куча", "Две кучи"])
        self.current_subtype = None
        self.blocks = []
        self.total_blocks = 0
        self.block_status = {}
        self.left_frame = None
        self.right_frame = None
        self.block_buttons = {}
        self.answer_entries = {}
        self.current_block_index = -1

        header = StyledLabel(self, text="Задания 19–21: Теория игр",
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
        theory_text = (
            "ТЕОРИЯ ДЛЯ ЗАДАНИЙ 19–21: ТЕОРИЯ ИГР\n\n"
            "О чём задания:\n"
            "• Задание 19: определение выигрышной стратегии для одного хода.\n"
            "• Задание 20: определение выигрышной стратегии для двух ходов.\n"
            "• Задание 21: определение выигрышной стратегии для произвольного количества ходов.\n\n"
            "Основные понятия:\n"
            "• Выигрышные и проигрышные позиции.\n"
            "• Дерево игры.\n"
            "• Анализ с конца.\n\n"
            "Пример решения:\n"
            "..."
        )
        textbox = ctk.CTkTextbox(frame, wrap="word", font=("Noto Sans Condensed", 14),
                                 fg_color=cfg.BG_COLOR, text_color=cfg.TEXT_COLOR)
        textbox.pack(fill="both", expand=True)
        textbox.insert("0.0", theory_text)
        textbox.configure(state="disabled")

    def setup_practice_tab(self):
        control_frame = StyledFrame(self.tab_practice)
        control_frame.pack(fill="x", padx=10, pady=10)

        StyledLabel(control_frame, text="Подтип заданий:", font=("Noto Sans Condensed", 14, "bold")).pack(side="left", padx=5)

        self.subtype_var = ctk.StringVar(value=self.subtypes[0] if self.subtypes else "")
        self.subtype_menu = ctk.CTkOptionMenu(control_frame, values=self.subtypes,
                                              variable=self.subtype_var, width=300,
                                              fg_color=cfg.BTN_COLOR, button_color=cfg.BTN_HOVER,
                                              text_color=cfg.TEXT_COLOR,
                                              command=self.on_subtype_changed)
        self.subtype_menu.pack(side="left", padx=10)

        self.practice_area = StyledFrame(self.tab_practice)
        self.practice_area.pack(fill="both", expand=True, padx=10, pady=10)
        self.practice_area.pack_forget()

        self.after(100, self.on_subtype_changed, self.subtype_var.get())

    def on_subtype_changed(self, chosen_subtype):
        self.start_practice()

    def start_practice(self):
        self.current_subtype = self.subtype_var.get()
        tasks_19 = TaskLoader.get_tasks(19, self.current_subtype)
        tasks_20 = TaskLoader.get_tasks(20, self.current_subtype)
        tasks_21 = TaskLoader.get_tasks(21, self.current_subtype)
        if not tasks_19:
            messagebox.showerror("Ошибка", f"Нет задач для подтипа «{self.current_subtype}»")
            return

        self.blocks = []
        for i in range(len(tasks_19)):
            block = {
                "19": tasks_19[i],
                "20": tasks_20[i] if i < len(tasks_20) else None,
                "21": tasks_21[i] if i < len(tasks_21) else None
            }
            self.blocks.append(block)
        self.total_blocks = len(self.blocks)
        self.block_status = {i: {"19": False, "20": False, "21": False} for i in range(self.total_blocks)}
        self.block_buttons = {}
        self.answer_entries = {}

        self.practice_area.pack(fill="both", expand=True, padx=10, pady=10)
        self.build_block_interface()

    def build_block_interface(self):
        for widget in self.practice_area.winfo_children():
            widget.destroy()

        content = StyledFrame(self.practice_area)
        content.pack(fill="both", expand=True)

        self.left_frame = ctk.CTkScrollableFrame(content, width=150, fg_color=cfg.COLORS[cfg.current_theme]["muted"])
        self.left_frame.pack(side="left", fill="y", padx=(0, 10))
        StyledLabel(self.left_frame, text="Блоки", font=("Noto Sans Condensed", 14, "bold")).pack(pady=5)

        for i in range(self.total_blocks):
            btn = ctk.CTkButton(
                self.left_frame,
                text=f"Блок {i+1}",
                width=120,
                height=35,
                corner_radius=8,
                fg_color=cfg.BTN_COLOR,
                hover_color=cfg.BTN_HOVER,
                text_color=cfg.TEXT_COLOR,
                font=("Noto Sans Condensed", 12, "bold"),
                command=lambda idx=i: self.display_block(idx)
            )
            btn.pack(pady=3, padx=10)
            self.block_buttons[i] = btn

        self.right_frame = ctk.CTkScrollableFrame(content, fg_color=cfg.BG_COLOR)
        self.right_frame.pack(side="right", fill="both", expand=True)

        if self.total_blocks > 0:
            self.display_block(0)

    def display_block(self, block_index):
        self.current_block_index = block_index
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        if block_index >= len(self.blocks):
            return
        block = self.blocks[block_index]

        StyledLabel(self.right_frame,
                    text=f"Блок {block_index+1} из {self.total_blocks}",
                    font=("Noto Sans Condensed", 14, "bold")).pack(pady=(5, 10))

        for num in ("19", "20", "21"):
            task = block[num]
            if not task:
                continue
            task_frame = StyledFrame(self.right_frame)
            task_frame.pack(fill="x", pady=5, padx=5)

            StyledLabel(task_frame, text=f"Задание {num}",
                        font=("Noto Sans Condensed", 14, "bold")).pack(anchor="w")

            if "image" in task and task["image"]:
                img_path = os.path.join(cfg.IMAGES_DIR, task["image"])
                if os.path.exists(img_path):
                    try:
                        pil_img = Image.open(img_path)
                        max_w = 400
                        if pil_img.width > max_w:
                            ratio = max_w / pil_img.width
                            pil_img = pil_img.resize((max_w, int(pil_img.height * ratio)),
                                                     Image.Resampling.LANCZOS)
                        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img,
                                               size=pil_img.size)
                        img_lbl = ctk.CTkLabel(task_frame, image=ctk_img, text="")
                        img_lbl.image = ctk_img
                        img_lbl.pack(anchor="w", pady=5)
                    except Exception as e:
                        StyledLabel(task_frame, text=f"⚠ Ошибка загрузки изображения: {e}",
                                    font=("Noto Sans Condensed", 12)).pack(anchor="w")

            StyledLabel(task_frame, text=task['question'],
                        font=("Noto Sans Condensed", 13), wraplength=600, justify="left").pack(anchor="w", pady=5)

            if "file" in task and task["file"]:
                file_path = os.path.join(cfg.FILES_DIR, task["file"])
                if os.path.exists(file_path):
                    def open_file(p=file_path):
                        try:
                            os.startfile(p)
                        except:
                            import subprocess
                            subprocess.Popen(["xdg-open", p])
                    StyledButton(task_frame, text="📎 Открыть файл", command=open_file, width=150).pack(anchor="w", pady=2)
                else:
                    StyledLabel(task_frame, text="⚠ Файл не найден", font=("Noto Sans Condensed", 12)).pack(anchor="w")

            entry = ctk.CTkEntry(task_frame, placeholder_text="Ваш ответ", width=250,
                                 text_color=cfg.TEXT_COLOR)
            entry.pack(anchor="w", pady=5)
            if num not in self.answer_entries:
                self.answer_entries[num] = {}
            self.answer_entries[num][block_index] = entry

        btn_frame = StyledFrame(self.right_frame)
        btn_frame.pack(fill="x", pady=10)

        check_btn = StyledButton(btn_frame, text="✅ Проверить блок",
                                 command=lambda: self.check_block(block_index), width=150)
        check_btn.pack(side="left", padx=10)

        hint_btn = StyledButton(btn_frame, text="💡 Показать решения",
                                command=lambda: self.show_block_solutions(block_index), width=150)
        hint_btn.pack(side="left", padx=10)

        self.feedback_label = StyledLabel(self.right_frame, text="")
        self.feedback_label.pack(anchor="w", pady=5)

        self.highlight_block_button(block_index)

    def highlight_block_button(self, active_index):
        for idx, btn in self.block_buttons.items():
            if idx == active_index:
                btn.configure(fg_color=cfg.BTN_HOVER)
            else:
                status = self.block_status[idx]
                all_correct = all(status.values())
                if all_correct:
                    btn.configure(fg_color=cfg.SUCCESS_COLOR)
                else:
                    any_correct = any(status.values())
                    if any_correct:
                        btn.configure(fg_color=cfg.PARTIAL_COLOR)
                    else:
                        btn.configure(fg_color=cfg.BTN_COLOR)

    def check_block(self, block_index):
        block = self.blocks[block_index]
        old_status = dict(self.block_status[block_index])
        new_status = {"19": False, "20": False, "21": False}
        all_correct_now = True

        for num in ("19", "20", "21"):
            if num not in block or not block[num]:
                continue
            entry = self.answer_entries[num][block_index]
            user_ans = entry.get().strip()
            correct_ans = block[num]['answer']
            if user_ans == correct_ans:
                new_status[num] = True
            else:
                all_correct_now = False

        self.block_status[block_index] = new_status

        for num in ("19", "20", "21"):
            if num not in block or not block[num]:
                continue
            old_correct = old_status.get(num, False)
            new_correct = new_status[num]
            if old_correct != new_correct:
                delta = (1.0 / self.total_blocks) if new_correct else (-1.0 / self.total_blocks)
                self.update_progress_callback(int(num), delta)

        was_fully_solved = all(old_status.values())
        if all_correct_now and not was_fully_solved:
            xp_gain = 30
            bytes_gain = 15
            level_up, bytes_earned = add_xp(self.user_id, xp_gain, master=self.winfo_toplevel())
            add_bytes(self.user_id, bytes_gain)
            Toast(self.winfo_toplevel(), f"+{xp_gain} XP, +{bytes_gain} байтов!", is_success=True)
            if level_up:
                Toast(self.winfo_toplevel(), f"🎉 УРОВЕНЬ {level_up}! +{bytes_earned} байтов", is_success=True)
                Confetti(self.winfo_toplevel())

        self.highlight_block_button(block_index)

        if all_correct_now:
            self.feedback_label.configure(text="✅ Блок решён верно!", text_color=cfg.SUCCESS_COLOR)
        else:
            self.feedback_label.configure(text="❌ Есть ошибки. Проверьте ответы.", text_color=cfg.ERROR_COLOR)

    def show_block_solutions(self, block_index):
        block = self.blocks[block_index]
        solutions = []
        for num in ("19", "20", "21"):
            task = block.get(num)
            if task:
                hint = task.get('hint', 'Решение не добавлено.')
                solutions.append(f"Задание {num}:\n{hint}")
        messagebox.showinfo("Решения", "\n\n".join(solutions))

    def setup_analytics_tab(self):
        self.analytics_frame = ctk.CTkScrollableFrame(self.tab_analytics, fg_color=cfg.BG_COLOR)
        self.analytics_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.update_analytics_display()

    def update_analytics_display(self):
        for widget in self.analytics_frame.winfo_children():
            widget.destroy()

        progress = load_progress(self.user_id)

        frame19 = StyledFrame(self.analytics_frame)
        frame19.pack(fill="x", pady=5)
        StyledLabel(frame19, text="Задание 19:", width=100).pack(side="left")
        bar19 = ctk.CTkProgressBar(frame19, width=200, progress_color=cfg.BTN_COLOR)
        bar19.pack(side="left", padx=5)
        val19 = progress.get(19, 0.0)
        bar19.set(val19)
        StyledLabel(frame19, text=f"{int(val19*100)}%").pack(side="left")

        frame20 = StyledFrame(self.analytics_frame)
        frame20.pack(fill="x", pady=5)
        StyledLabel(frame20, text="Задание 20:", width=100).pack(side="left")
        bar20 = ctk.CTkProgressBar(frame20, width=200, progress_color=cfg.BTN_COLOR)
        bar20.pack(side="left", padx=5)
        val20 = progress.get(20, 0.0)
        bar20.set(val20)
        StyledLabel(frame20, text=f"{int(val20*100)}%").pack(side="left")

        frame21 = StyledFrame(self.analytics_frame)
        frame21.pack(fill="x", pady=5)
        StyledLabel(frame21, text="Задание 21:", width=100).pack(side="left")
        bar21 = ctk.CTkProgressBar(frame21, width=200, progress_color=cfg.BTN_COLOR)
        bar21.pack(side="left", padx=5)
        val21 = progress.get(21, 0.0)
        bar21.set(val21)
        StyledLabel(frame21, text=f"{int(val21*100)}%").pack(side="left")

        StyledLabel(self.analytics_frame, text="Освоение подтипов:",
                    font=("Noto Sans Condensed", 14, "bold")).pack(anchor="w", pady=(15, 5))

        for st in self.subtypes:
            blocks_st = TaskLoader.get_tasks(19, st)
            total_blocks = len(blocks_st) if blocks_st else 1
            progress_19 = progress.get(19, 0.0)
            progress_20 = progress.get(20, 0.0)
            progress_21 = progress.get(21, 0.0)
            min_progress = min(progress_19, progress_20, progress_21)
            solved_blocks = int(round(min_progress * total_blocks))

            ratio = solved_blocks / total_blocks if total_blocks else 0
            if ratio == 1.0:
                color = cfg.SUCCESS_COLOR
                status = "освоен"
            elif ratio > 0:
                color = cfg.PARTIAL_COLOR
                status = f"частично ({solved_blocks}/{total_blocks} блоков)"
            else:
                color = cfg.ERROR_COLOR
                status = f"не решено (0/{total_blocks} блоков)"

            row = StyledFrame(self.analytics_frame)
            row.pack(fill="x", pady=2)
            StyledLabel(row, text=st, width=200, anchor="w").pack(side="left")
            StyledLabel(row, text=status, text_color=color).pack(side="left", padx=10)
