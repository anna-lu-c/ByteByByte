# create_test_screen.py
import customtkinter as ctk
from tkinter import messagebox
import app.core.config as cfg
from app.ui.widgets.buttons import StyledButton
from app.ui.widgets.cards import StyledLabel, StyledFrame, CardFrame
from app.core.constants import TASK_NAMES
from app.core.database import create_teacher_test, assign_test_to_students

class CreateTestScreen(ctk.CTkFrame):
    def __init__(self, master, dashboard, class_id, **kwargs):
        super().__init__(master, fg_color=cfg.BG_COLOR, **kwargs)
        self.dashboard = dashboard
        self.class_id = class_id
        self.user_id = dashboard.user_id
        self.task_vars = {}        # {номер: (BooleanVar, StringVar)}

        StyledButton(self, text="← Назад", command=self.go_back, width=100).pack(anchor="nw", padx=20, pady=15)

        scroll = ctk.CTkScrollableFrame(self, fg_color=cfg.BG_COLOR)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        StyledLabel(scroll, text="📝 Создать тест", font=("Noto Sans Condensed", 22, "bold")).pack(pady=10)

        # Название теста
        name_frame = StyledFrame(scroll)
        name_frame.pack(fill="x", pady=5)
        StyledLabel(name_frame, text="Название:").pack(side="left", padx=5)
        self.name_entry = ctk.CTkEntry(name_frame, width=300, text_color=cfg.TEXT_COLOR)
        self.name_entry.pack(side="left", padx=5)

        # Время
        time_frame = StyledFrame(scroll)
        time_frame.pack(fill="x", pady=5)
        StyledLabel(time_frame, text="Время (мин):").pack(side="left", padx=5)
        self.time_entry = ctk.CTkEntry(time_frame, width=80, text_color=cfg.TEXT_COLOR)
        self.time_entry.pack(side="left", padx=5)
        self.time_entry.insert(0, "45")

        # Выбор заданий с количеством
        StyledLabel(scroll, text="Выберите задания и количество:", font=("Noto Sans Condensed", 16, "bold")).pack(anchor="w", pady=10)

        tasks_container = ctk.CTkScrollableFrame(scroll, fg_color=cfg.BG_COLOR, height=300)
        tasks_container.pack(fill="x", pady=5)

        for num in range(1, 28):
            row = StyledFrame(tasks_container)
            row.pack(fill="x", pady=2, padx=5)

            var = ctk.BooleanVar(value=False)
            cb = ctk.CTkCheckBox(row, text=f"№{num}: {TASK_NAMES.get(num, '')[:50]}",
                                 variable=var, text_color=cfg.TEXT_COLOR, fg_color=cfg.BTN_COLOR)
            cb.pack(side="left", padx=5)

            count_var = ctk.StringVar(value="1")
            count_entry = ctk.CTkEntry(row, width=60, textvariable=count_var,
                                       text_color=cfg.TEXT_COLOR, placeholder_text="Кол-во")
            count_entry.pack(side="right", padx=5)
            StyledLabel(row, text="шт.").pack(side="right")

            self.task_vars[num] = (var, count_var)

        # Кнопка создания
        create_btn = StyledButton(scroll, text="Создать тест", command=self.create_test,
                                  width=200, height=45, font=("Noto Sans Condensed", 16, "bold"))
        create_btn.pack(pady=20)

    def go_back(self):
        self.dashboard.restore_center()

    def create_test(self):
        title = self.name_entry.get().strip()
        if not title:
            messagebox.showwarning("Ошибка", "Введите название теста")
            return

        try:
            time_limit = int(self.time_entry.get())
            if time_limit <= 0:
                raise ValueError
        except:
            messagebox.showwarning("Ошибка", "Время должно быть целым положительным числом")
            return

        # Собираем словарь {номер задания: количество}
        selected_tasks = {}
        for num, (var, count_var) in self.task_vars.items():
            if var.get():
                try:
                    cnt = int(count_var.get())
                    if cnt <= 0:
                        raise ValueError
                except ValueError:
                    messagebox.showwarning("Ошибка", f"Количество для задания №{num} должно быть целым положительным числом")
                    return
                selected_tasks[num] = cnt

        if not selected_tasks:
            messagebox.showwarning("Ошибка", "Выберите хотя бы одно задание")
            return

        # Передаём словарь в БД
        test_id = create_teacher_test(self.user_id, self.class_id, title, selected_tasks, time_limit)
        assign_test_to_students(test_id, self.class_id)
        messagebox.showinfo("Готово", f"Тест «{title}» создан и назначен ученикам класса.")
        self.go_back()
