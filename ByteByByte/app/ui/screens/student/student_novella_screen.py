# student_novella_screen.py
import customtkinter as ctk
import app.core.config as cfg
from app.ui.widgets.buttons import StyledButton
from app.ui.widgets.cards import StyledLabel


class NovelScreen(ctk.CTkFrame):
    def __init__(self, master, dashboard, class_id, **kwargs):
        super().__init__(master, fg_color=cfg.BG_COLOR, **kwargs)
        self.dashboard = dashboard

        StyledButton(self, text="← Назад", command=self.dashboard.restore_center,
                     width=100).pack(anchor="nw", padx=20, pady=15)

        StyledLabel(self, text="📖 Сюжетная новелла", font=("Noto Sans Condensed", 26, "bold")).pack(pady=15)
        StyledLabel(self, text="Этот раздел находится в разработке.\n"
                               "Здесь будут отображаться главы новеллы, созданные учителем.",
                    font=("Noto Sans Condensed", 14)).pack(pady=20)
