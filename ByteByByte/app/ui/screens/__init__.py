# __init__.py

from .auth.login_screen import LoginScreen
from .auth.register_screen import RegisterScreen
from .auth.onboarding_screen import OnboardingScreen

from .dashboard.dashboard_screen import DashboardScreen

from .training.training_screen import TrainingScreen
from .training.section_screen import SectionFrame
from .training.combined_game_screen import CombinedGameFrame
from .training.theory_screen import TheoryScreen

from .exam.exam_main_screen import ExamMainScreen
from .exam.exam_test_screen import ExamTestScreen

from .quest.quest_screen import QuestScreen

from .teacher.teacher_panel import TeacherPanel
from .teacher.create_test_screen import CreateTestScreen

from .student.take_test_screen import TakeTestScreen

from .profile.profile_screen import ProfileFrame
from .profile.settings_screen import SettingsFrame
from .profile.achievements_screen import AchievementsFrame
from .profile.inventory_screen import ShopFrame
from .profile.info_screen import InfoFrame
from .profile.rating_screen import RatingScreen

from .houses.houses_screen import HousesFrame
from .guilds.guilds_screen import GuildsFrame

from .admin.admin_panel_screen import AdminPanel

__all__ = [
    "LoginScreen",
    "RegisterScreen",
    "OnboardingScreen",
    "DashboardScreen",
    "TrainingScreen",
    "SectionFrame",
    "CombinedGameFrame",
    "ExamMainScreen",
    "ExamTestScreen",
    "QuestScreen",
    "TeacherPanel",
    "CreateTestScreen",
    "TakeTestScreen",
    "ProfileFrame",
    "SettingsFrame",
    "ShopFrame",
    "HousesFrame",
    "GuildsFrame",
    "InfoFrame",
    "RatingScreen",
    "AchievementsFrame",
    "AdminPanel",
    "TheoryScreen",
]
