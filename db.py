import sqlite3
from datetime import datetime

DB_PATH = "dashboard.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            due_date TEXT,
            tag TEXT,
            priority TEXT,
            est_min INTEGER,
            status TEXT DEFAULT 'open',
            created_at TEXT DEFAULT (datetime('now'))
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            body_md TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );
        """
    )
    conn.commit()
    return conn

# ---- Task helpers ----
def add_task(title, due_date=None, tag=None, priority="Normal", est_min=None):
    conn = get_conn()
    conn.execute(
        "INSERT INTO tasks(title, due_date, tag, priority, est_min, status) VALUES (?, ?, ?, ?, ?, 'open')",
        (title, due_date, tag, priority, est_min),
    )
    conn.commit()

def list_tasks(include_done=True):
    conn = get_conn()
    if include_done:
        rows = conn.execute("SELECT * FROM tasks ORDER BY COALESCE(due_date, '9999-12-31') ASC, priority DESC").fetchall()
    else:
        rows = conn.execute("SELECT * FROM tasks WHERE status='open' ORDER BY COALESCE(due_date, '9999-12-31') ASC, priority DESC").fetchall()
    return [dict(r) for r in rows]

def update_task_status(task_id, status):
    conn = get_conn()
    conn.execute("UPDATE tasks SET status=? WHERE id=?", (status, task_id))
    conn.commit()

def delete_task(task_id):
    conn = get_conn()
    conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()

# ---- Notes helpers ----
def add_note(title, body_md=""):
    conn = get_conn()
    conn.execute("INSERT INTO notes(title, body_md) VALUES (?, ?)", (title, body_md))
    conn.commit()

def list_notes():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM notes ORDER BY updated_at DESC").fetchall()
    return [dict(r) for r in rows]

def get_note(note_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM notes WHERE id=?", (note_id,)).fetchone()
    return dict(row) if row else None

def update_note(note_id, title, body_md):
    conn = get_conn()
    conn.execute("UPDATE notes SET title=?, body_md=?, updated_at=datetime('now') WHERE id=?", (title, body_md, note_id))
    conn.commit()

def delete_note(note_id):
    conn = get_conn()
    conn.execute("DELETE FROM notes WHERE id=?", (note_id,))
    conn.commit()

# ---- Settings helpers ----
def set_setting(key, value):
    conn = get_conn()
    conn.execute("INSERT INTO settings(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))
    conn.commit()

def get_setting(key, default=None):
    conn = get_conn()
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return row[0] if row else default
