# onboarding_screen.py
import customtkinter as ctk
import app.core.config as cfg
from app.ui.widgets.buttons import StyledButton
from app.ui.widgets.cards import StyledLabel, StyledFrame, CardFrame
from app.core.database import set_onboarding_shown


class OnboardingScreen(ctk.CTkFrame):
    def __init__(self, master, user_id, username, first_name, last_name, class_name, **kwargs):
        super().__init__(master, fg_color=cfg.BG_COLOR, **kwargs)
        self.master = master
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.class_name = class_name
        self.setup_ui()

    def setup_ui(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color=cfg.BG_COLOR)
        scroll.pack(fill="both", expand=True, padx=30, pady=20)

        StyledLabel(scroll, text="Добро пожаловать в «Байт за Байтом»!",
                    font=("Noto Sans Condensed", 26, "bold")).pack(pady=(20, 10))

        card_about = CardFrame(scroll)
        card_about.pack(fill="x", pady=10)
        StyledLabel(card_about, text="📱 О приложении", font=("Noto Sans Condensed", 18, "bold")).pack(anchor="w", padx=15, pady=5)
        about_text = ("«Байт за Байтом» — это современный геймифицированный тренажёр для подготовки к ЕГЭ по информатике.\n\n"
                      "• 27 заданий с теорией и практикой\n"
                      "• Симуляция экзамена с таймером\n"
                      "• Детальная аналитика прогресса\n"
                      "• Уровни, XP, байты, дома, достижения и магазин")
        StyledLabel(card_about, text=about_text, wraplength=700, justify="left", font=("Noto Sans Condensed", 14)).pack(anchor="w", padx=15, pady=5)

        card_gamification = CardFrame(scroll)
        card_gamification.pack(fill="x", pady=10)
        StyledLabel(card_gamification, text="🎮 Как работает геймификация", font=("Noto Sans Condensed", 18, "bold")).pack(anchor="w", padx=15, pady=5)
        gam_text = ("• За каждое правильно решённое задание вы получаете +10 XP и +5 байтов.\n"
                    "• За успешную сдачу экзамена — +20 XP и +10 байтов за каждое верное задание.\n"
                    "• При повышении уровня вы получаете +50 байтов и праздничный салют.\n"
                    "• Байты можно тратить в магазине на титулы и бустеры.\n"
                    "• Вступайте в дома, чтобы получать постоянные бонусы к опыту или байтам.\n"
                    "• Достижения открываются за особые успехи (100 решённых задач, 10 уровень и т.д.)")
        StyledLabel(card_gamification, text=gam_text, wraplength=700, justify="left", font=("Noto Sans Condensed", 14)).pack(anchor="w", padx=15, pady=5)

        card_ege = CardFrame(scroll)
        card_ege.pack(fill="x", pady=10)
        StyledLabel(card_ege, text="📚 Об ЕГЭ по информатике", font=("Noto Sans Condensed", 18, "bold")).pack(anchor="w", padx=15, pady=5)
        ege_text = ("• Количество заданий: 27\n"
                    "• Продолжительность: 235 минут\n"
                    "• Максимальный первичный балл: 29 (с 2024 г.)\n"
                    "• Минимальный тестовый балл для поступления в вузы: 44")
        StyledLabel(card_ege, text=ege_text, justify="left", font=("Noto Sans Condensed", 14)).pack(anchor="w", padx=15, pady=5)

        card_author = CardFrame(scroll)
        card_author.pack(fill="x", pady=10)
        StyledLabel(card_author, text="👩‍💻 Об авторе", font=("Noto Sans Condensed", 18, "bold")).pack(anchor="w", padx=15, pady=5)
        author_text = "Лукина Анна Вячеславовна\nСтудентка НовГУ, группа 2241"
        StyledLabel(card_author, text=author_text, font=("Noto Sans Condensed", 14), justify="center").pack(pady=5)

        continue_btn = StyledButton(scroll, text="Начать обучение →", command=self.finish_onboarding,
                                    width=250, height=45, font=("Noto Sans Condensed", 16, "bold"))
        continue_btn.pack(pady=30)

    def finish_onboarding(self):
        set_onboarding_shown(self.user_id)
        cfg.apply_theme("light")
        from app.ui.screens.dashboard.dashboard_screen import DashboardScreen
        self.master.show_screen(DashboardScreen, user_id=self.user_id, username=self.username,
                                first_name=self.first_name, last_name=self.last_name, class_name=self.class_name)
