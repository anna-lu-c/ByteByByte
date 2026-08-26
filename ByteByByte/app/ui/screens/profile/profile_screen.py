# profile_screen.py
import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import os
import sys
from datetime import datetime
import hashlib

import app.core.config as cfg
from app.ui.widgets.buttons import StyledButton
from app.ui.widgets.cards import StyledLabel, StyledFrame, CardFrame
from app.core.database import (
    load_progress, load_exam_history,
    reset_user_data, clear_last_user, get_user_gamification
)
from app.core.constants import TASK_NAMES, TOTAL_TASKS, HOUSES, ACHIEVEMENTS


class ProfileFrame(ctk.CTkFrame):
    def __init__(self, master, dashboard, **kwargs):
        super().__init__(master, fg_color=cfg.BG_COLOR, **kwargs)
        self.dashboard = dashboard
        self.user_id = dashboard.user_id
        self.gamification = get_user_gamification(self.user_id)

        StyledButton(self, text="← Назад", command=self.dashboard.restore_center,
                     width=100).pack(anchor="nw", padx=20, pady=15)

        scroll = ctk.CTkScrollableFrame(self, fg_color=cfg.BG_COLOR)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        d = self.dashboard

        # === Карточка профиля с аватаром и рамкой ===
        card_profile = CardFrame(scroll)
        card_profile.pack(fill="x", pady=10)

        # Горизонтальный блок: аватар, имя, рамка
        profile_header = StyledFrame(card_profile)
        profile_header.pack(fill="x", padx=15, pady=10)

        # Аватар (заглушка, в будущем можно менять)
        avatar_frame = StyledFrame(profile_header)
        avatar_frame.pack(side="left", padx=(0, 15))
        self.avatar_label = StyledLabel(avatar_frame, text="👤", font=("Noto Sans Condensed", 48))
        self.avatar_label.pack()
        # Рамка вокруг аватара (заглушка)
        self.frame_label = StyledLabel(avatar_frame, text="┅┅┅┅┅", font=("Noto Sans Condensed", 10),
                                       text_color=cfg.COLORS[cfg.current_theme]["muted_fg"])
        self.frame_label.pack()

        # Информация о пользователе
        info_frame = StyledFrame(profile_header)
        info_frame.pack(side="left", fill="both", expand=True)

        StyledLabel(info_frame, text=f"{d.first_name} {d.last_name}",
                    font=("Noto Sans Condensed", 20, "bold")).pack(anchor="w")
        StyledLabel(info_frame, text=f"Логин: @{d.username}",
                    font=("Noto Sans Condensed", 14)).pack(anchor="w")
        StyledLabel(info_frame, text=f"Класс: {d.class_name}",
                    font=("Noto Sans Condensed", 14)).pack(anchor="w")

        # Титулы и дом
        titles = self.gamification.get('titles', [])
        titles_text = ", ".join(titles) if titles else "Нет"
        StyledLabel(info_frame, text=f"Титулы: {titles_text}",
                    font=("Noto Sans Condensed", 13, "italic")).pack(anchor="w")

        house_name = self.gamification.get('house', '') or "Не выбран"
        house_color = cfg.COLORS[cfg.current_theme]["muted_fg"]
        for house in HOUSES:
            if house['name'] == self.gamification['house']:
                house_color = house['color']
                break
        StyledLabel(info_frame, text=f"Дом: {house_name}",
                    font=("Noto Sans Condensed", 14, "bold"), text_color=house_color).pack(anchor="w")

        # Кнопки быстрого доступа: сменить аватар, рамку, магазин, достижения
        quick_frame = StyledFrame(card_profile)
        quick_frame.pack(fill="x", padx=15, pady=(0, 10))
        StyledButton(quick_frame, text="🖼️ Сменить аватар",
                     command=self.change_avatar, width=150).pack(side="left", padx=5)
        StyledButton(quick_frame, text="🖼️ Сменить рамку",
                     command=self.change_frame, width=150).pack(side="left", padx=5)
        StyledButton(quick_frame, text="🛒 Магазин",
                     command=self.open_shop, width=120).pack(side="left", padx=5)
        StyledButton(quick_frame, text="🏆 Достижения",
                     command=self.open_achievements, width=120).pack(side="left", padx=5)

        # === Карточка игровой статистики ===
        card_stats = CardFrame(scroll)
        card_stats.pack(fill="x", pady=10)

        StyledLabel(card_stats, text="📊 Игровая статистика",
                    font=("Noto Sans Condensed", 18, "bold")).pack(anchor="w", padx=15, pady=5)

        stats_frame = StyledFrame(card_stats)
        stats_frame.pack(fill="x", padx=15, pady=5)

        StyledLabel(stats_frame, text=f"Уровень: {self.gamification['level']}",
                    font=("Noto Sans Condensed", 14)).pack(anchor="w", pady=2)
        StyledLabel(stats_frame, text=f"Опыт (XP): {self.gamification['xp']} / {self.gamification['level'] * 100}",
                    font=("Noto Sans Condensed", 14)).pack(anchor="w", pady=2)
        StyledLabel(stats_frame, text=f"Байты: {self.gamification['bytes']}",
                    font=("Noto Sans Condensed", 14)).pack(anchor="w", pady=2)

        # Достижения (краткий список разблокированных)
        unlocked_achievements = [a['name'] for a in ACHIEVEMENTS if a['id'] in self.gamification['achievements']]
        ach_str = ", ".join(unlocked_achievements) if unlocked_achievements else "Нет"
        StyledLabel(stats_frame, text=f"Достижения: {ach_str}",
                    font=("Noto Sans Condensed", 13), wraplength=400).pack(anchor="w", pady=2)

        # === Карточка с действиями ===
        card_actions = CardFrame(scroll)
        card_actions.pack(fill="x", pady=10)

        StyledLabel(card_actions, text="⚙️ Управление аккаунтом",
                    font=("Noto Sans Condensed", 18, "bold")).pack(anchor="w", padx=15, pady=5)

        actions_frame = StyledFrame(card_actions)
        actions_frame.pack(fill="x", padx=15, pady=10)

        StyledButton(actions_frame, text="📄 Экспорт аналитики",
                     command=self.export_analytics, width=220).pack(pady=5)
        StyledButton(actions_frame, text="🔄 Сбросить прогресс",
                     command=self.confirm_reset_user_data, width=220).pack(pady=5)
        StyledButton(actions_frame, text="🗑️ Удалить аккаунт",
                     command=self.confirm_delete_account, width=220).pack(pady=5)
        StyledButton(actions_frame, text="🚪 Выйти из аккаунта",
                     command=self.logout, width=220).pack(pady=5)

    # ---------- Методы-заглушки для смены аватара/рамки ----------
    def change_avatar(self):
        # В будущем: открыть окно выбора из купленных иконок
        messagebox.showinfo("Смена аватара", "Выбор иконки будет доступен в магазине после покупки.")

    def change_frame(self):
        # В будущем: открыть окно выбора рамки из купленных
        messagebox.showinfo("Смена рамки", "Выбор рамки будет доступен в магазине после покупки.")

    def open_shop(self):
        from app.ui.screens.profile.inventory_screen import ShopFrame
        self.dashboard.master.show_screen(ShopFrame, dashboard=self.dashboard)

    def open_achievements(self):
        from app.ui.screens.profile.achievements_screen import AchievementsFrame
        self.dashboard.master.show_screen(AchievementsFrame, dashboard=self.dashboard)

    # ---------- действия ----------
    def confirm_reset_user_data(self):
        d = self.dashboard
        if messagebox.askyesno("Сброс данных аккаунта",
                               f"Удалить весь прогресс и историю пользователя '{d.username}'?\n"
                               "Игровые показатели (уровень, XP, байты) останутся без изменений."):
            reset_user_data(d.user_id)
            messagebox.showinfo("Готово", "Прогресс и история экзаменов сброшены.")

    def confirm_delete_account(self):
        d = self.dashboard
        if messagebox.askyesno("Удаление аккаунта",
                               f"Полностью удалить аккаунт '{d.username}'?\nЭто действие необратимо."):
            conn = sqlite3.connect(cfg.DB_PATH)
            conn.execute("DELETE FROM users WHERE id = ?", (d.user_id,))
            conn.commit()
            conn.close()
            clear_last_user()
            messagebox.showinfo("Аккаунт удалён", "Приложение будет закрыто.")
            self.dashboard.master.destroy()
            sys.exit()

    def export_analytics(self):
        d = self.dashboard
        os.makedirs(cfg.EXPORTS_DIR, exist_ok=True)
        progress = load_progress(d.user_id)
        history = load_exam_history(d.user_id)

        report_lines = [
            f"Отчёт по ученику: {d.first_name} {d.last_name}",
            f"Класс: {d.class_name}",
            f"Логин: {d.username}",
            f"Уровень: {self.gamification['level']}",
            f"XP: {self.gamification['xp']}",
            f"Байты: {self.gamification['bytes']}",
            f"Дом: {self.gamification['house'] or 'Не выбран'}",
            f"Титулы: {', '.join(self.gamification['titles']) if self.gamification['titles'] else 'Нет'}",
            f"Дата генерации: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\n" + "=" * 50,
            "ПРОГРЕСС ПО ЗАДАНИЯМ:"
        ]
        for task in range(1, TOTAL_TASKS + 1):
            percent = int(progress.get(task, 0.0) * 100)
            report_lines.append(f"Задание {task:2d} ({TASK_NAMES.get(task, '')[:25]}): {percent:3d}%")
        report_lines.append("\n" + "=" * 50)
        report_lines.append("ИСТОРИЯ ЭКЗАМЕНОВ:")
        if history:
            for idx, rec in enumerate(history, 1):
                date_str = rec[1]
                score, total, duration = rec[2], rec[3], rec[4]
                percent = (score / total) * 100 if total else 0
                report_lines.append(
                    f"{idx}. {date_str} | Баллы: {score}/{total} ({percent:.1f}%) | Время: {duration // 60} мин {duration % 60} сек")
        else:
            report_lines.append("Экзамены не проводились.")

        report_text = "\n".join(report_lines)
        current_hash = hashlib.md5(report_text.encode('utf-8')).hexdigest()

        conn = sqlite3.connect(cfg.DB_PATH)
        row = conn.execute("SELECT last_export_date, previous_report_hash FROM export_log WHERE user_id = ?",
                           (d.user_id,)).fetchone()
        last_hash = row[1] if row else None
        if last_hash == current_hash:
            messagebox.showinfo("Экспорт", "Данные не изменились. Отчёт не сохранён.")
            conn.close()
            return

        filename = f"analytics_{d.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(cfg.EXPORTS_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report_text)

        if row:
            conn.execute("UPDATE export_log SET last_export_date=?, previous_report_hash=? WHERE user_id=?",
                         (datetime.now().isoformat(), current_hash, d.user_id))
        else:
            conn.execute("INSERT INTO export_log (user_id, last_export_date, previous_report_hash) VALUES (?, ?, ?)",
                         (d.user_id, datetime.now().isoformat(), current_hash))
        conn.commit()
        conn.close()
        messagebox.showinfo("Экспорт", f"Отчёт сохранён в файл:\n{filepath}")

    def logout(self):
        clear_last_user()
        from app.ui.screens.auth.login_screen import LoginScreen
        self.dashboard.master.show_screen(LoginScreen)
