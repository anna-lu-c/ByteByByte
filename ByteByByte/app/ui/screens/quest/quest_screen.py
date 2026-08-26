# quest_screen.py
import customtkinter as ctk
from app.ui.widgets.buttons import StyledButton
from app.ui.widgets.cards import StyledLabel

class QuestScreen(ctk.CTkFrame):
    def __init__(self, master, dashboard, **kwargs):
        super().__init__(master, fg_color="#f0f0f0")
        self.dashboard = dashboard

        StyledButton(self, text="← Назад", command=self.dashboard.restore_center,
                     width=100).pack(anchor="nw", padx=20, pady=15)
        StyledLabel(self, text="📜 Текстовый квест",
                    font=("Noto Sans Condensed", 26, "bold")).pack(pady=20)
        StyledLabel(self, text="Этот раздел находится в разработке.\n"
                               "Здесь будет сюжетный квест с задачами и развилками.",
                    font=("Noto Sans Condensed", 14)).pack(pady=10)
