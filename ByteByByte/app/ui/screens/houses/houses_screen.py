# houses_screen.py
import customtkinter as ctk
import app.core.config as cfg
from app.ui.widgets.buttons import StyledButton
from app.ui.widgets.cards import StyledLabel, CardFrame
from app.core.database import get_user_gamification
from app.core.constants import HOUSES
from .my_house_tab import MyHouseTab
from .ranking_tab import RankingTab
from .members_tab import MembersTab


class HousesFrame(ctk.CTkFrame):
    def __init__(self, master, dashboard, **kwargs):
        super().__init__(master, fg_color=cfg.BG_COLOR, **kwargs)
        self.dashboard = dashboard
        self.user_id = dashboard.user_id
        self.gamification = get_user_gamification(self.user_id)
        self.current_house = self.gamification.get("house", "")

        StyledButton(self, text="← Назад", command=self.dashboard.restore_center,
                     width=100).pack(anchor="nw", padx=20, pady=15)

        StyledLabel(self, text="🏠 Дома", font=("Noto Sans Condensed", 26, "bold")).pack(pady=15)

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

        self.tab_my_house = self.tabview.add("🏠 Мой дом")
        self.tab_ranking = self.tabview.add("🏆 Рейтинг домов")
        self.tab_members = self.tabview.add("👥 Участники")

        MyHouseTab(self.tab_my_house, self.current_house, HOUSES, cfg)
        RankingTab(self.tab_ranking, HOUSES, cfg)
        MembersTab(self.tab_members, self.current_house, HOUSES, cfg)
