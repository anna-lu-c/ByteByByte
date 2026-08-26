# training_screen.py
import customtkinter as ctk
from tkinter import messagebox
import app.core.config as cfg
from app.ui.widgets.buttons import StyledButton
from app.ui.widgets.cards import StyledLabel, StyledFrame, CardFrame
from app.core.database import load_progress, save_progress, get_user_gamification
from app.core.constants import TASK_NAMES, TOTAL_TASKS

class TrainingScreen(ctk.CTkFrame):
    def __init__(self, master, user_id, username, first_name, last_name, class_name, **kwargs):
        super().__init__(master, fg_color=cfg.BG_COLOR, **kwargs)
        self.master = master
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.class_name = class_name
        self.loaded_progress = load_progress(user_id)
        self.gamification = get_user_gamification(user_id)
        self.section_widgets = {}
        self.main_ui_elements = []

        self.setup_ui()
        self.show_sections_grid()

    def setup_ui(self):
        top_panel = StyledFrame(self)
        top_panel.pack(fill="x", padx=20, pady=(10, 5))
        self._create_stats_panel(top_panel)

        self.title_label = StyledLabel(
            self,
            text="Тренировочный модуль\nИзучайте теорию и практику по каждому заданию ЕГЭ",
            font=("Noto Sans Condensed", 20, "bold"),
            justify="center"
        )
        self.title_label.pack(pady=10)
        self.main_ui_elements.append(self.title_label)

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
        self.main_ui_elements.append(self.tabview)

        self.tab_sections = self.tabview.add("📚 Разделы")
        self.tab_analytics = self.tabview.add("📊 Аналитика")

        self.sections_container = StyledFrame(self.tab_sections)
        self.sections_container.pack(fill="both", expand=True)

        self.setup_analytics_tab()

        self.source_frame = ctk.CTkFrame(self, fg_color=cfg.COLORS[cfg.current_theme]["secondary"], height=30)
        self.source_frame.pack(side="bottom", fill="x", padx=10, pady=5)
        self.main_ui_elements.append(self.source_frame)
        source_label = StyledLabel(
            self.source_frame,
            text="📚 Задания взяты с образовательного портала «Решу ЕГЭ» по информатике",
            font=("Noto Sans Condensed", 12, "italic"),
            text_color=cfg.COLORS[cfg.current_theme]["muted_fg"]
        )
        source_label.pack(pady=3)

        self.hint_label = StyledLabel(
            self,
            text="Выберите раздел и начните тренировку. За правильные ответы вы получаете XP и байты!",
            font=("Noto Sans Condensed", 12, "italic")
        )
        self.hint_label.pack(pady=(0, 10))
        self.main_ui_elements.append(self.hint_label)

        self.back_btn = StyledButton(
            self,
            text="← Назад в главное меню",
            command=self.go_back,
            width=200
        )
        self.back_btn.pack(pady=10)
        self.main_ui_elements.append(self.back_btn)

        self.section_view_container = None

    def _create_stats_panel(self, parent):
        stats_frame = CardFrame(parent)
        stats_frame.pack(fill="x", pady=5)

        self.level_label = StyledLabel(stats_frame, text=f"Уровень: {self.gamification['level']}",
                                       font=("Noto Sans Condensed", 14, "bold"))
        self.level_label.pack(side="left", padx=15, pady=5)

        self.xp_label = StyledLabel(stats_frame, text=f"XP: {self.gamification['xp']} / {self.gamification['level'] * 100}",
                                    font=("Noto Sans Condensed", 14))
        self.xp_label.pack(side="left", padx=15, pady=5)

        self.bytes_label = StyledLabel(stats_frame, text=f"💰 {self.gamification['bytes']} байтов",
                                       font=("Noto Sans Condensed", 14))
        self.bytes_label.pack(side="left", padx=15, pady=5)

    def update_stats_display(self):
        self.gamification = get_user_gamification(self.user_id)
        self.level_label.configure(text=f"Уровень: {self.gamification['level']}")
        self.xp_label.configure(text=f"XP: {self.gamification['xp']} / {self.gamification['level'] * 100}")
        self.bytes_label.configure(text=f"💰 {self.gamification['bytes']} байтов")

    def _hide_main_ui(self):
        for widget in self.main_ui_elements:
            widget.pack_forget()

    def _show_main_ui(self):
        self.title_label.pack(pady=10)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.source_frame.pack(side="bottom", fill="x", padx=10, pady=5)
        self.hint_label.pack(pady=(0, 10))
        self.back_btn.pack(pady=10)
        self.update_stats_display()

    def _close_section(self):
        if self.section_view_container:
            self.section_view_container.destroy()
            self.section_view_container = None
        self._show_main_ui()
        self.show_sections_grid()

    def show_sections_grid(self):
        for widget in self.sections_container.winfo_children():
            widget.destroy()

        scroll_frame = ctk.CTkScrollableFrame(self.sections_container, fg_color=cfg.BG_COLOR)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        for task_num in range(1, TOTAL_TASKS + 1):
            self.create_task_tile(scroll_frame, task_num)

    def create_task_tile(self, parent, task_num):
        tile = ctk.CTkFrame(
            parent,
            width=180,
            height=150,
            corner_radius=16,
            fg_color=cfg.TILE_BG,
            border_width=2,
            border_color=cfg.TILE_BORDER
        )
        tile.pack_propagate(False)

        def on_enter(e):
            tile.configure(fg_color=cfg.TILE_HOVER, border_color=cfg.BTN_COLOR)
        def on_leave(e):
            tile.configure(fg_color=cfg.TILE_BG, border_color=cfg.TILE_BORDER)

        tile.bind("<Enter>", on_enter)
        tile.bind("<Leave>", on_leave)

        progress_value = self.loaded_progress.get(task_num, 0.0)
        progress_bar = ctk.CTkProgressBar(tile, width=140, height=8, corner_radius=4,
                                          progress_color=cfg.BTN_COLOR)
        progress_bar.pack(pady=(10, 5))
        progress_bar.set(progress_value)

        num_label = StyledLabel(
            tile,
            text=f"№{task_num}",
            font=("Noto Sans Condensed", 16, "bold")
        )
        num_label.pack(pady=(5, 2))

        name_label = StyledLabel(
            tile,
            text=TASK_NAMES.get(task_num, f"Задание {task_num}"),
            font=("Noto Sans Condensed", 11),
            wraplength=160
        )
        name_label.pack(pady=(0, 5))

        percent_label = StyledLabel(
            tile,
            text=f"{int(progress_value * 100)}%",
            font=("Noto Sans Condensed", 10),
            text_color=cfg.COLORS[cfg.current_theme]["muted_fg"]
        )
        percent_label.pack(pady=(0, 10))

        self.section_widgets[task_num] = {
            "progress_value": progress_value,
            "tile": tile,
            "progress_bar": progress_bar,
            "percent_label": percent_label
        }

        tile.bind("<Button-1>", lambda e, n=task_num: self.open_section(n))
        num_label.bind("<Button-1>", lambda e, n=task_num: self.open_section(n))
        name_label.bind("<Button-1>", lambda e, n=task_num: self.open_section(n))

        row = (task_num - 1) // 5
        col = (task_num - 1) % 5
        tile.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)
        parent.grid_rowconfigure(row, weight=1)

    def setup_analytics_tab(self):
        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            self.has_matplotlib = True
        except ImportError:
            self.has_matplotlib = False

        scroll = ctk.CTkScrollableFrame(self.tab_analytics, fg_color=cfg.BG_COLOR)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        if not self.has_matplotlib:
            StyledLabel(
                scroll,
                text="Для отображения радарной диаграммы установите matplotlib:\npip install matplotlib",
                font=("Noto Sans Condensed", 14)
            ).pack(pady=20)
        else:
            self.create_radar_chart(scroll)

        problem_frame = StyledFrame(scroll)
        problem_frame.pack(fill="x", pady=10)
        StyledLabel(
            problem_frame,
            text="Проблемные разделы (прогресс < 60%):",
            font=("Noto Sans Condensed", 14, "bold")
        ).pack(anchor="w", padx=10, pady=5)

        problem_text = ""
        for num in range(1, TOTAL_TASKS + 1):
            val = self.loaded_progress.get(num, 0.0)
            if val < 0.6:
                problem_text += f"• Задание {num}: {int(val*100)}%\n"
        if not problem_text:
            problem_text = "Отлично! Все разделы освоены более чем на 60%."

        problem_label = StyledLabel(scroll, text=problem_text, justify="left")
        problem_label.pack(anchor="w", padx=20, pady=5)

        detail_btn = StyledButton(
            scroll,
            text="Подробная аналитика",
            command=self.show_detailed_analytics,
            width=200
        )
        detail_btn.pack(pady=15)

    def create_radar_chart(self, parent):
        try:
            import numpy as np
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        except ImportError:
            StyledLabel(parent, text="Установите numpy и matplotlib для диаграммы", font=("Noto Sans Condensed", 12)).pack()
            return

        values = [self.loaded_progress.get(i, 0.0) * 10 for i in range(1, TOTAL_TASKS + 1)]
        angles = np.linspace(0, 2 * np.pi, TOTAL_TASKS, endpoint=False).tolist()
        values += values[:1]
        angles += angles[:1]

        fig = Figure(figsize=(6, 6), dpi=100)
        ax = fig.add_subplot(111, polar=True)
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels([str(i) for i in range(1, TOTAL_TASKS + 1)], fontsize=8)
        ax.set_ylim(0, 10)
        ax.set_yticks([2, 4, 6, 8, 10])
        ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'])
        ax.plot(angles, values, linewidth=2, linestyle='solid', color=cfg.BTN_COLOR)
        ax.fill(angles, values, alpha=0.25, color=cfg.BTN_COLOR)
        ax.set_title("Прогресс по заданиям (0–100%)", pad=20, fontdict={'fontsize': 12, 'fontweight': 'bold'})

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)

    def show_detailed_analytics(self):
        messagebox.showinfo("Детальная аналитика", "Здесь будет более подробный отчёт по каждому разделу.")

    def update_section_progress(self, task_num, delta):
        widgets = self.section_widgets.get(task_num)
        if not widgets:
            return
        new_value = min(widgets["progress_value"] + delta, 1.0)
        widgets["progress_value"] = new_value
        widgets["progress_bar"].set(new_value)
        widgets["percent_label"].configure(text=f"{int(new_value*100)}%")
        save_progress(self.user_id, task_num, new_value)
        self.loaded_progress[task_num] = new_value

    def go_back(self):
        from app.ui.screens.dashboard.dashboard_screen import DashboardScreen
        self.master.show_screen(DashboardScreen,
                                user_id=self.user_id,
                                username=self.username,
                                first_name=self.first_name,
                                last_name=self.last_name,
                                class_name=self.class_name)

    def open_section(self, task_num):
        self._close_section()
        self._hide_main_ui()
        self.section_view_container = ctk.CTkFrame(self, fg_color=cfg.BG_COLOR)
        self.section_view_container.pack(fill="both", expand=True)

        def update_progress(task, delta):
            self.update_section_progress(task, delta)

        if task_num in (19, 20, 21):
            from app.ui.screens.training.combined_game_screen import CombinedGameFrame
            section = CombinedGameFrame(
                self.section_view_container,
                task_num,
                update_progress,
                self.user_id,
                go_back_callback=self._close_section
            )
        else:
            from app.ui.screens.training.section_screen import SectionFrame
            section = SectionFrame(
                self.section_view_container,
                task_num,
                update_progress,
                self.user_id,
                go_back_callback=self._close_section
            )
        section.pack(fill="both", expand=True)
