# admin_panel_screen.py
import customtkinter as ctk
from tkinter import messagebox
import app.core.config as cfg
from app.ui.widgets.buttons import StyledButton
from app.ui.widgets.cards import StyledLabel, StyledFrame, CardFrame
from app.core.database import get_all_users, update_user_role, toggle_block_user, delete_user

class AdminPanel(ctk.CTkFrame):
    def __init__(self, master, dashboard, **kwargs):
        super().__init__(master, fg_color=cfg.BG_COLOR, **kwargs)
        self.dashboard = dashboard

        StyledButton(self, text="← Назад", command=self.dashboard.restore_center,
                     width=100).pack(anchor="nw", padx=20, pady=15)

        StyledLabel(self, text="🛡️ Панель администратора", font=("Noto Sans Condensed", 26, "bold")).pack(pady=15)

        self.users_frame = ctk.CTkScrollableFrame(self, fg_color=cfg.BG_COLOR)
        self.users_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.refresh_btn = StyledButton(self, text="Обновить список", command=self.load_users)
        self.refresh_btn.pack(pady=10)

        self.load_users()

    def load_users(self):
        for widget in self.users_frame.winfo_children():
            widget.destroy()

        users = get_all_users()
        for u in users:
            uid, uname, fname, lname, cls, role, blocked, lvl, xp, bytes_val, house = u
            card = CardFrame(self.users_frame)
            card.pack(fill="x", pady=5, padx=10)

            info = f"{fname} {lname} (@{uname}) | Класс: {cls} | Роль: {role} | Ур.{lvl} XP:{xp} 💰{bytes_val}"
            if blocked:
                info += " | ❌ ЗАБЛОКИРОВАН"
            StyledLabel(card, text=info, font=("Noto Sans Condensed", 13, "bold")).pack(anchor="w", padx=10, pady=5)

            btn_frame = StyledFrame(card)
            btn_frame.pack(fill="x", padx=10, pady=5)

            # Смена роли
            role_var = ctk.StringVar(value=role)
            role_menu = ctk.CTkOptionMenu(btn_frame, values=["student", "teacher", "admin", "author"],
                                          variable=role_var, width=100,
                                          fg_color=cfg.BTN_COLOR, text_color=cfg.TEXT_COLOR)
            role_menu.pack(side="left", padx=5)
            StyledButton(btn_frame, text="Сменить роль",
                         command=lambda uid=uid, rv=role_var: self.change_role(uid, rv.get()),
                         width=120).pack(side="left", padx=5)

            # Блокировка/разблокировка
            block_text = "Разблокировать" if blocked else "Заблокировать"
            StyledButton(btn_frame, text=block_text,
                         command=lambda uid=uid: self.toggle_block(uid),
                         width=130).pack(side="left", padx=5)

            # Удаление
            StyledButton(btn_frame, text="Удалить", fg_color="#d9534f",
                         command=lambda uid=uid: self.delete_user(uid),
                         width=100).pack(side="left", padx=5)

    def change_role(self, user_id, new_role):
        if messagebox.askyesno("Подтверждение", f"Изменить роль пользователя на {new_role}?"):
            update_user_role(user_id, new_role)
            self.load_users()

    def toggle_block(self, user_id):
        toggle_block_user(user_id)
        self.load_users()

    def delete_user(self, user_id):
        if messagebox.askyesno("Удаление", "Вы уверены, что хотите безвозвратно удалить этого пользователя?"):
            delete_user(user_id)
            self.load_users()
