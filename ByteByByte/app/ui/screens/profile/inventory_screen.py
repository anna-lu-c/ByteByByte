# inventory_screen.py
import customtkinter as ctk
from tkinter import messagebox
import app.core.config as cfg
from app.ui.widgets.buttons import StyledButton
from app.ui.widgets.cards import StyledLabel, CardFrame
from app.core.database import get_user_gamification, update_user_gamification
from app.core.constants import SHOP_ITEMS


class ShopFrame(ctk.CTkFrame):
    def __init__(self, master, dashboard, **kwargs):
        super().__init__(master, fg_color=cfg.BG_COLOR, **kwargs)
        self.dashboard = dashboard
        self.user_id = dashboard.user_id
        self.gamification = get_user_gamification(self.user_id)
        self.bytes_amt = self.gamification.get("bytes", 0)
        self.titles = self.gamification.get("titles", [])
        self.items_purchased = self.gamification.get("items_purchased", 0)
        self.achievements = self.gamification.get("achievements", [])

        StyledButton(self, text="← Назад", command=self.dashboard.restore_center,
                     width=100).pack(anchor="nw", padx=20, pady=15)

        StyledLabel(self, text="🛒 Магазин", font=("Noto Sans Condensed", 26, "bold")).pack(pady=15)

        # Баланс
        self.balance_label = StyledLabel(self, text=f"💰 Ваш баланс: {self.bytes_amt} байтов",
                                         font=("Noto Sans Condensed", 16, "bold"))
        self.balance_label.pack(pady=5)

        scroll = ctk.CTkScrollableFrame(self, fg_color=cfg.BG_COLOR)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        # Отображение товаров
        for item in SHOP_ITEMS:
            owned = False
            if item["type"] == "title":
                owned = item["value"] in self.titles
            elif item["type"] == "frame":
                # пока заглушка для рамок
                owned = False
            elif item["type"] == "booster":
                owned = False  # бустеры не хранятся как постоянные

            card = CardFrame(scroll)
            card.pack(fill="x", pady=5, padx=10)

            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=5)

            StyledLabel(row, text=item.get("icon", "🛍️"), font=("Noto Sans Condensed", 24)).pack(side="left", padx=5)
            StyledLabel(row, text=item["name"], font=("Noto Sans Condensed", 16, "bold")).pack(side="left", padx=5)
            StyledLabel(row, text=item["description"], font=("Noto Sans Condensed", 12),
                        wraplength=300, justify="left").pack(side="left", padx=10)

            if owned:
                StyledLabel(row, text="✅ Куплено", text_color=cfg.SUCCESS_COLOR,
                            font=("Noto Sans Condensed", 13, "bold")).pack(side="right", padx=10)
            else:
                btn_text = f"Купить за {item['cost']}"
                StyledButton(row, text=btn_text,
                             command=lambda i=item: self.buy_item(i),
                             width=140).pack(side="right", padx=10)

    def buy_item(self, item):
        if self.bytes_amt < item["cost"]:
            messagebox.showwarning("Недостаточно байтов", "У вас не хватает байтов для этой покупки.")
            return

        # Проверка на уже купленное
        if item["type"] == "title":
            if item["value"] in self.titles:
                messagebox.showinfo("Уже куплено", "У вас уже есть этот титул.")
                return
            self.titles.append(item["value"])
            update_user_gamification(self.user_id, titles=self.titles)

        elif item["type"] == "frame":
            # Заглушка для рамок — можно будет хранить в поле items или отдельной таблице
            # Пока просто учтём покупку, увеличив счётчик
            self.items_purchased += 1
            update_user_gamification(self.user_id, items_purchased=self.items_purchased)
            messagebox.showinfo("Покупка", f"Рамка '{item['name']}' куплена! Примените её в профиле.")

        elif item["type"] == "booster":
            # Бустеры активируются сразу? Пока просто заглушка с сообщением
            messagebox.showinfo("Покупка", f"Бустер '{item['name']}' активирован на 1 час!")
            # В реальности нужно записать время активации

        # Списываем байты
        self.bytes_amt -= item["cost"]
        update_user_gamification(self.user_id, bytes=self.bytes_amt)
        self.balance_label.configure(text=f"💰 Ваш баланс: {self.bytes_amt} байтов")

        # Обновить экран, чтобы кнопки изменились
        self.refresh_shop()

    def refresh_shop(self):
        # Простейший способ: пересоздать экран
        self.dashboard.master.show_screen(ShopFrame, dashboard=self.dashboard)
