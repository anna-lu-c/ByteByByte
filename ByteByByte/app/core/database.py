# database.py
import sqlite3
import json
import os
import secrets
from app.core.config import DB_PATH, LAST_USER_FILE

def _add_column_if_not_exists(cur, table, column, col_type):
    """Добавляет колонку в таблицу, если её ещё нет."""
    cur.execute(f"PRAGMA table_info({table})")
    existing = [col[1] for col in cur.fetchall()]
    if column not in existing:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Таблица users (основные поля)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            first_name TEXT DEFAULT '',
            last_name TEXT DEFAULT '',
            class_name TEXT DEFAULT '',
            onboarding_shown INTEGER DEFAULT 0
        )
    """)

    # Добавляем недостающие колонки (для обратной совместимости)
    for col, col_type in [
        ('first_name', 'TEXT DEFAULT ""'),
        ('last_name', 'TEXT DEFAULT ""'),
        ('class_name', 'TEXT DEFAULT ""'),
        ('onboarding_shown', 'INTEGER DEFAULT 0')
    ]:
        _add_column_if_not_exists(cur, 'users', col, col_type)

    # Роль и блокировка
    _add_column_if_not_exists(cur, 'users', 'role', 'TEXT DEFAULT "student"')
    _add_column_if_not_exists(cur, 'users', 'blocked', 'INTEGER DEFAULT 0')

    # --- Геймификация ---
    gamification_columns = [
        ('level', 'INTEGER DEFAULT 1'),
        ('xp', 'INTEGER DEFAULT 0'),
        ('bytes', 'INTEGER DEFAULT 500'),
        ('house', 'TEXT DEFAULT ""'),
        ('titles', 'TEXT DEFAULT "[]"'),
        ('achievements', 'TEXT DEFAULT "[]"'),
        ('items_purchased', 'INTEGER DEFAULT 0'),
        ('theme', 'TEXT DEFAULT "light"')
    ]
    for col, col_type in gamification_columns:
        _add_column_if_not_exists(cur, 'users', col, col_type)

    # Таблица прогресса
    cur.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            user_id INTEGER,
            task_number INTEGER,
            progress_value REAL DEFAULT 0.0,
            PRIMARY KEY (user_id, task_number),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Таблица истории экзаменов
    cur.execute("""
        CREATE TABLE IF NOT EXISTS exam_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            score INTEGER,
            total INTEGER,
            duration INTEGER,
            details TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Таблица лога экспорта
    cur.execute("""
        CREATE TABLE IF NOT EXISTS export_log (
            user_id INTEGER PRIMARY KEY,
            last_export_date TIMESTAMP,
            previous_report_hash TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # --- Новые таблицы: классы, тесты, новеллы ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            teacher_id INTEGER NOT NULL,
            invite_code TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS class_members (
            class_id INTEGER,
            user_id INTEGER,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (class_id, user_id),
            FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS teacher_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER,
            teacher_id INTEGER,
            title TEXT,
            tasks TEXT,
            time_limit INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
            FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS test_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_id INTEGER,
            student_id INTEGER,
            answers TEXT,
            score INTEGER,
            finished INTEGER DEFAULT 0,
            started_at TIMESTAMP,
            finished_at TIMESTAMP,
            FOREIGN KEY (test_id) REFERENCES teacher_tests(id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS class_novellas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER,
            teacher_id INTEGER,
            chapter_number INTEGER,
            title TEXT,
            content TEXT,
            case_text TEXT,
            case_answer TEXT,
            required_tasks TEXT,
            reward_xp INTEGER DEFAULT 30,
            reward_bytes INTEGER DEFAULT 20,
            FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
            FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_novella_progress (
            user_id INTEGER,
            novella_id INTEGER,
            chapter_id INTEGER,
            read INTEGER DEFAULT 0,
            case_solved INTEGER DEFAULT 0,
            tasks_done TEXT,
            completed INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, novella_id, chapter_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (novella_id) REFERENCES class_novellas(id) ON DELETE CASCADE
        )
    """)

    conn.commit()

    # Создаём учётную запись автора, если её нет
    cur.execute("SELECT id FROM users WHERE username = 'ariannev'")
    if not cur.fetchone():
        cur.execute("INSERT INTO users (username, password, first_name, last_name, class_name, role, blocked) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    ('ariannev', 'thelong2004', 'Анна', 'Лукина', 'author', 'author', 0))
        author_id = cur.lastrowid
        for task_num in range(1, 28):
            cur.execute("INSERT OR IGNORE INTO progress (user_id, task_number, progress_value) VALUES (?, ?, 0.0)",
                        (author_id, task_num))
        cur.execute("UPDATE users SET level=1, xp=0, bytes=0, house='' WHERE id=?", (author_id,))
        conn.commit()

    conn.close()

# ---------- Базовые функции пользователя ----------
def register_user(username, password, first_name, last_name, class_name):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO users (username, password, first_name, last_name, class_name)
            VALUES (?, ?, ?, ?, ?)
        """, (username, password, first_name, last_name, class_name))
        user_id = cur.lastrowid
        conn.commit()
        for task_num in range(1, 28):
            cur.execute("INSERT OR IGNORE INTO progress (user_id, task_number, progress_value) VALUES (?, ?, 0.0)",
                        (user_id, task_num))
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def login_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, first_name, last_name, class_name, onboarding_shown FROM users WHERE username = ? AND password = ?",
                (username, password))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0], row[1], row[2], row[3], bool(row[4])
    return None, None, None, None, False

def set_onboarding_shown(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE users SET onboarding_shown = 1 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

def load_progress(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT task_number, progress_value FROM progress WHERE user_id = ?", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}

def save_progress(user_id, task_num, value):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE progress SET progress_value = ? WHERE user_id = ? AND task_number = ?",
                (value, user_id, task_num))
    conn.commit()
    conn.close()

def reset_user_data(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE progress SET progress_value = 0.0 WHERE user_id = ?", (user_id,))
    cur.execute("DELETE FROM exam_history WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def save_exam_result(user_id, score, total, duration, details):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO exam_history (user_id, score, total, duration, details) VALUES (?, ?, ?, ?, ?)",
        (user_id, score, total, duration, json.dumps(details))
    )
    conn.commit()
    conn.close()

def load_exam_history(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, date, score, total, duration, details FROM exam_history WHERE user_id = ? ORDER BY date DESC",
                (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def save_last_user(username):
    with open(LAST_USER_FILE, "w", encoding="utf-8") as f:
        f.write(username)

def load_last_user():
    if os.path.exists(LAST_USER_FILE):
        with open(LAST_USER_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None

def clear_last_user():
    if os.path.exists(LAST_USER_FILE):
        os.remove(LAST_USER_FILE)

# ---------- Геймификация ----------
def get_user_gamification(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT level, xp, bytes, house, titles, achievements, items_purchased, theme
        FROM users WHERE id = ?
    """, (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {
            "level": row[0],
            "xp": row[1],
            "bytes": row[2],
            "house": row[3] or "",
            "titles": json.loads(row[4]) if row[4] else [],
            "achievements": json.loads(row[5]) if row[5] else [],
            "items_purchased": row[6],
            "theme": row[7] or "light"
        }
    return {"level": 1, "xp": 0, "bytes": 500, "house": "", "titles": [], "achievements": [], "items_purchased": 0, "theme": "light"}

def update_user_gamification(user_id, **kwargs):
    allowed = ['level', 'xp', 'bytes', 'house', 'titles', 'achievements', 'items_purchased', 'theme']
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return
    if 'titles' in updates:
        updates['titles'] = json.dumps(updates['titles'], ensure_ascii=False)
    if 'achievements' in updates:
        updates['achievements'] = json.dumps(updates['achievements'], ensure_ascii=False)
    set_clause = ", ".join([f"{k}=?" for k in updates])
    values = list(updates.values()) + [user_id]
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"UPDATE users SET {set_clause} WHERE id=?", values)
    conn.commit()
    conn.close()

# ---------- Роли и администрирование ----------
def get_user_role(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT role FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 'student'

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, username, first_name, last_name, class_name, role, blocked, level, xp, bytes, house FROM users ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows

def update_user_role(user_id, new_role):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE users SET role=? WHERE id=?", (new_role, user_id))
    conn.commit()
    conn.close()

def toggle_block_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT blocked FROM users WHERE id=?", (user_id,))
    row = cur.fetchone()
    if row:
        new_status = 0 if row[0] else 1
        cur.execute("UPDATE users SET blocked=? WHERE id=?", (new_status, user_id))
        conn.commit()
    conn.close()

def delete_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM progress WHERE user_id=?", (user_id,))
    cur.execute("DELETE FROM exam_history WHERE user_id=?", (user_id,))
    cur.execute("DELETE FROM class_members WHERE user_id=?", (user_id,))
    cur.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

# ---------- Классы (гильдии) ----------
def create_class(teacher_id, name):
    code = secrets.token_hex(4).upper()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO classes (name, teacher_id, invite_code) VALUES (?, ?, ?)",
                (name, teacher_id, code))
    conn.commit()
    class_id = cur.lastrowid
    conn.close()
    return class_id, code

def join_class(user_id, invite_code):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id FROM classes WHERE invite_code = ?", (invite_code,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return False, "Класс не найден"
    class_id = row[0]
    try:
        cur.execute("INSERT INTO class_members (class_id, user_id) VALUES (?, ?)", (class_id, user_id))
        conn.commit()
        return True, "Вы присоединились к классу"
    except sqlite3.IntegrityError:
        return False, "Вы уже состоите в этом классе"
    finally:
        conn.close()

def get_teacher_classes(teacher_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, name, invite_code FROM classes WHERE teacher_id = ?", (teacher_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_class_members(class_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT u.id, u.username, u.first_name, u.last_name, u.level, u.xp
        FROM class_members cm
        JOIN users u ON cm.user_id = u.id
        WHERE cm.class_id = ?
    """, (class_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_user_class(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT c.id, c.name, c.teacher_id
        FROM classes c
        JOIN class_members cm ON c.id = cm.class_id
        WHERE cm.user_id = ?
    """, (user_id,))
    row = cur.fetchone()
    conn.close()
    return row  # (class_id, name, teacher_id) или None

# ---------- Тесты учителя ----------
def create_teacher_test(teacher_id, class_id, title, tasks, time_limit):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO teacher_tests (class_id, teacher_id, title, tasks, time_limit) VALUES (?,?,?,?,?)",
                (class_id, teacher_id, title, json.dumps(tasks), time_limit))
    conn.commit()
    test_id = cur.lastrowid
    conn.close()
    return test_id

