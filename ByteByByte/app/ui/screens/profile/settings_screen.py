# settings_screen.py
import customtkinter as ctk
from app.ui.widgets.buttons import StyledButton
from app.ui.widgets.cards import StyledLabel, StyledFrame, CardFrame
import app.core.config as cfg
from app.core.database import get_user_gamification, update_user_gamification


class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, dashboard, **kwargs):
        super().__init__(master, fg_color=cfg.BG_COLOR, **kwargs)
        self.dashboard = dashboard
        self.user_id = dashboard.user_id

        self.gamification = get_user_gamification(self.user_id)
        self.current_theme = self.gamification.get("theme", "light")

        StyledButton(self, text="← Назад", command=self.dashboard.restore_center,
                     width=100).pack(anchor="nw", padx=20, pady=15)

        scroll = ctk.CTkScrollableFrame(self, fg_color=cfg.BG_COLOR)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        StyledLabel(scroll, text="⚙️ Настройки", font=("Noto Sans Condensed", 26, "bold")).pack(pady=10)

        # === Карточка темы ===
        card_theme = CardFrame(scroll)
        card_theme.pack(fill="x", pady=10)

        StyledLabel(card_theme, text="🎨 Оформление", font=("Noto Sans Condensed", 18, "bold")).pack(anchor="w", padx=15, pady=5)

        theme_frame = StyledFrame(card_theme)
        theme_frame.pack(fill="x", padx=15, pady=10)

        StyledLabel(theme_frame, text="Тема:", font=("Noto Sans Condensed", 14)).pack(side="left", padx=5)

        self.theme_var = ctk.StringVar(value=self.current_theme)
        theme_menu = ctk.CTkOptionMenu(theme_frame, values=["light", "dark"],
                                       variable=self.theme_var,
                                       fg_color=cfg.BTN_COLOR, button_color=cfg.BTN_HOVER,
                                       text_color=cfg.TEXT_COLOR, width=120)
        theme_menu.pack(side="left", padx=10)

        apply_theme_btn = StyledButton(theme_frame, text="Применить", command=self.change_theme,
                                       width=100)
        apply_theme_btn.pack(side="left", padx=10)

        # === Карточка анимаций ===
        card_anim = CardFrame(scroll)
        card_anim.pack(fill="x", pady=10)

        StyledLabel(card_anim, text="✨ Анимации", font=("Noto Sans Condensed", 18, "bold")).pack(anchor="w", padx=15, pady=5)

        anim_frame = StyledFrame(card_anim)
        anim_frame.pack(fill="x", padx=15, pady=10)

        self.animations_var = ctk.BooleanVar(value=True)
        anim_cb = ctk.CTkCheckBox(anim_frame, text="Включить анимации (конфетти, тосты)",
                                  variable=self.animations_var,
                                  text_color=cfg.TEXT_COLOR, fg_color=cfg.BTN_COLOR)
        anim_cb.pack(anchor="w", pady=2)

        # === Карточка звука ===
        card_sound = CardFrame(scroll)
        card_sound.pack(fill="x", pady=10)

        StyledLabel(card_sound, text="🔊 Звук", font=("Noto Sans Condensed", 18, "bold")).pack(anchor="w", padx=15, pady=5)

        sound_frame = StyledFrame(card_sound)
        sound_frame.pack(fill="x", padx=15, pady=10)

        self.sound_var = ctk.BooleanVar(value=True)
        sound_cb = ctk.CTkCheckBox(sound_frame, text="Включить звуковые эффекты",
                                   variable=self.sound_var,
                                   text_color=cfg.TEXT_COLOR, fg_color=cfg.BTN_COLOR)
        sound_cb.pack(anchor="w", pady=2)

        StyledLabel(sound_frame, text="(Функция в разработке)", font=("Noto Sans Condensed", 12),
                    text_color=cfg.COLORS[cfg.current_theme]["muted_fg"]).pack(anchor="w", pady=2)

        # === Карточка сброса настроек ===
        card_reset = CardFrame(scroll)
        card_reset.pack(fill="x", pady=10)

        StyledLabel(card_reset, text="🔄 Сброс", font=("Noto Sans Condensed", 18, "bold")).pack(anchor="w", padx=15, pady=5)

        reset_frame = StyledFrame(card_reset)
        reset_frame.pack(fill="x", padx=15, pady=10)

        StyledButton(reset_frame, text="Сбросить все настройки по умолчанию",
                     command=self.reset_settings, width=250).pack(pady=5)

        # === Информация ===
        StyledLabel(scroll, text="Версия приложения: 2.0.0",
                    font=("Noto Sans Condensed", 12), text_color=cfg.COLORS[cfg.current_theme]["muted_fg"]).pack(pady=15)

    def change_theme(self):
        new_theme = self.theme_var.get()
        if new_theme == self.current_theme:
            return
        self.current_theme = new_theme
        cfg.apply_theme(new_theme)
        update_user_gamification(self.user_id, theme=new_theme)
        self.dashboard.master.configure(fg_color=cfg.BG_COLOR)
        self.dashboard.restore_center()

    def reset_settings(self):
        from tkinter import messagebox
        if messagebox.askyesno("Сброс настроек", "Вернуть все настройки приложения к исходным?"):
            cfg.apply_theme("light")
            update_user_gamification(self.user_id, theme="light")
            self.theme_var.set("light")
            self.animations_var.set(True)
            self.sound_var.set(True)
            messagebox.showinfo("Сброс", "Настройки сброшены. Тема изменена на светлую.")
            self.dashboard.restore_center()
