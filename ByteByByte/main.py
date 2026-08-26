# main.py
import customtkinter as ctk
from tkinter import messagebox
import sys
import os

# Настройка внешнего вида
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# Импорт конфигурации из нового ядра
from app.core.config import BG_COLOR, load_app_fonts, FONT_BOLD

# Загружаем кастомные шрифты до создания любых виджетов
load_app_fonts()


class MainApplication(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.configure(fg_color=BG_COLOR)
        self.title("Байт за Байтом")
        self.geometry("1000x700")
        self.minsize(800, 600)

        self.current_screen = None
        self.show_login_screen()
        # Перехватываем закрытие окна
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def show_screen(self, screen_class, **kwargs):
        """Уничтожает текущий экран и создаёт новый."""
        if self.current_screen is not None:
            self.current_screen.destroy()
        self.current_screen = screen_class(self, **kwargs)
        self.current_screen.pack(fill="both", expand=True)

    def show_login_screen(self):
        try:
            # Новый путь к экрану входа
            from app.ui.screens.auth.login_screen import LoginScreen
            self.show_screen(LoginScreen)
        except ImportError as e:
            print(f"Ошибка импорта LoginScreen: {e}")
            self.show_fallback_screen()

    def show_fallback_screen(self):
        fallback_frame = ctk.CTkFrame(self, fg_color=BG_COLOR)
        label = ctk.CTkLabel(
            fallback_frame,
            text="Загрузка...\n\nПожалуйста, подождите.\nЕсли это сообщение не исчезает,\nпроверьте структуру проекта.",
            font=FONT_BOLD
        )
        label.pack(expand=True)
        self.current_screen = fallback_frame
        self.current_screen.pack(fill="both", expand=True)

    def on_close(self):
        # Новый путь к экрану теста
        from app.ui.screens.exam.exam_test_screen import ExamTestScreen
        if isinstance(self.current_screen, ExamTestScreen) and self.current_screen.test_active:
            if messagebox.askyesno("Выход из теста",
                                   "Вы действительно хотите выйти? Активный тест будет завершён, результаты сохранятся."):
                self.current_screen.finish_exam()
                self.destroy()
            else:
                return
        else:
            self.destroy()


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
