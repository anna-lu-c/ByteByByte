# my_house_tab.py
import customtkinter as ctk
from app.ui.widgets.cards import StyledLabel, CardFrame, StyledFrame


class MyHouseTab:
    def __init__(self, parent, current_house, houses, cfg):
        scroll = ctk.CTkScrollableFrame(parent, fg_color=cfg.BG_COLOR)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        house_data = next((h for h in houses if h["name"] == current_house), None)

        if not house_data:
            StyledLabel(scroll, text="Вы не состоите в доме. Дом назначается автоматически при регистрации.",
                        font=("Noto Sans Condensed", 14), wraplength=500).pack(pady=20)
            return

        card = CardFrame(scroll)
        card.pack(fill="x", padx=10, pady=10)

        header = StyledFrame(card)
        header.pack(fill="x", pady=(10, 5))
        StyledLabel(header, text=house_data["icon"], font=("Noto Sans Condensed", 36)).pack(side="left", padx=10)
        StyledLabel(header, text=house_data["name"], font=("Noto Sans Condensed", 24, "bold"),
                    text_color=house_data["color"]).pack(side="left", padx=5)

        StyledLabel(card, text=f"Символ: {house_data['symbol']}",
                    font=("Noto Sans Condensed", 14, "italic")).pack(anchor="w", padx=10, pady=2)
        StyledLabel(card, text=house_data["motto"],
                    font=("Noto Sans Condensed", 16, "bold"), text_color=house_data["color"]).pack(anchor="w", padx=10, pady=5)

        StyledLabel(card, text="📜 Философия дома", font=("Noto Sans Condensed", 16, "bold")).pack(anchor="w", padx=10, pady=(10, 2))
        StyledLabel(card, text=house_data["description"], wraplength=600,
                    justify="left", font=("Noto Sans Condensed", 13)).pack(anchor="w", padx=10, pady=2)

        StyledLabel(card, text="📖 Легенда", font=("Noto Sans Condensed", 16, "bold")).pack(anchor="w", padx=10, pady=(10, 2))
        StyledLabel(card, text=house_data["legend"], wraplength=600,
                    justify="left", font=("Noto Sans Condensed", 13)).pack(anchor="w", padx=10, pady=2)

        StyledLabel(card, text="✨ Бонусы", font=("Noto Sans Condensed", 16, "bold")).pack(anchor="w", padx=10, pady=(10, 2))
        StyledLabel(card, text=house_data["bonus_description"], font=("Noto Sans Condensed", 13)).pack(anchor="w", padx=10, pady=2)
        StyledLabel(card, text="Дом назначен случайно при регистрации и не может быть изменён.",
                    font=("Noto Sans Condensed", 11, "italic"),
                    text_color=cfg.COLORS[cfg.current_theme]["muted_fg"]).pack(anchor="w", padx=10, pady=10)
