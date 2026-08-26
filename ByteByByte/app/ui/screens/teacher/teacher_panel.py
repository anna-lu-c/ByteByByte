# teacher_panel.py
import customtkinter as ctk
from tkinter import messagebox
import json
import app.core.config as cfg
from app.ui.widgets.buttons import StyledButton
from app.ui.widgets.cards import StyledLabel, StyledFrame, CardFrame
from app.core.database import (
    get_teacher_classes, create_class, get_class_members,
    get_class_tests, get_test_assignments, delete_teacher_test
)


class TeacherPanel(ctk.CTkFrame):
    def __init__(self, master, dashboard):
        super().__init__(master, fg_color=cfg.BG_COLOR)
        self.dashboard = dashboard
        self.user_id = dashboard.user_id
        self.setup_ui()

    def setup_ui(self):
        StyledLabel(self, text="🎓 Мои классы", font=("Noto Sans Condensed", 26, "bold")).pack(pady=15)

        create_frame = StyledFrame(self)
        create_frame.pack(fill="x", padx=20, pady=10)
        self.new_class_name = ctk.CTkEntry(create_frame, placeholder_text="Название класса", width=200,
                                           text_color=cfg.TEXT_COLOR)
        self.new_class_name.pack(side="left", padx=5)
        StyledButton(create_frame, text="Создать класс", command=self.create_teacher_class).pack(side="left", padx=5)

        classes = get_teacher_classes(self.user_id)

        total_students = 0
        for cls in classes:
            members = get_class_members(cls[0])
            total_students += len(members)

        if total_students > 0:
            StyledLabel(self, text=f"👥 Всего учеников в ваших классах: {total_students}",
                        font=("Noto Sans Condensed", 14)).pack(pady=5)

        if not classes:
            StyledLabel(self, text="У вас пока нет классов.", font=("Noto Sans Condensed", 14)).pack(pady=20)
            return

        scroll = ctk.CTkScrollableFrame(self, fg_color=cfg.BG_COLOR)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        for cls in classes:
            card = CardFrame(scroll)
            card.pack(fill="x", pady=10)

            StyledLabel(card, text=f"Класс: {cls[1]}", font=("Noto Sans Condensed", 18, "bold")).pack(anchor="w", padx=10, pady=5)
            StyledLabel(card, text=f"Код приглашения: {cls[2]}", font=("Noto Sans Condensed", 14)).pack(anchor="w", padx=10)

            btn_frame = StyledFrame(card)
            btn_frame.pack(fill="x", padx=10, pady=5)
            StyledButton(btn_frame, text="👥 Ученики",
                         command=lambda cid=cls[0]: self.show_class_students(cid)).pack(side="left", padx=5)
            StyledButton(btn_frame, text="📝 Создать тест",
                         command=lambda cid=cls[0]: self.open_create_test(cid)).pack(side="left", padx=5)
            StyledButton(btn_frame, text="📊 Результаты",
                         command=lambda cid=cls[0]: self.show_test_results(cid)).pack(side="left", padx=5)
            StyledButton(btn_frame, text="📖 Создать новеллу",
                         command=lambda cid=cls[0]: self.create_novella_stub(cid)).pack(side="left", padx=5)

    def create_teacher_class(self):
        name = self.new_class_name.get().strip()
        if not name:
            messagebox.showwarning("Ошибка", "Введите название класса")
            return
        class_id, code = create_class(self.user_id, name)
        messagebox.showinfo("Класс создан", f"Класс «{name}» создан.\nКод приглашения: {code}")
        self.dashboard.restore_center()

    def show_class_students(self, class_id):
        members = get_class_members(class_id)
        if not members:
            messagebox.showinfo("Ученики", "В этом классе ещё нет учеников.")
            return
        top = ctk.CTkToplevel(self)
        top.title("Список учеников")
        top.geometry("500x400")
        top.grab_set()
        scroll = ctk.CTkScrollableFrame(top, fg_color=cfg.BG_COLOR)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        for m in members:
            row = StyledFrame(scroll)
            row.pack(fill="x", pady=2)
            StyledLabel(row, text=f"{m[2]} {m[3]} (ур.{m[4]}, XP: {m[5]})",
                        font=("Noto Sans Condensed", 14)).pack(anchor="w")

    def open_create_test(self, class_id):
        from app.ui.screens.teacher.create_test_screen import CreateTestScreen
        self.dashboard.master.show_screen(CreateTestScreen, dashboard=self.dashboard, class_id=class_id)

    def show_test_results(self, class_id):
        tests = get_class_tests(class_id)
        if not tests:
            messagebox.showinfo("Результаты", "Нет созданных тестов.")
            return
        top = ctk.CTkToplevel(self)
        top.title("Результаты тестов")
        top.geometry("700x550")
        top.grab_set()
        scroll = ctk.CTkScrollableFrame(top, fg_color=cfg.BG_COLOR)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        StyledLabel(scroll, text="Выберите тест для просмотра результатов или удаления",
                    font=("Noto Sans Condensed", 16, "bold")).pack(pady=5)
        for test in tests:
            test_id, title, tasks, time_lim = test
            tasks_parsed = json.loads(tasks)
            if isinstance(tasks_parsed, list):
                tasks_parsed = {num: 1 for num in tasks_parsed}
            total_q = sum(tasks_parsed.values())
            frame = CardFrame(scroll)
            frame.pack(fill="x", pady=5)
            StyledLabel(frame, text=f"{title} (Заданий: {total_q}, Время: {time_lim} мин)",
                        font=("Noto Sans Condensed", 14, "bold")).pack(anchor="w", padx=10, pady=2)
            btn_row = StyledFrame(frame)
            btn_row.pack(fill="x", padx=10, pady=5)
            StyledButton(btn_row, text="Просмотр результатов",
                         command=lambda tid=test_id: self.show_test_detail(tid)).pack(side="left", padx=5)
            StyledButton(btn_row, text="Удалить тест", fg_color="#d9534f",
                         command=lambda tid=test_id: self.confirm_delete_test(tid, top)).pack(side="left", padx=5)

    def confirm_delete_test(self, test_id, parent_window):
        if messagebox.askyesno("Удаление теста", "Вы действительно хотите удалить тест и все его результаты?"):
            delete_teacher_test(test_id)
            parent_window.destroy()
            messagebox.showinfo("Удалено", "Тест удалён.")
            self.dashboard.restore_center()

    def show_test_detail(self, test_id):
        assignments = get_test_assignments(test_id)
        top = ctk.CTkToplevel(self)
        top.title("Результаты теста")
        top.geometry("500x400")
        top.grab_set()
        scroll = ctk.CTkScrollableFrame(top, fg_color=cfg.BG_COLOR)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        for a in assignments:
            assign_id, fname, lname, score, finished = a
            status = "Завершён" if finished else "Не начат"
            StyledLabel(scroll, text=f"{fname} {lname}: {score} баллов, {status}",
                        font=("Noto Sans Condensed", 14)).pack(anchor="w", pady=2)

    def create_novella_stub(self, class_id):
        messagebox.showinfo("В разработке",
                            "Редактор новеллы пока недоступен.\nВы можете добавить главы вручную через БД.")
