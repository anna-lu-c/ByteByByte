# ranking_tab.py
import customtkinter as ctk
from app.ui.widgets.cards import StyledLabel, CardFrame, StyledFrame
from app.core.database import get_house_ranking


class RankingTab:
    def __init__(self, parent, houses, cfg):
        scroll = ctk.CTkScrollableFrame(parent, fg_color=cfg.BG_COLOR)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        StyledLabel(scroll, text="🏆 Рейтинг домов", font=("Noto Sans Condensed", 22, "bold")).pack(pady=10)

        ranking = get_house_ranking()
        if not ranking:
            StyledLabel(scroll, text="Пока нет данных для рейтинга.", font=("Noto Sans Condensed", 14)).pack(pady=20)
            return

        max_xp = max([xp for _, xp in ranking]) if ranking else 1

        for i, (house_name, total_xp) in enumerate(ranking, start=1):
            house_data = next((h for h in houses if h["name"] == house_name), None)
            if not house_data:
                continue

            card = CardFrame(scroll)
            card.pack(fill="x", pady=5, padx=10)

            row = StyledFrame(card)
            row.pack(fill="x", padx=10, pady=5)

            StyledLabel(row, text=f"#{i}", font=("Noto Sans Condensed", 18, "bold"), width=50).pack(side="left")
            StyledLabel(row, text=house_data["icon"], font=("Noto Sans Condensed", 24)).pack(side="left", padx=5)
            StyledLabel(row, text=house_name, font=("Noto Sans Condensed", 16, "bold"),
                        text_color=house_data["color"], width=150).pack(side="left")

            bar_frame = StyledFrame(row)
            bar_frame.pack(side="left", fill="x", expand=True, padx=10)
            progress = total_xp / max_xp if max_xp > 0 else 0
            progress_bar = ctk.CTkProgressBar(bar_frame, height=12, corner_radius=6,
                                              progress_color=house_data["color"])
            progress_bar.pack(side="left", fill="x", expand=True)
            progress_bar.set(progress)

            StyledLabel(row, text=f"{total_xp} XP", font=("Noto Sans Condensed", 14, "bold"), width=100).pack(side="right")
