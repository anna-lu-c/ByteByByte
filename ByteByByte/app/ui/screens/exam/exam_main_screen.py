# exam_main_screen.py
import customtkinter as ctk
import json
import app.core.config as cfg
from app.ui.widgets.buttons import StyledButton
from app.ui.widgets.cards import StyledLabel, StyledFrame, CardFrame
from app.core.database import load_exam_history, get_user_gamification
from app.core.constants import TOTAL_TASKS

class ExamMainScreen(ctk.CTkFrame):
    """Основной экран подготовительного модуля: приветствие, кнопка запуска, аналитика с геймификацией."""

    def __init__(self, master, user_id, username, first_name, last_name, class_name, **kwargs):
        super().__init__(master, fg_color=cfg.BG_COLOR, **kwargs)
        self.master = master
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.class_name = class_name

        self.gamification = get_user_gamification(user_id)
        self.level = self.gamification["level"]
        self.xp = self.gamification["xp"]
        self.bytes_amt = self.gamification["bytes"]

        self.setup_ui()
        self.show_welcome_message()

    def setup_ui(self):
        top_panel = StyledFrame(self)
        top_panel.pack(fill="x", padx=20, pady=(10, 5))
        self._create_stats_panel(top_panel)

        self.tabview = ctk.CTkTabview(
            self,
            fg_color=cfg.BG_COLOR,
            segmented_button_fg_color=cfg.COLORS[cfg.current_theme]["secondary"],
            segmented_button_selected_color=cfg.BTN_COLOR,
            segmented_button_unselected_color=cfg.COLORS[cfg.current_theme]["muted"],
            segmented_button_unselected_hover_color=cfg.BTN_HOVER,
            text_color=cfg.TEXT_COLOR,
            corner_radius=16
        )
        self.tabview.pack(fill="both", expand=True, padx=15, pady=(5, 10))

        self.tab_test = self.tabview.add("📝 Тестирование")
        self.tab_analytics = self.tabview.add("📊 Аналитика")

        self.main_frame = StyledFrame(self.tab_test)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.setup_analytics_tab()

        self.back_btn = StyledButton(self, text="← Назад в главное меню", command=self.go_back, width=200)
        self.back_btn.pack(pady=10)

    def _create_stats_panel(self, parent):
        stats_frame = CardFrame(parent)
        stats_frame.pack(fill="x", pady=5)

        self.level_label = StyledLabel(stats_frame, text=f"Уровень: {self.level}", font=("Noto Sans Condensed", 14, "bold"))
        self.level_label.pack(side="left", padx=15, pady=5)

        self.xp_label = StyledLabel(stats_frame, text=f"XP: {self.xp} / {self.level * 100}", font=("Noto Sans Condensed", 14))
        self.xp_label.pack(side="left", padx=15, pady=5)

        self.bytes_label = StyledLabel(stats_frame, text=f"💰 {self.bytes_amt} байтов", font=("Noto Sans Condensed", 14))
        self.bytes_label.pack(side="left", padx=15, pady=5)

    def update_stats_display(self):
        self.gamification = get_user_gamification(self.user_id)
        self.level = self.gamification["level"]
        self.xp = self.gamification["xp"]
        self.bytes_amt = self.gamification["bytes"]
        self.level_label.configure(text=f"Уровень: {self.level}")
        self.xp_label.configure(text=f"XP: {self.xp} / {self.level * 100}")
        self.bytes_label.configure(text=f"💰 {self.bytes_amt} байтов")

    def show_welcome_message(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        scroll = ctk.CTkScrollableFrame(self.main_frame, fg_color=cfg.BG_COLOR)
        scroll.pack(fill="both", expand=True)

        StyledLabel(scroll, text="📋 Структура ЕГЭ по информатике",
                    font=("Noto Sans Condensed", 18, "bold")).pack(anchor="w", pady=(10, 5))
        StyledLabel(scroll, text="• 27 заданий\n• Продолжительность: 235 минут",
                    font=("Noto Sans Condensed", 14)).pack(anchor="w", padx=20)

        self.transfer_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.transfer_frame.pack(fill="x", pady=10)

        self.show_transfer_btn = StyledButton(
            self.transfer_frame, text="📊 Показать таблицу перевода баллов",
            command=self.toggle_transfer_table, width=280
        )
        self.show_transfer_btn.pack(anchor="w", padx=20)

        self.transfer_table_frame = StyledFrame(scroll)
        self.transfer_table_frame.pack_forget()

        StyledLabel(scroll, text="📌 Правила симуляции",
                    font=("Noto Sans Condensed", 18, "bold")).pack(anchor="w", pady=(15, 5))
        rules = ("• Можно пропускать задания и возвращаться к ним позже\n"
                 "• Ответы сохраняются автоматически\n"
                 "• Таймер запускается после нажатия «Начать тестирование»\n"
                 "• По истечении времени тест завершится автоматически")
        StyledLabel(scroll, text=rules, font=("Noto Sans Condensed", 14), justify="left").pack(anchor="w", padx=20)

        start_btn = StyledButton(scroll, text="▶ Начать тестирование", command=self.start_exam,
                                 width=220, height=45, font=("Noto Sans Condensed", 16, "bold"))
        start_btn.pack(pady=25)

        StyledLabel(scroll, text="✨ Удачи! Всё получится! ✨",
                    font=("Noto Sans Condensed", 14, "italic")).pack(pady=20)

    def toggle_transfer_table(self):
        if self.transfer_table_frame.winfo_ismapped():
            self.transfer_table_frame.pack_forget()
            self.show_transfer_btn.configure(text="📊 Показать таблицу перевода баллов")
        else:
            for w in self.transfer_table_frame.winfo_children():
                w.destroy()
            StyledLabel(self.transfer_table_frame, text="Таблица перевода (первичный → тестовый)",
                        font=("Noto Sans Condensed", 14, "bold")).pack(pady=5)
            text = ("29 → 100\n28 → 98\n27 → 95\n26 → 92\n25 → 88\n24 → 85\n23 → 82\n"
                    "22 → 78\n21 → 75\n20 → 72\n19 → 68\n18 → 65\n17 → 62\n16 → 58\n"
                    "15 → 55\n14 → 52\n13 → 48\n12 → 45\n11 → 42\n10 → 38\n9 → 35\n"
                    "8 → 32\n7 → 28\n6 → 25\n5 → 22\n4 → 18\n3 → 15\n2 → 12\n1 → 8\n0 → 0")
            StyledLabel(self.transfer_table_frame, text=text, font=("Noto Sans Condensed", 12)).pack()
            self.transfer_table_frame.pack(fill="x", pady=5, padx=20)
            self.show_transfer_btn.configure(text="📊 Скрыть таблицу перевода баллов")

    def start_exam(self):
        self.back_btn.pack_forget()
        self.tabview.pack_forget()
        self.main_frame.pack_forget()

        from app.ui.screens.exam.exam_test_screen import ExamTestScreen
        self.test_screen = ExamTestScreen(
            self,
            user_id=self.user_id,
            username=self.username,
            first_name=self.first_name,
            last_name=self.last_name,
            class_name=self.class_name,
            on_finish_callback=self.on_test_finished
        )
        self.test_screen.pack(fill="both", expand=True)

    def on_test_finished(self, score, total, details, duration):
        self.test_screen.destroy()
        self.update_stats_display()

        self.back_btn.pack(pady=10)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=(5, 10))
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.show_welcome_message()
        self.tabview.set("📊 Аналитика")
        self.refresh_analytics_tab()

    def setup_analytics_tab(self):
        self.analytics_frame = ctk.CTkScrollableFrame(self.tab_analytics, fg_color=cfg.BG_COLOR)
        self.analytics_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.refresh_analytics_tab()

    def refresh_analytics_tab(self):
        for widget in self.analytics_frame.winfo_children():
            widget.destroy()

        history = load_exam_history(self.user_id)
        if not history:
            StyledLabel(self.analytics_frame, text="История попыток пуста. Пройдите хотя бы одну симуляцию.",
                        font=("Noto Sans Condensed", 14)).pack(pady=20)
            return

        title = StyledLabel(self.analytics_frame, text="История симуляций", font=("Noto Sans Condensed", 20, "bold"))
        title.pack(pady=10)

        table_container = StyledFrame(self.analytics_frame)
        table_container.pack(fill="x", padx=10, pady=5)

        headers = ["Дата", "Баллы", "Время", "Процент"]
        widths = [200, 100, 120, 100]
        header_frame = StyledFrame(table_container)
        header_frame.pack(fill="x", pady=2)
        for h, w in zip(headers, widths):
            StyledLabel(header_frame, text=h, width=w, font=("Noto Sans Condensed", 14, "bold")).pack(side="left", padx=2)

        for record in history:
            row_frame = StyledFrame(table_container)
            row_frame.pack(fill="x", pady=1)

            date_str = record[1].split('.')[0] if '.' in record[1] else record[1]
            StyledLabel(row_frame, text=date_str, width=widths[0]).pack(side="left", padx=2)

            score_text = f"{record[2]} / {record[3]}"
            StyledLabel(row_frame, text=score_text, width=widths[1]).pack(side="left", padx=2)

            duration = record[4]
            if duration < 3600:
                time_str = f"{duration // 60:02d}:{duration % 60:02d}"
            else:
                h = duration // 3600
                m = (duration % 3600) // 60
                s = duration % 60
                time_str = f"{h:02d}:{m:02d}:{s:02d}"
            StyledLabel(row_frame, text=time_str, width=widths[2]).pack(side="left", padx=2)

            percent = (record[2] / record[3]) * 100 if record[3] > 0 else 0
            percent_text = f"{percent:.1f}%"
            StyledLabel(row_frame, text=percent_text, width=widths[3]).pack(side="left", padx=2)

        try:
            self.create_radar_chart(history)
        except ImportError:
            StyledLabel(self.analytics_frame, text="Для диаграммы установите matplotlib и numpy",
                        font=("Noto Sans Condensed", 12)).pack(pady=5)

        avg_primary = sum(r[2] for r in history) / len(history)
        test_score = self.primary_to_test(avg_primary)
        StyledLabel(self.analytics_frame,
                    text=f"Средний балл: {avg_primary:.1f} первичных / {test_score} тестовых",
                    font=("Noto Sans Condensed", 14, "bold")).pack(pady=5)

        problem_frame = StyledFrame(self.analytics_frame)
        problem_frame.pack(fill="x", pady=10)
        StyledLabel(problem_frame, text="Самые проблемные задания (низкий средний балл):",
                    font=("Noto Sans Condensed", 14, "bold")).pack(anchor="w", padx=5)

        task_scores = {i: [] for i in range(1, TOTAL_TASKS + 1)}
        for record in history:
            details = json.loads(record[5]) if record[5] else []
            for d in details:
                task_scores[d['number']].append(1 if d['is_correct'] else 0)

        avg_by_task = []
        for num in range(1, TOTAL_TASKS + 1):
            scores = task_scores[num]
            avg = sum(scores) / len(scores) if scores else 0
            avg_by_task.append((num, avg))

        worst = sorted(avg_by_task, key=lambda x: x[1])[:5]
        problem_text = "\n".join([f"• Задание {num}: {avg:.1%}" for num, avg in worst])
        StyledLabel(problem_frame, text=problem_text, justify="left").pack(anchor="w", padx=20, pady=5)

        detail_btn = StyledButton(
            self.analytics_frame,
            text="Подробный отчёт (последняя попытка)",
            command=lambda: self.show_detailed_report(history[0])
        )
        detail_btn.pack(pady=15)

    def primary_to_test(self, primary):
        table = {29: 100, 28: 98, 27: 95, 26: 92, 25: 88, 24: 85, 23: 82,
                 22: 78, 21: 75, 20: 72, 19: 68, 18: 65, 17: 62, 16: 58,
                 15: 55, 14: 52, 13: 48, 12: 45, 11: 42, 10: 38, 9: 35,
                 8: 32, 7: 28, 6: 25, 5: 22, 4: 18, 3: 15, 2: 12, 1: 8, 0: 0}
        p = int(round(primary))
        return table.get(p, p * 3)

    def create_radar_chart(self, history):
        try:
            import numpy as np
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        except ImportError:
            return

        task_scores = {i: [] for i in range(1, TOTAL_TASKS + 1)}
        for record in history:
            details = json.loads(record[5]) if record[5] else []
            for d in details:
                task_scores[d['number']].append(1 if d['is_correct'] else 0)

        values = []
        for i in range(1, TOTAL_TASKS + 1):
            scores = task_scores[i]
            avg = sum(scores) / len(scores) if scores else 0
            values.append(avg * 10)

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
        ax.set_title("Средний процент правильных ответов по заданиям", pad=20)

        canvas = FigureCanvasTkAgg(fig, master=self.analytics_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)

    def show_detailed_report(self, record):
        details = json.loads(record[5]) if record[5] else []
        score = record[2]
        total = record[3]
        duration = record[4]

        report_window = ctk.CTkToplevel(self)
        report_window.configure(fg_color=cfg.BG_COLOR)
        report_window.title(f"Детальный отчёт от {record[1]}")
        report_window.geometry("800x600")
        report_window.grab_set()

        title = StyledLabel(report_window, text=f"Результаты от {record[1]}",
                            font=("Noto Sans Condensed", 20, "bold"))
        title.pack(pady=10)

        info = f"Баллы: {score} из {total} | Время: {duration//60:02d}:{duration%60:02d}"
        StyledLabel(report_window, text=info, font=("Noto Sans Condensed", 14)).pack()

        table_frame = ctk.CTkScrollableFrame(report_window, width=700, height=300, fg_color=cfg.BG_COLOR)
        table_frame.pack(pady=10, padx=10, fill="both", expand=True)

        header_frame = StyledFrame(table_frame)
        header_frame.pack(fill="x", pady=2)
        StyledLabel(header_frame, text="№", width=50, font=("Noto Sans Condensed", 14, "bold")).pack(side="left", padx=5)
        StyledLabel(header_frame, text="Ваш ответ", width=150, font=("Noto Sans Condensed", 14, "bold")).pack(side="left", padx=5)
        StyledLabel(header_frame, text="Верный ответ", width=150, font=("Noto Sans Condensed", 14, "bold")).pack(side="left", padx=5)
        StyledLabel(header_frame, text="Результат", width=100, font=("Noto Sans Condensed", 14, "bold")).pack(side="left", padx=5)

        for d in details:
            row = StyledFrame(table_frame)
            row.pack(fill="x", pady=1)
            StyledLabel(row, text=str(d['number']), width=50).pack(side="left", padx=5)
            StyledLabel(row, text=d['user'], width=150).pack(side="left", padx=5)
            StyledLabel(row, text=d['correct'], width=150).pack(side="left", padx=5)
            result_text = "✅ Верно" if d['is_correct'] else "❌ Ошибка"
            color = cfg.SUCCESS_COLOR if d['is_correct'] else cfg.ERROR_COLOR
            StyledLabel(row, text=result_text, width=100, text_color=color).pack(side="left", padx=5)

        close_btn = StyledButton(report_window, text="Закрыть", command=report_window.destroy, width=150)
        close_btn.pack(pady=10)

    def go_back(self):
        from app.ui.screens.dashboard.dashboard_screen import DashboardScreen
        self.master.show_screen(DashboardScreen,
                                user_id=self.user_id,
                                username=self.username,
                                first_name=self.first_name,
                                last_name=self.last_name,
                                class_name=self.class_name)
