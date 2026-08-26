# achievements_screen.py
import customtkinter as ctk
import app.core.config as cfg
from app.ui.widgets.buttons import StyledButton
from app.ui.widgets.cards import StyledLabel, CardFrame
from app.core.database import get_user_gamification
from app.core.constants import ACHIEVEMENTS


class AchievementsFrame(ctk.CTkFrame):
    def __init__(self, master, dashboard, **kwargs):
        super().__init__(master, fg_color=cfg.BG_COLOR, **kwargs)
        self.dashboard = dashboard
        self.user_id = dashboard.user_id
        self.gamification = get_user_gamification(self.user_id)

        StyledButton(self, text="← Назад", command=self.dashboard.restore_center,
                     width=100).pack(anchor="nw", padx=20, pady=15)

        scroll = ctk.CTkScrollableFrame(self, fg_color=cfg.BG_COLOR)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        StyledLabel(scroll, text="🏆 Достижения", font=("Noto Sans Condensed", 26, "bold")).pack(pady=10)

        unlocked_count = len([a for a in ACHIEVEMENTS if a["id"] in self.gamification["achievements"]])
        StyledLabel(scroll, text=f"Получено: {unlocked_count} / {len(ACHIEVEMENTS)}",
                    font=("Noto Sans Condensed", 14)).pack(pady=5)

        container = ctk.CTkFrame(scroll, fg_color="transparent")
        container.pack(fill="both", expand=True, pady=10)

        for i, ach in enumerate(ACHIEVEMENTS):
            unlocked = ach["id"] in self.gamification["achievements"]
            card = CardFrame(container)
            row = i // 3
            col = i % 3
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            StyledLabel(card, text=ach["icon"], font=("Noto Sans Condensed", 32)).pack(pady=(10, 0))
            StyledLabel(card, text=ach["name"], font=("Noto Sans Condensed", 16, "bold")).pack()
            StyledLabel(card, text=ach["desc"], font=("Noto Sans Condensed", 12),
                        text_color=cfg.COLORS[cfg.current_theme]["muted_fg"]).pack(pady=2)
            status = "✅ ПОЛУЧЕНО" if unlocked else "🔒 ЗАКРЫТО"
            color = cfg.COLORS[cfg.current_theme]["success"] if unlocked else cfg.COLORS[cfg.current_theme]["muted_fg"]
            StyledLabel(card, text=status, font=("Noto Sans Condensed", 12, "bold"), text_color=color).pack(pady=5)

        for i in range(3):
            container.columnconfigure(i, weight=1)
