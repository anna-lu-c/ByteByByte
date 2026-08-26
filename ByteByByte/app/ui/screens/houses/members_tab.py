# members_tab.py
import customtkinter as ctk
from app.ui.widgets.cards import StyledLabel, StyledFrame
from app.core.database import get_house_members


class MembersTab:
    def __init__(self, parent, current_house, houses, cfg):
        scroll = ctk.CTkScrollableFrame(parent, fg_color=cfg.BG_COLOR)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        house_data = next((h for h in houses if h["name"] == current_house), None)
        if not house_data:
            StyledLabel(scroll, text="Вы не состоите в доме.", font=("Noto Sans Condensed", 14)).pack(pady=20)
            return

        StyledLabel(scroll, text=f"👥 Участники дома «{current_house}»",
                    font=("Noto Sans Condensed", 22, "bold"), text_color=house_data["color"]).pack(pady=10)

        members = get_house_members(current_house)
        if not members:
            StyledLabel(scroll, text="В этом доме пока нет участников.", font=("Noto Sans Condensed", 14)).pack(pady=20)
            return

        header = StyledFrame(scroll)
        header.pack(fill="x", padx=10, pady=5)
        StyledLabel(header, text="№", width=40, font=("Noto Sans Condensed", 13, "bold")).pack(side="left")
        StyledLabel(header, text="Участник", width=200, font=("Noto Sans Condensed", 13, "bold")).pack(side="left")
        StyledLabel(header, text="Уровень", width=80, font=("Noto Sans Condensed", 13, "bold")).pack(side="left")
        StyledLabel(header, text="XP", width=100, font=("Noto Sans Condensed", 13, "bold")).pack(side="left")

        for i, (first_name, last_name, level, xp) in enumerate(members, start=1):
            row = StyledFrame(scroll)
            row.pack(fill="x", padx=10, pady=2)
            StyledLabel(row, text=str(i), width=40).pack(side="left")
            StyledLabel(row, text=f"{first_name} {last_name}", width=200).pack(side="left")
            StyledLabel(row, text=str(level), width=80).pack(side="left")
            StyledLabel(row, text=str(xp), width=100).pack(side="left")
