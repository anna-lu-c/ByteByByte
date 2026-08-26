# buttons.py
import customtkinter as ctk
import app.core.config as cfg


class StyledButton(ctk.CTkButton):
    def __init__(self, master, **kwargs):
        kwargs.setdefault('fg_color', cfg.BTN_COLOR)
        kwargs.setdefault('hover_color', cfg.BTN_HOVER)
        kwargs.setdefault('text_color', cfg.TEXT_COLOR)
        kwargs.setdefault('corner_radius', 12)
        kwargs.setdefault('border_width', 0)
        kwargs.setdefault('font', ("Noto Sans Condensed", 14, "normal"))
        super().__init__(master, **kwargs)