def get_class_tests(class_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, title, tasks, time_limit FROM teacher_tests WHERE class_id = ? ORDER BY created_at DESC", (class_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def assign_test_to_students(test_id, class_id, student_ids=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if student_ids is None:
        cur.execute("SELECT user_id FROM class_members WHERE class_id = ?", (class_id,))
        student_ids = [row[0] for row in cur.fetchall()]
    for sid in student_ids:
        cur.execute("INSERT OR IGNORE INTO test_assignments (test_id, student_id) VALUES (?,?)",
                    (test_id, sid))
    conn.commit()
    conn.close()

def get_student_tests(student_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT ta.id, tt.title, tt.tasks, tt.time_limit, ta.finished, ta.score
        FROM test_assignments ta
        JOIN teacher_tests tt ON ta.test_id = tt.id
        WHERE ta.student_id = ? AND ta.finished = 0
        ORDER BY tt.created_at DESC
    """, (student_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def start_test_assignment(assignment_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE test_assignments SET started_at = datetime('now') WHERE id = ?", (assignment_id,))
    conn.commit()
    conn.close()

def save_test_answers(assignment_id, answers, score, finished=True):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE test_assignments SET answers=?, score=?, finished=?, finished_at=datetime('now') WHERE id=?",
                (json.dumps(answers), score, 1 if finished else 0, assignment_id))
    conn.commit()
    conn.close()

def get_test_assignments(test_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT ta.id, u.first_name, u.last_name, ta.score, ta.finished
        FROM test_assignments ta
        JOIN users u ON ta.student_id = u.id
        WHERE ta.test_id = ?
    """, (test_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_student_completed_tests(student_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT ta.id, tt.title, tt.tasks, ta.score, ta.finished_at
        FROM test_assignments ta
        JOIN teacher_tests tt ON ta.test_id = tt.id
        WHERE ta.student_id = ? AND ta.finished = 1
        ORDER BY ta.finished_at DESC
    """, (student_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def delete_teacher_test(test_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM test_assignments WHERE test_id=?", (test_id,))
    cur.execute("DELETE FROM teacher_tests WHERE id=?", (test_id,))
    conn.commit()
    conn.close()

# ---------- Новеллы (заглушки) ----------
def create_novella_chapter(teacher_id, class_id, chapter_number, title, content, case_text, case_answer, required_tasks):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""INSERT INTO class_novellas (class_id, teacher_id, chapter_number, title, content, case_text, case_answer, required_tasks)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (class_id, teacher_id, chapter_number, title, content, case_text, case_answer, json.dumps(required_tasks)))
    conn.commit()
    novella_id = cur.lastrowid
    conn.close()
    return novella_id

def get_class_novellas(class_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, chapter_number, title FROM class_novellas WHERE class_id = ? ORDER BY chapter_number", (class_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

# ---------- Функции для экрана Домов ----------
def get_house_ranking():
    """Возвращает суммарный XP для каждого дома среди учеников."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT house, SUM(xp) as total_xp
        FROM users
        WHERE role = 'student' AND house IS NOT NULL AND house != ''
        GROUP BY house
        ORDER BY total_xp DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows  # список кортежей (house_name, total_xp)

def get_house_members(house_name, limit=50):
    """Возвращает список учеников указанного дома, отсортированных по XP."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT first_name, last_name, level, xp
        FROM users
        WHERE role = 'student' AND house = ?
        ORDER BY xp DESC
        LIMIT ?
    """, (house_name, limit))
    rows = cur.fetchall()
    conn.close()
    return rows

# Инициализация при импорте
init_db()
