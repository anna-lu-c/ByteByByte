# dashboard_screen.py
import customtkinter as ctk
import app.core.config as cfg
from app.ui.widgets.buttons import StyledButton
from app.ui.widgets.cards import StyledLabel, StyledFrame, CardFrame
from app.core.database import get_user_gamification, get_user_role


class DashboardScreen(ctk.CTkFrame):
    def __init__(self, master, user_id, username, first_name, last_name, class_name, **kwargs):
        super().__init__(master, fg_color=cfg.BG_COLOR, **kwargs)
        self.master = master
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.class_name = class_name

        self.gamification = get_user_gamification(user_id)
        self.role = get_user_role(user_id)

        self.level = self.gamification["level"]
        self.xp = self.gamification["xp"]
        self.bytes_amt = self.gamification["bytes"]
        self.house = self.gamification["house"]
        self.titles = self.gamification["titles"]
        self.achievements = self.gamification["achievements"]

        self.setup_ui()

    def setup_ui(self):
        main = StyledFrame(self)
        main.pack(fill="both", expand=True, padx=30, pady=20)

        top = StyledFrame(main)
        top.pack(fill="x", pady=(0, 20))
        StyledLabel(top, text=f"Добро пожаловать, {self.first_name} {self.last_name}!",
                    font=("Noto Sans Condensed", 24, "bold")).pack(side="left")
        btn_frame = StyledFrame(top)
        btn_frame.pack(side="right")
        StyledButton(btn_frame, text="Профиль", command=self.show_profile, width=100).pack(side="left", padx=5)
        StyledButton(btn_frame, text="Настройки", command=self.show_settings, width=100).pack(side="left", padx=5)

        if self.role == 'teacher':
            self.setup_teacher_ui(main)
            return

        self.setup_student_ui(main)

        if self.role in ('admin', 'author'):
            self.setup_admin_button(main)

    def setup_student_ui(self, main):
        stats = StyledFrame(main)
        stats.pack(fill="x", pady=10)
        self._stat_card(stats, "Уровень", str(self.level), cfg.COLORS[cfg.current_theme]["level"])
        self._stat_card(stats, "Байты", str(self.bytes_amt), cfg.COLORS[cfg.current_theme]["bytes"])
        self._stat_card(stats, "Опыт", f"{self.xp}/{(self.level*100)}", cfg.COLORS[cfg.current_theme]["xp"])

        prog_frame = StyledFrame(main)
        prog_frame.pack(fill="x", pady=10)
        xp_needed = self.level * 100
        xp_progress = self.xp / xp_needed if xp_needed else 0
        pb = ctk.CTkProgressBar(prog_frame, width=400, corner_radius=6, progress_color=cfg.BTN_COLOR)
        pb.pack(fill="x", pady=5)
        pb.set(xp_progress)
        StyledLabel(prog_frame, text=f"До следующего уровня: {xp_needed - self.xp} XP",
                    font=("Noto Sans Condensed", 12)).pack()

        quick = StyledFrame(main)
        quick.pack(pady=20)
        actions = [
            ("🛒 Магазин", self.show_shop),
            ("🏠 Дома", self.show_houses),
            ("🏆 Достижения", self.show_achievements),
            ("🎓 Гильдии", self.show_guilds),
            ("🏆 Рейтинг", self.show_rating),          # <-- добавлена кнопка рейтинга
        ]
        for text, cmd in actions:
            StyledButton(quick, text=text, command=cmd, width=140, height=40).pack(side="left", padx=10)

        big = StyledFrame(main)
        big.pack(pady=30)
        StyledButton(big, text="📚 Тренировочный модуль", command=self.open_training,
                     width=220, height=80, font=("Noto Sans Condensed", 16, "bold")).pack(side="left", padx=15)
        StyledButton(big, text="📘 Учебник", command=self.show_theory,
                     width=220, height=80, font=("Noto Sans Condensed", 16, "bold")).pack(side="left", padx=15)
        StyledButton(big, text="🎯 Подготовительный модуль", command=self.open_exam,
                     width=220, height=80, font=("Noto Sans Condensed", 16, "bold"), fg_color="#8b5cf6").pack(side="left", padx=15)

    def setup_teacher_ui(self, main):
        info = StyledFrame(main)
        info.pack(fill="x", pady=20)
        StyledLabel(info, text="👨‍🏫 Панель учителя", font=("Noto Sans Condensed", 20, "bold")).pack(anchor="w")
        StyledLabel(info, text="Управляйте классами, создавайте тесты и сюжетные новеллы.",
                    font=("Noto Sans Condensed", 14)).pack(anchor="w", pady=5)

        quick = StyledFrame(main)
        quick.pack(pady=20)
        StyledButton(quick, text="🎓 Мои классы", command=self.show_guilds,
                     width=200, height=50, font=("Noto Sans Condensed", 16, "bold")).pack(pady=10)
        # Учитель тоже может смотреть рейтинг (по желанию)
        StyledButton(quick, text="🏆 Рейтинг", command=self.show_rating,
                     width=200, height=50, font=("Noto Sans Condensed", 16, "bold")).pack(pady=5)

    def setup_admin_button(self, main):
        admin_frame = StyledFrame(main)
        admin_frame.pack(pady=(10, 0))
        StyledButton(admin_frame, text="🛡️ Админ-панель", command=self.show_admin,
                     width=200, height=50, font=("Noto Sans Condensed", 16, "bold"),
                     fg_color="#6c5ce7", hover_color="#5a4bd1").pack()

    def _stat_card(self, parent, label, value, color):
        card = CardFrame(parent)
        card.pack(side="left", expand=True, fill="both", padx=10, pady=5)
        StyledLabel(card, text=label, font=("Noto Sans Condensed", 14),
                    text_color=cfg.COLORS[cfg.current_theme]["muted_fg"]).pack(pady=(10,0))
        StyledLabel(card, text=value, font=("Noto Sans Condensed", 28, "bold"), text_color=color).pack(pady=5)

    def clear_center(self):
        pass

    def restore_center(self):
        self.master.show_screen(DashboardScreen,
                                user_id=self.user_id,
                                username=self.username,
                                first_name=self.first_name,
                                last_name=self.last_name,
                                class_name=self.class_name)

    def _show_frame(self, frame_class):
        self.master.show_screen(frame_class, dashboard=self)

    # ---------- Навигация по экранам ----------
    def show_profile(self):
        from app.ui.screens.profile.profile_screen import ProfileFrame
        self._show_frame(ProfileFrame)

    def show_settings(self):
        from app.ui.screens.profile.settings_screen import SettingsFrame
        self._show_frame(SettingsFrame)

    def show_shop(self):
        from app.ui.screens.profile.inventory_screen import ShopFrame
        self._show_frame(ShopFrame)

    def show_houses(self):
        from app.ui.screens.houses.houses_screen import HousesFrame
        self._show_frame(HousesFrame)

    def show_guilds(self):
        from app.ui.screens.guilds.guilds_screen import GuildsFrame
        self._show_frame(GuildsFrame)

    def show_achievements(self):
        from app.ui.screens.profile.achievements_screen import AchievementsFrame
        self._show_frame(AchievementsFrame)

    def show_info(self):
        from app.ui.screens.profile.info_screen import InfoFrame
        self._show_frame(InfoFrame)

    def show_admin(self):
        from app.ui.screens.admin.admin_panel_screen import AdminPanel
        self._show_frame(AdminPanel)

    def show_theory(self):
        from app.ui.screens.training.theory_screen import TheoryScreen
        self._show_frame(TheoryScreen)

    def show_rating(self):
        from app.ui.screens.profile.rating_screen import RatingScreen
        self._show_frame(RatingScreen)

    def open_training(self):
        from app.ui.screens.training.training_screen import TrainingScreen
        self.master.show_screen(TrainingScreen,
                                user_id=self.user_id,
                                username=self.username,
                                first_name=self.first_name,
                                last_name=self.last_name,
                                class_name=self.class_name)

    def open_exam(self):
        from app.ui.screens.exam.exam_main_screen import ExamMainScreen
        self.master.show_screen(ExamMainScreen,
                                user_id=self.user_id,
                                username=self.username,
                                first_name=self.first_name,
                                last_name=self.last_name,
                                class_name=self.class_name)
