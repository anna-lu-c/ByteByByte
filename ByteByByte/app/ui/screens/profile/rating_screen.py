# rating_screen.py
import customtkinter as ctk
from app.ui.widgets.buttons import StyledButton
from app.ui.widgets.cards import StyledLabel, StyledFrame
from app.core.database import get_all_users


class RatingScreen(ctk.CTkFrame):
    def __init__(self, master, dashboard, **kwargs):
        super().__init__(master, fg_color="#f0f0f0")
        self.dashboard = dashboard

        StyledButton(self, text="← Назад", command=self.dashboard.restore_center,
                     width=100).pack(anchor="nw", padx=20, pady=15)

        StyledLabel(self, text="🏆 Рейтинг участников",
                    font=("Noto Sans Condensed", 26, "bold")).pack(pady=15)

        # Скроллируемая таблица
        table_frame = ctk.CTkScrollableFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Заголовки
        header = StyledFrame(table_frame)
        header.pack(fill="x", pady=5)
        StyledLabel(header, text="Место", width=60, font=("Noto Sans Condensed", 13, "bold")).pack(side="left", padx=5)
        StyledLabel(header, text="Имя", width=200, font=("Noto Sans Condensed", 13, "bold")).pack(side="left", padx=5)
        StyledLabel(header, text="Уровень", width=80, font=("Noto Sans Condensed", 13, "bold")).pack(side="left", padx=5)
        StyledLabel(header, text="XP", width=100, font=("Noto Sans Condensed", 13, "bold")).pack(side="left", padx=5)
        StyledLabel(header, text="Байты", width=100, font=("Noto Sans Condensed", 13, "bold")).pack(side="left", padx=5)

        # Получаем всех пользователей, сортируем по XP (или level, bytes)
        users = get_all_users()
        # Сортируем по убыванию XP, потом по уровню
        sorted_users = sorted(users, key=lambda u: (u[9], u[7]), reverse=True)  # индексы: 7=level, 9=xp

        for i, u in enumerate(sorted_users, start=1):
            uid, uname, fname, lname, cls, role, blocked, lvl, xp, bytes_val, house = u
            if blocked:  # пропускаем заблокированных (по желанию)
                continue
            row = StyledFrame(table_frame)
            row.pack(fill="x", pady=2)
            StyledLabel(row, text=str(i), width=60).pack(side="left", padx=5)
            display_name = f"{fname} {lname}"
            StyledLabel(row, text=display_name, width=200).pack(side="left", padx=5)
            StyledLabel(row, text=str(lvl), width=80).pack(side="left", padx=5)
            StyledLabel(row, text=str(xp), width=100).pack(side="left", padx=5)
            StyledLabel(row, text=str(bytes_val), width=100).pack(side="left", padx=5)
