# login_screen.py
import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import app.core.config as cfg
from app.ui.widgets.buttons import StyledButton
from app.ui.widgets.cards import StyledLabel, StyledFrame, CardFrame
from app.core.database import login_user, load_last_user, save_last_user, clear_last_user


class LoginScreen(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=cfg.BG_COLOR, **kwargs)
        self.master = master
        self.setup_ui()
        self.after(100, self.auto_login)

    def setup_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        card = CardFrame(self)
        card.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        title = StyledLabel(card, text="Байт за Байтом",
                            font=("Noto Sans Condensed", 32, "bold"))
        title.grid(row=0, column=0, pady=(30, 10))

        subtitle = StyledLabel(card, text="Геймифицированная подготовка к ЕГЭ по информатике",
                               font=("Noto Sans Condensed", 14))
        subtitle.grid(row=1, column=0, pady=(0, 30))

        self.login_entry = ctk.CTkEntry(card, placeholder_text="Логин", width=280, height=45,
                                        corner_radius=12, text_color=cfg.TEXT_COLOR)
        self.login_entry.grid(row=2, column=0, pady=8)

        self.password_entry = ctk.CTkEntry(card, placeholder_text="Пароль", show="*",
                                           width=280, height=45, corner_radius=12,
                                           text_color=cfg.TEXT_COLOR)
        self.password_entry.grid(row=3, column=0, pady=8)

        self.remember_var = ctk.BooleanVar(value=True)
        remember_cb = ctk.CTkCheckBox(card, text="Запомнить меня",
                                      variable=self.remember_var,
                                      text_color=cfg.TEXT_COLOR, fg_color=cfg.BTN_COLOR,
                                      corner_radius=6)
        remember_cb.grid(row=4, column=0, pady=10)

        login_btn = StyledButton(card, text="Войти", command=self.login, width=220, height=45)
        login_btn.grid(row=5, column=0, pady=10)

        register_btn = ctk.CTkButton(card, text="Зарегистрироваться",
                                     command=self.open_register, width=220, height=45,
                                     fg_color="transparent", border_width=2,
                                     border_color=cfg.BTN_COLOR, text_color=cfg.TEXT_COLOR,
                                     hover_color=cfg.BTN_HOVER)
        register_btn.grid(row=6, column=0, pady=10)

        demo_label = StyledLabel(card, text="Демо-доступ: логин 'demo', пароль 'demo'",
                                 font=("Noto Sans Condensed", 12, "italic"),
                                 text_color=cfg.COLORS[cfg.current_theme]["muted_fg"])
        demo_label.grid(row=7, column=0, pady=(20, 10))

    def auto_login(self):
        last_user = load_last_user()
        if last_user:
            self.login_entry.insert(0, last_user)
            self.after(200, self._safe_focus_password)

    def _safe_focus_password(self):
        try:
            if self.winfo_exists() and self.password_entry.winfo_exists():
                self.password_entry.focus()
        except Exception:
            pass

    def login(self):
        username = self.login_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль")
            return

        user_id, first_name, last_name, class_name, onboarding_shown = login_user(username, password)
        if user_id is None:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")
            return

        try:
            conn = sqlite3.connect(cfg.DB_PATH)
            blocked = conn.execute("SELECT blocked FROM users WHERE id = ?", (user_id,)).fetchone()
            conn.close()
            if blocked and blocked[0]:
                messagebox.showerror("Ошибка", "Ваш аккаунт заблокирован. Обратитесь к администратору.")
                return
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось проверить статус аккаунта: {e}")
            return

        if self.remember_var.get():
            save_last_user(username)
        else:
            clear_last_user()

        from app.core.database import get_user_gamification
        gam = get_user_gamification(user_id)
        cfg.apply_theme(gam.get("theme", "light"))

        if not onboarding_shown:
            from app.ui.screens.auth.onboarding_screen import OnboardingScreen
            self.master.show_screen(OnboardingScreen,
                                    user_id=user_id, username=username,
                                    first_name=first_name, last_name=last_name,
                                    class_name=class_name)
        else:
            from app.ui.screens.dashboard.dashboard_screen import DashboardScreen
            self.master.show_screen(DashboardScreen,
                                    user_id=user_id, username=username,
                                    first_name=first_name, last_name=last_name,
                                    class_name=class_name)

    def open_register(self):
        from app.ui.screens.auth.register_screen import RegisterScreen
        self.master.show_screen(RegisterScreen)
