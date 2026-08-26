# student_panel.py
import customtkinter as ctk
from tkinter import messagebox
import json
import app.core.config as cfg
from app.ui.widgets.buttons import StyledButton
from app.ui.widgets.cards import StyledLabel, StyledFrame, CardFrame
from app.core.database import (
    get_user_class, join_class, get_class_members,
    get_student_tests, get_student_completed_tests
)


class StudentPanel(ctk.CTkFrame):
    def __init__(self, master, dashboard):
        super().__init__(master, fg_color=cfg.BG_COLOR)
        self.dashboard = dashboard
        self.user_id = dashboard.user_id

        user_class = get_user_class(self.user_id)
        if user_class:
            class_id, class_name, teacher_id = user_class
            self.display_class_info(class_id, class_name)
        else:
            self.show_join_interface()

    def show_join_interface(self):
        StyledLabel(self, text="🔑 Присоединиться к классу",
                    font=("Noto Sans Condensed", 22, "bold")).pack(pady=15)

        card = CardFrame(self)
        card.pack(padx=40, pady=20, fill="both", expand=True)

        StyledLabel(card, text="Введите код приглашения, полученный от учителя:",
                    font=("Noto Sans Condensed", 14)).pack(pady=10)

        entry_frame = StyledFrame(card)
        entry_frame.pack(pady=10)
        self.code_entry = ctk.CTkEntry(entry_frame, placeholder_text="Код приглашения", width=200,
                                       text_color=cfg.TEXT_COLOR)
        self.code_entry.pack(side="left", padx=5)
        StyledButton(entry_frame, text="Войти", command=self.join_class).pack(side="left")

        self.status_label = StyledLabel(card, text="")
        self.status_label.pack()

    def join_class(self):
        code = self.code_entry.get().strip()
        if not code:
            self.status_label.configure(text="Введите код")
            return
        ok, msg = join_class(self.user_id, code)
        self.status_label.configure(text=msg)
        if ok:
            self.dashboard.restore_center()

    def display_class_info(self, class_id, class_name):
        main_scroll = ctk.CTkScrollableFrame(self, fg_color=cfg.BG_COLOR)
        main_scroll.pack(fill="both", expand=True, padx=10, pady=(0,10))

        StyledLabel(main_scroll, text=f"🏫 Класс: {class_name}",
                    font=("Noto Sans Condensed", 24, "bold")).pack(pady=15)

        members = get_class_members(class_id)
        StyledLabel(main_scroll, text=f"👥 Ученики ({len(members)})",
                    font=("Noto Sans Condensed", 16, "bold")).pack(anchor="w", padx=20, pady=(5,2))

        if members:
            members_frame = StyledFrame(main_scroll)
            members_frame.pack(fill="x", padx=20, pady=5)
            header = StyledFrame(members_frame)
            header.pack(fill="x")
            StyledLabel(header, text="Ученик", width=200).pack(side="left")
            StyledLabel(header, text="Уровень", width=100).pack(side="left")
            StyledLabel(header, text="XP", width=100).pack(side="left")
            for m in members:
                row = StyledFrame(members_frame)
                row.pack(fill="x", pady=1)
                StyledLabel(row, text=f"{m[2]} {m[3]}", width=200).pack(side="left")
                StyledLabel(row, text=str(m[4]), width=100).pack(side="left")
                StyledLabel(row, text=str(m[5]), width=100).pack(side="left")
        else:
            StyledLabel(main_scroll, text="Пока нет учеников.", font=("Noto Sans Condensed", 12)).pack(anchor="w", padx=20)

        # --- Активные тесты ---
        StyledLabel(main_scroll, text="📝 Активные тесты", font=("Noto Sans Condensed", 18, "bold")).pack(anchor="w", padx=20, pady=(15,5))
        active_tests = get_student_tests(self.user_id)
        if not active_tests:
            StyledLabel(main_scroll, text="Нет активных тестов.", font=("Noto Sans Condensed", 14)).pack(anchor="w", padx=20)
        else:
            for t in active_tests:
                assign_id, title, tasks_json, time_lim, finished, score = t
                tasks = json.loads(tasks_json)
                if isinstance(tasks, list):
                    tasks = {num: 1 for num in tasks}
                total_questions = sum(tasks.values())
                card = CardFrame(main_scroll)
                card.pack(fill="x", padx=20, pady=5)
                StyledLabel(card, text=f"Тест: {title}", font=("Noto Sans Condensed", 16, "bold")).pack(anchor="w", padx=10, pady=2)
                StyledLabel(card, text=f"Заданий: {total_questions} | Время: {time_lim} мин",
                            font=("Noto Sans Condensed", 12)).pack(anchor="w", padx=10)
                StyledButton(card, text="Начать тест",
                             command=lambda aid=assign_id, ttl=title, tsk=tasks, tl=time_lim:
                                 self.start_test(aid, ttl, tsk, tl),
                             width=150).pack(padx=10, pady=5)

        # --- Завершённые тесты ---
        StyledLabel(main_scroll, text="✅ Завершённые тесты", font=("Noto Sans Condensed", 18, "bold")).pack(anchor="w", padx=20, pady=(15,5))
        completed_tests = get_student_completed_tests(self.user_id)
        if not completed_tests:
            StyledLabel(main_scroll, text="Нет завершённых тестов.", font=("Noto Sans Condensed", 14)).pack(anchor="w", padx=20)
        else:
            for ct in completed_tests:
                assign_id, title, tasks_json, score, finished_at = ct
                tasks = json.loads(tasks_json)
                if isinstance(tasks, list):
                    tasks = {num: 1 for num in tasks}
                total = sum(tasks.values())
                card = CardFrame(main_scroll)
                card.pack(fill="x", padx=20, pady=5)
                StyledLabel(card, text=f"Тест: {title}", font=("Noto Sans Condensed", 14, "bold")).pack(anchor="w", padx=10, pady=2)
                StyledLabel(card, text=f"Результат: {score} из {total} | Завершён: {finished_at[:10] if finished_at else ''}",
                            font=("Noto Sans Condensed", 12)).pack(anchor="w", padx=10)

        StyledButton(main_scroll, text="📖 Сюжетная новелла (от учителя)",
                     command=lambda: self.show_novella_stub(class_id)).pack(pady=10)

    def start_test(self, assignment_id, title, tasks_dict, time_limit):
        from app.ui.screens.student.take_test_screen import TakeTestScreen
        self.dashboard.master.show_screen(TakeTestScreen,
                                          dashboard=self.dashboard,
                                          assignment_id=assignment_id,
                                          test_title=title,
                                          tasks_dict=tasks_dict,
                                          time_limit=time_limit)

    def show_novella_stub(self, class_id):
        from app.ui.screens.student.student_novella_screen import NovelScreen
        self.dashboard.master.show_screen(NovelScreen, dashboard=self.dashboard, class_id=class_id)
