# game_service.py
from app.core.database import get_user_gamification, update_user_gamification, get_user_role
from app.utils.confetti import Confetti
import math

def add_xp(user_id, amount, master=None):
    """Добавляет XP, повышает уровень, начисляет байты за уровень, показывает конфетти (только для студентов)"""
    if get_user_role(user_id) != 'student':
        return None, 0

    data = get_user_gamification(user_id)
    new_xp = data["xp"] + amount
    level = data["level"]
    xp_to_next = 100 * level   # формула: для перехода с level на level+1 нужно level*100 XP
    bytes_earned = 0
    leveled_up = False
    while new_xp >= xp_to_next:
        new_xp -= xp_to_next
        level += 1
        xp_to_next = 100 * level
        bytes_earned += 50
        leveled_up = True
    if leveled_up and master:
        Confetti(master)
    update_user_gamification(user_id, xp=new_xp, level=level, bytes=data["bytes"]+bytes_earned)
    if leveled_up:
        return level, bytes_earned
    return None, 0

def add_bytes(user_id, amount):
    """Добавляет байты (только для студентов)"""
    if get_user_role(user_id) != 'student':
        return
    data = get_user_gamification(user_id)
    update_user_gamification(user_id, bytes=data["bytes"]+amount)

def get_level(xp):
    if xp <= 0:
        return 1
    level = 1
    need = 100
    while xp >= need:
        xp -= need
        level += 1
        need = 100 * level
    return level

def check_daily_bonus(user_id):
    # заглушка
    pass
