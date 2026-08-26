# theory_screen.py
import customtkinter as ctk
import app.core.config as cfg
from app.ui.widgets.buttons import StyledButton
from app.ui.widgets.cards import StyledLabel
from app.repositories.theory_repository import TheoryLoader
from app.core.constants import TASK_NAMES


class TheoryScreen(ctk.CTkFrame):
    def __init__(self, master, dashboard, **kwargs):
        super().__init__(master, fg_color=cfg.BG_COLOR, **kwargs)
        self.dashboard = dashboard

        StyledButton(self, text="← Назад", command=self.dashboard.restore_center,
                     width=100).pack(anchor="nw", padx=20, pady=15)

        StyledLabel(self, text="📘 Учебник по информатике", font=("Noto Sans Condensed", 26, "bold")).pack(pady=15)

        # Две вкладки
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=cfg.BG_COLOR,
            segmented_button_fg_color=cfg.COLORS[cfg.current_theme]["secondary"],
            segmented_button_selected_color=cfg.BTN_COLOR,
            segmented_button_unselected_color=cfg.COLORS[cfg.current_theme]["muted"],
            segmented_button_unselected_hover_color=cfg.COLORS[cfg.current_theme]["muted"],
            text_color=cfg.TEXT_COLOR,
            corner_radius=16
        )
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        self.tab_general = self.tabview.add("📘 Общая теория")
        self.tab_tasks = self.tabview.add("📝 По заданиям")

        self.setup_general_tab()
        self.setup_tasks_tab()

    # ---------- Общая теория: один скроллируемый текст ----------
    def setup_general_tab(self):
        frame = ctk.CTkScrollableFrame(self.tab_general, fg_color=cfg.BG_COLOR)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        general = TheoryLoader.load_general()
        sections = general.get("sections", [])
        if sections:
            content = sections[0].get("content", "Общая теория пока не добавлена.")
        else:
            content = "Общая теория пока не добавлена."

        textbox = ctk.CTkTextbox(frame, wrap="word", font=("Noto Sans Condensed", 14),
                                 fg_color=cfg.BG_COLOR, text_color=cfg.TEXT_COLOR)
        textbox.pack(fill="both", expand=True)
        textbox.insert("0.0", content)
        textbox.configure(state="disabled")

    # ---------- По заданиям: слева номера, справа теория ----------
    def setup_tasks_tab(self):
        main_frame = ctk.CTkFrame(self.tab_tasks, fg_color=cfg.BG_COLOR)
        main_frame.pack(fill="both", expand=True)

        # Левая панель с номерами заданий
        self.task_list_frame = ctk.CTkScrollableFrame(main_frame, width=80,
                                                      fg_color=cfg.COLORS[cfg.current_theme]["secondary"])
        self.task_list_frame.pack(side="left", fill="y", padx=(0, 10))

        # Заполняем номера 1–27
        for num in range(1, 28):
            btn = ctk.CTkButton(self.task_list_frame, text=str(num), width=50, height=30,
                                corner_radius=8,
                                fg_color=cfg.BTN_COLOR, hover_color=cfg.COLORS[cfg.current_theme]["muted"],
                                text_color=cfg.TEXT_COLOR, font=("Noto Sans Condensed", 12, "bold"),
                                command=lambda n=num: self.show_task_theory(n))
            btn.pack(pady=2, padx=5)

        # Правая панель с текстом теории
        self.task_content_frame = ctk.CTkScrollableFrame(main_frame, fg_color=cfg.BG_COLOR)
        self.task_content_frame.pack(side="right", fill="both", expand=True)

        # Показать теорию первого задания по умолчанию
        self.show_task_theory(1)

    def show_task_theory(self, num):
        for w in self.task_content_frame.winfo_children():
            w.destroy()

        theory = TheoryLoader.load_task_theory(num)
        title = theory.get("title", TASK_NAMES.get(num, f"Задание {num}"))
        content = theory.get("content", "Теория для этого задания пока не добавлена.")

        StyledLabel(self.task_content_frame, text=f"Задание №{num}: {title}",
                    font=("Noto Sans Condensed", 20, "bold")).pack(anchor="w", pady=10)
        textbox = ctk.CTkTextbox(self.task_content_frame, wrap="word", font=("Noto Sans Condensed", 14),
                                 fg_color=cfg.BG_COLOR, text_color=cfg.TEXT_COLOR)
        textbox.pack(fill="both", expand=True)
        textbox.insert("0.0", content)
        textbox.configure(state="disabled")
