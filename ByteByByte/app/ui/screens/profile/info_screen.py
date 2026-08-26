# info_screen.py
import customtkinter as ctk
import app.core.config as cfg
from app.ui.widgets.buttons import StyledButton
from app.ui.widgets.cards import StyledLabel, StyledFrame, CardFrame

class InfoFrame(ctk.CTkFrame):
    def __init__(self, master, dashboard, **kwargs):
        super().__init__(master, fg_color=cfg.BG_COLOR, **kwargs)
        self.dashboard = dashboard

        StyledButton(self, text="← Назад", command=self.dashboard.restore_center,
                     width=100).pack(anchor="nw", padx=20, pady=15)

        scroll = ctk.CTkScrollableFrame(self, fg_color=cfg.BG_COLOR)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        # === О приложении ===
        card_about = CardFrame(scroll)
        card_about.pack(fill="x", pady=10)

        StyledLabel(card_about, text="📘 О приложении", font=("Noto Sans Condensed", 18, "bold")).pack(anchor="w", pady=5, padx=10)
        info = ("«Байт за Байтом» — современный геймифицированный тренажёр для подготовки к ЕГЭ по информатике.\n\n"
                "• 27 заданий с теорией и практикой\n"
                "• Симуляция экзамена с таймером 235 минут\n"
                "• Аналитика прогресса и детальные отчёты\n"
                "• Уровни, XP, байты, дома, достижения и магазин\n"
                "• Сохранение прогресса в базе данных")
        StyledLabel(card_about, text=info, wraplength=700, justify="left", font=("Noto Sans Condensed", 14)).pack(anchor="w", pady=5, padx=10)

        # === Инструкция ===
        card_instruction = CardFrame(scroll)
        card_instruction.pack(fill="x", pady=10)

        StyledLabel(card_instruction, text="📖 Инструкция", font=("Noto Sans Condensed", 18, "bold")).pack(anchor="w", pady=5, padx=10)
        instruction = ("1. Зарегистрируйтесь или войдите в аккаунт.\n"
                       "2. Изучайте теорию и решайте задачи в Тренировочном модуле.\n"
                       "3. Зарабатывайте XP и байты за правильные ответы.\n"
                       "4. Повышайте уровень, покупайте титулы в магазине.\n"
                       "5. Вступайте в дома для получения бонусов.\n"
                       "6. Проверьте свои силы в Подготовительном модуле — симуляции ЕГЭ.\n"
                       "7. Анализируйте результаты через вкладку Аналитика.\n"
                       "8. Экспортируйте отчёт в профиле.")
        StyledLabel(card_instruction, text=instruction, wraplength=700, justify="left", font=("Noto Sans Condensed", 14)).pack(anchor="w", pady=5, padx=10)

        # === Геймификация ===
        card_gamification = CardFrame(scroll)
        card_gamification.pack(fill="x", pady=10)

        StyledLabel(card_gamification, text="🎮 Геймификация", font=("Noto Sans Condensed", 18, "bold")).pack(anchor="w", pady=5, padx=10)
        gamification_text = ("• XP (опыт) — получайте за решение задач и экзамены.\n"
                             "• Уровни — каждый новый уровень даёт +50 байтов.\n"
                             "• Байты — внутриигровая валюта для магазина.\n"
                             "• Дома — глобальные сообщества с бонусами.\n"
                             "• Достижения — особые награды за успехи.\n"
                             "• Титулы и бустеры — покупайте в магазине.")
        StyledLabel(card_gamification, text=gamification_text, wraplength=700, justify="left", font=("Noto Sans Condensed", 14)).pack(anchor="w", pady=5, padx=10)

        # === Техническая информация ===
        card_tech = CardFrame(scroll)
        card_tech.pack(fill="x", pady=10)

        StyledLabel(card_tech, text="💻 Техническая информация", font=("Noto Sans Condensed", 18, "bold")).pack(anchor="w", pady=5, padx=10)
        tech_text = ("• Разработано на Python + customtkinter\n"
                     "• База данных: SQLite\n"
                     "• Графики: matplotlib\n"
                     "• Поддерживается светлая и тёмная тема")
        StyledLabel(card_tech, text=tech_text, wraplength=700, justify="left", font=("Noto Sans Condensed", 14)).pack(anchor="w", pady=5, padx=10)

        # === Автор ===
        card_author = CardFrame(scroll)
        card_author.pack(fill="x", pady=10)

        StyledLabel(card_author, text="👩‍💻 Об авторе", font=("Noto Sans Condensed", 18, "bold")).pack(anchor="w", pady=5, padx=10)
        author_text = "Лукина Анна Вячеславовна\nСтудентка НовГУ, группа 2241\nПроект в рамках курсовой работы"
        StyledLabel(card_author, text=author_text, font=("Noto Sans Condensed", 14), justify="center").pack(pady=5)

        # Версия
        StyledLabel(scroll, text="Версия 2.0.0", font=("Noto Sans Condensed", 12), text_color=cfg.COLORS[cfg.current_theme]["muted_fg"]).pack(pady=15)
