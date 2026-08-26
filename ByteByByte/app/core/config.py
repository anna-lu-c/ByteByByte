# config.py
import os
import sys
import customtkinter as ctk

# ---------- Определение базовой директории ----------
if getattr(sys, 'frozen', False):
    # Упакованное приложение
    BASE_DIR = sys._MEIPASS
else:
    # Режим разработки: поднимаемся на два уровня вверх от app/core/config.py
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

def resource_path(relative_path):
    """Возвращает абсолютный путь к ресурсу, работая и в dev-режиме, и в собранном .exe."""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = BASE_DIR
    return os.path.join(base_path, relative_path)

# ---------- Директории ресурсов (неизменяемые) ----------
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")
os.makedirs(RESOURCES_DIR, exist_ok=True)

TASKS_DIR = os.path.join(RESOURCES_DIR, "tasks")
IMAGES_DIR = os.path.join(RESOURCES_DIR, "images")
FILES_DIR = os.path.join(RESOURCES_DIR, "files")
THEORY_DIR = os.path.join(RESOURCES_DIR, "theory")
FONTS_DIR = os.path.join(RESOURCES_DIR, "fonts")
ICONS_DIR = os.path.join(RESOURCES_DIR, "icons")

# Создаём все ресурсные папки
for d in [TASKS_DIR, IMAGES_DIR, FILES_DIR, THEORY_DIR, FONTS_DIR, ICONS_DIR]:
    os.makedirs(d, exist_ok=True)

# ---------- Директории пользовательских данных (изменяемые) ----------
USER_DATA_DIR = os.path.join(BASE_DIR, "user_data")
os.makedirs(USER_DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(USER_DATA_DIR, "progress.db")
LAST_USER_FILE = os.path.join(USER_DATA_DIR, "last_user.txt")
EXPORTS_DIR = os.path.join(USER_DATA_DIR, "exports")
CACHE_DIR = os.path.join(USER_DATA_DIR, "cache")

os.makedirs(EXPORTS_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# ---------- Логи ----------
LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# ---------- Шрифты (Noto Sans Condensed) ----------
FONT_REGULAR_PATH = os.path.join(FONTS_DIR, "NotoSans_Condensed-Regular.ttf")
FONT_BOLD_PATH = os.path.join(FONTS_DIR, "NotoSans_Condensed-Bold.ttf")
FONT_ITALIC_PATH = os.path.join(FONTS_DIR, "NotoSans_Condensed-Italic.ttf")

FONT_REGULAR = ("Noto Sans Condensed", 14)
FONT_BOLD = ("Noto Sans Condensed", 14, "bold")
FONT_ITALIC = ("Noto Sans Condensed", 14, "italic")

def load_app_fonts():
    """Загружает шрифты в CustomTkinter. Вызовите до создания любых виджетов."""
    for path in (FONT_REGULAR_PATH, FONT_BOLD_PATH, FONT_ITALIC_PATH):
        if os.path.exists(path):
            ctk.FontManager.load_font(path)

# ---------- Цветовые схемы ----------
COLORS = {
    "light": {
        "bg": "#ffffff", "fg": "#0a0a0a", "card": "#ffffff", "card_fg": "#0a0a0a",
        "primary": "#10b981", "primary_fg": "#ffffff", "secondary": "#f3f4f6",
        "muted": "#ececf0", "muted_fg": "#717182", "border": "#e5e7eb",
        "level": "#8b5cf6", "bytes": "#f59e0b", "xp": "#3b82f6",
        "success": "#10b981", "error": "#ef4444", "partial": "#f59e0b"
    },
    "dark": {
        "bg": "#0f1419", "fg": "#ededee", "card": "#1a1f2e", "card_fg": "#ededee",
        "primary": "#10b981", "primary_fg": "#ffffff", "secondary": "#2a2e3d",
        "muted": "#252a39", "muted_fg": "#9ca3af", "border": "#2d3243",
        "level": "#a78bfa", "bytes": "#fbbf24", "xp": "#60a5fa",
        "success": "#34d399", "error": "#f87171", "partial": "#fbbf24"
    }
}

# Глобальные переменные текущей темы (будут обновляться через apply_theme)
current_theme = "light"
BG_COLOR = COLORS["light"]["bg"]
TEXT_COLOR = COLORS["light"]["fg"]
BTN_COLOR = COLORS["light"]["primary"]
BTN_HOVER = COLORS["light"]["primary"]
SUCCESS_COLOR = COLORS["light"]["success"]
ERROR_COLOR = COLORS["light"]["error"]
PARTIAL_COLOR = COLORS["light"]["partial"]
TILE_BG = COLORS["light"]["card"]
TILE_BORDER = COLORS["light"]["border"]
TILE_HOVER = COLORS["light"]["secondary"]

def apply_theme(theme):
    global current_theme, BG_COLOR, TEXT_COLOR, BTN_COLOR, BTN_HOVER
    global SUCCESS_COLOR, ERROR_COLOR, PARTIAL_COLOR, TILE_BG, TILE_BORDER, TILE_HOVER
    if theme not in COLORS:
        theme = "light"

    # Переключаем тему самого CustomTkinter
    ctk.set_appearance_mode(theme)

    current_theme = theme
    c = COLORS[theme]
    BG_COLOR = c["bg"]
    TEXT_COLOR = c["fg"]
    BTN_COLOR = c["primary"]
    BTN_HOVER = c["primary"]   # можно будет сделать чуть темнее/светлее
    SUCCESS_COLOR = c["success"]
    ERROR_COLOR = c["error"]
    PARTIAL_COLOR = c["partial"]
    TILE_BG = c["card"]
    TILE_BORDER = c["border"]
    TILE_HOVER = c["secondary"]

# ---------- Настройки экзамена ----------
EXAM_TIME_LIMIT = 235 * 60
TOTAL_TASKS = 27

# ---------- Звук (глобальная настройка) ----------
SOUND_ENABLED = True   # Изменяется из настроек пользователя

# ---------- Supabase (заглушка) ----------
SUPABASE_URL = ""
SUPABASE_ANON_KEY = ""
