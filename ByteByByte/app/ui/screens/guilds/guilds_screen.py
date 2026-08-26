# guilds_screen.py
import customtkinter as ctk
import app.core.config as cfg
from app.ui.widgets.buttons import StyledButton
from app.core.database import get_user_role


class GuildsFrame(ctk.CTkFrame):
    def __init__(self, master, dashboard, **kwargs):
        super().__init__(master, fg_color=cfg.BG_COLOR, **kwargs)
        self.dashboard = dashboard
        self.user_id = dashboard.user_id
        self.role = get_user_role(self.user_id)

        StyledButton(self, text="← Назад", command=self.dashboard.restore_center,
                     width=100).pack(anchor="nw", padx=20, pady=15)

        if self.role == 'teacher':
            from app.ui.screens.teacher.teacher_panel import TeacherPanel
            self.current_panel = TeacherPanel(self, self.dashboard)
        else:
            from app.ui.screens.student.student_panel import StudentPanel
            self.current_panel = StudentPanel(self, self.dashboard)

        self.current_panel.pack(fill="both", expand=True)
