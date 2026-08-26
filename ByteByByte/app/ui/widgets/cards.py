# cards.py
import customtkinter as ctk
import app.core.config as cfg


class StyledLabel(ctk.CTkLabel):
    def __init__(self, master, **kwargs):
        kwargs.setdefault('text_color', cfg.TEXT_COLOR)
        kwargs.setdefault('font', ("Noto Sans Condensed", 14))
        super().__init__(master, **kwargs)


class StyledFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        kwargs.setdefault('fg_color', cfg.BG_COLOR)
        kwargs.setdefault('corner_radius', 16)
        kwargs.setdefault('border_width', 0)
        super().__init__(master, **kwargs)


class CardFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        kwargs.setdefault('fg_color', cfg.TILE_BG)
        kwargs.setdefault('corner_radius', 20)
        kwargs.setdefault('border_width', 1)
        kwargs.setdefault('border_color', cfg.TILE_BORDER)
        super().__init__(master, **kwargs)
