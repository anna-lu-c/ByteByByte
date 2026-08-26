# register_screen.py
import customtkinter as ctk
from tkinter import messagebox
import random
import app.core.config as cfg
from app.ui.widgets.buttons import StyledButton
from app.ui.widgets.cards import StyledLabel, StyledFrame, CardFrame
from app.core.database import register_user, update_user_gamification
from app.core.constants import HOUSES


class RegisterScreen(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=cfg.BG_COLOR, **kwargs)
        self.master = master
        self.setup_ui()

    def setup_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        card = CardFrame(self)
        card.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        StyledLabel(card, text="Регистрация", font=("Noto Sans Condensed", 28, "bold")).pack(pady=(20, 15))

        self.first_name_entry = ctk.CTkEntry(card, placeholder_text="Имя", width=280, height=40,
                                             corner_radius=12, text_color=cfg.TEXT_COLOR)
        self.first_name_entry.pack(pady=8)

        self.last_name_entry = ctk.CTkEntry(card, placeholder_text="Фамилия", width=280, height=40,
                                            corner_radius=12, text_color=cfg.TEXT_COLOR)
        self.last_name_entry.pack(pady=8)

        self.class_entry = ctk.CTkEntry(card, placeholder_text="Класс (например, 11А)", width=280, height=40,
                                        corner_radius=12, text_color=cfg.TEXT_COLOR)
        self.class_entry.pack(pady=8)

        self.login_entry = ctk.CTkEntry(card, placeholder_text="Придумайте логин", width=280, height=40,
                                        corner_radius=12, text_color=cfg.TEXT_COLOR)
        self.login_entry.pack(pady=8)

        self.password_entry = ctk.CTkEntry(card, placeholder_text="Придумайте пароль", show="*", width=280, height=40,
                                           corner_radius=12, text_color=cfg.TEXT_COLOR)
        self.password_entry.pack(pady=8)

        self.password2_entry = ctk.CTkEntry(card, placeholder_text="Повторите пароль", show="*", width=280, height=40,
                                            corner_radius=12, text_color=cfg.TEXT_COLOR)
        self.password2_entry.pack(pady=8)

        register_btn = StyledButton(card, text="Зарегистрироваться", command=self.register,
                                    width=220, height=45, font=("Noto Sans Condensed", 14, "bold"))
        register_btn.pack(pady=20)

        back_btn = ctk.CTkButton(card, text="← Назад ко входу", command=self.back_to_login,
                                 fg_color="transparent", border_width=2,
                                 text_color=cfg.TEXT_COLOR, width=200, height=40,
                                 corner_radius=12)
        back_btn.pack(pady=(0, 20))

        self.password2_entry.bind("<Return>", lambda e: self.register())

    def register(self):
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        class_name = self.class_entry.get().strip()
        username = self.login_entry.get().strip()
        pwd = self.password_entry.get().strip()
        pwd2 = self.password2_entry.get().strip()

        if not all([first_name, last_name, class_name, username, pwd]):
            messagebox.showerror("Ошибка", "Заполните все поля")
            return
        if pwd != pwd2:
            messagebox.showerror("Ошибка", "Пароли не совпадают")
            return
        if len(pwd) < 4:
            messagebox.showerror("Ошибка", "Пароль должен содержать не менее 4 символов")
            return

        user_id = register_user(username, pwd, first_name, last_name, class_name)
        if user_id is None:
            messagebox.showerror("Ошибка", "Пользователь с таким логином уже существует")
            return

        house = random.choice(HOUSES)['name']
        update_user_gamification(user_id, house=house)

        messagebox.showinfo("Успех", "Регистрация прошла успешно!")
        cfg.apply_theme("light")
        from app.ui.screens.auth.onboarding_screen import OnboardingScreen
        self.master.show_screen(OnboardingScreen, user_id=user_id, username=username,
                                first_name=first_name, last_name=last_name, class_name=class_name)

    def back_to_login(self):
        from app.ui.screens.auth.login_screen import LoginScreen
        self.master.show_screen(LoginScreen)
