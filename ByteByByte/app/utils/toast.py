# toast.py
from tkinter import Toplevel
import customtkinter as ctk
from app.core.config import COLORS, current_theme


class Toast(Toplevel):
    def __init__(self, parent, message, duration=2000, is_success=True):
        super().__init__(parent)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        theme_colors = COLORS[current_theme]
        bg = theme_colors["success"] if is_success else theme_colors["error"]
        self.configure(bg=bg)
        ctk.CTkLabel(self, text=message, text_color="white",
                     font=("Noto Sans Condensed", 12, "bold")).pack(padx=20, pady=10)
        x = parent.winfo_x() + parent.winfo_width() - 300
        y = parent.winfo_y() + parent.winfo_height() - 80
        self.geometry(f"+{x}+{y}")
        self.after(duration, self.destroy)
