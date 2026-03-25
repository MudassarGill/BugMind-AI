"""
BugMind AI — SQLite Database Setup
Creates tables for users, code_history, and learning_stats.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "bugmind.db")


def get_db():
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Initialize database tables."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS code_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            language TEXT DEFAULT 'python',
            output TEXT,
            error_type TEXT,
            error_message TEXT,
            ai_explanation TEXT,
            ai_fix TEXT,
            is_error INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS learning_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            total_runs INTEGER DEFAULT 0,
            total_errors INTEGER DEFAULT 0,
            total_fixes INTEGER DEFAULT 0,
            type_errors INTEGER DEFAULT 0,
            syntax_errors INTEGER DEFAULT 0,
            name_errors INTEGER DEFAULT 0,
            value_errors INTEGER DEFAULT 0,
            index_errors INTEGER DEFAULT 0,
            other_errors INTEGER DEFAULT 0,
            streak_days INTEGER DEFAULT 0,
            last_active TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE INDEX IF NOT EXISTS idx_code_history_user ON code_history(user_id);
        CREATE INDEX IF NOT EXISTS idx_code_history_error ON code_history(is_error);
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")


# --- Helper Functions ---

def create_user(name: str, email: str, password_hash: str) -> dict:
    conn = get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash)
        )
        user_id = cursor.lastrowid
        # Create initial learning stats
        conn.execute(
            "INSERT INTO learning_stats (user_id) VALUES (?)", (user_id,)
        )
        conn.commit()
        return {"id": user_id, "name": name, "email": email}
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def get_user_by_email(email: str) -> dict:
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def save_code_run(user_id: int, code: str, language: str, output: str,
                  error_type: str = None, error_message: str = None,
                  ai_explanation: str = None, ai_fix: str = None,
                  is_error: bool = False) -> int:
    conn = get_db()
    cursor = conn.execute(
        """INSERT INTO code_history 
           (user_id, code, language, output, error_type, error_message, 
            ai_explanation, ai_fix, is_error)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, code, language, output, error_type, error_message,
         ai_explanation, ai_fix, int(is_error))
    )
    run_id = cursor.lastrowid

    # Update learning stats
    conn.execute(
        "UPDATE learning_stats SET total_runs = total_runs + 1, last_active = datetime('now'), updated_at = datetime('now') WHERE user_id = ?",
        (user_id,)
    )
    if is_error and error_type:
        error_col = _get_error_column(error_type)
        conn.execute(
            f"UPDATE learning_stats SET total_errors = total_errors + 1, {error_col} = {error_col} + 1 WHERE user_id = ?",
            (user_id,)
        )
    conn.commit()
    conn.close()
    return run_id


def increment_fixes(user_id: int):
    conn = get_db()
    conn.execute(
        "UPDATE learning_stats SET total_fixes = total_fixes + 1, updated_at = datetime('now') WHERE user_id = ?",
        (user_id,)
    )
    conn.commit()
    conn.close()


def get_user_stats(user_id: int) -> dict:
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM learning_stats WHERE user_id = ?", (user_id,)
    ).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def get_code_history(user_id: int, limit: int = 20) -> list:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM code_history WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_recent_errors(user_id: int, limit: int = 10) -> list:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM code_history WHERE user_id = ? AND is_error = 1 ORDER BY created_at DESC LIMIT ?",
        (user_id, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _get_error_column(error_type: str) -> str:
    mapping = {
        "TypeError": "type_errors",
        "SyntaxError": "syntax_errors",
        "NameError": "name_errors",
        "ValueError": "value_errors",
        "IndexError": "index_errors",
    }
    return mapping.get(error_type, "other_errors")


if __name__ == "__main__":
    init_db()
