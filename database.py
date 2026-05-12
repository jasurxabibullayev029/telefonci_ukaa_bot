import sqlite3
from datetime import datetime
from typing import Optional


class Database:
    def __init__(self, db_path: str = "gamebot.db"):
        self.db_path = db_path

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self._conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id    INTEGER PRIMARY KEY,
                    username   TEXT    DEFAULT '',
                    full_name  TEXT    DEFAULT '',
                    joined_at  TEXT    DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS games (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    name       TEXT    NOT NULL,
                    file_id    TEXT    NOT NULL,
                    added_at   TEXT    DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS bans (
                    user_id    INTEGER PRIMARY KEY,
                    ban_until  TEXT    NOT NULL
                );

                CREATE TABLE IF NOT EXISTS subscriptions (
                    user_id    INTEGER PRIMARY KEY,
                    is_subscribed INTEGER DEFAULT 0,
                    last_check   TEXT    DEFAULT (datetime('now'))
                );
                """
            )

    def add_user(self, user_id: int, username: str, full_name: str):
        with self._conn() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)",
                (user_id, username, full_name),
            )

    def get_all_users(self) -> list:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM users").fetchall()
            return [dict(r) for r in rows]

    def count_users(self) -> int:
        with self._conn() as conn:
            return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    def add_game(self, name: str, file_id: str):
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO games (name, file_id) VALUES (?, ?)",
                (name, file_id),
            )

    def get_all_games(self) -> list:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT id, name, file_id, added_at FROM games ORDER BY added_at DESC"
            ).fetchall()
            return [dict(r) for r in rows]

    def get_game(self, game_id: int) -> Optional[dict]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM games WHERE id = ?", (game_id,)).fetchone()
            return dict(row) if row else None

    def delete_game(self, game_id: int):
        with self._conn() as conn:
            conn.execute("DELETE FROM games WHERE id = ?", (game_id,))

    def count_games(self) -> int:
        with self._conn() as conn:
            return conn.execute("SELECT COUNT(*) FROM games").fetchone()[0]

    def set_ban(self, user_id: int, ban_until: datetime):
        with self._conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO bans (user_id, ban_until) VALUES (?, ?)",
                (user_id, ban_until.isoformat()),
            )

    def get_ban(self, user_id: int) -> Optional[datetime]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT ban_until FROM bans WHERE user_id = ?", (user_id,)
            ).fetchone()
            if not row:
                return None
            ban_until = datetime.fromisoformat(row["ban_until"])
            if datetime.now() < ban_until:
                return ban_until
            conn.execute("DELETE FROM bans WHERE user_id = ?", (user_id,))
            return None

    def remove_ban(self, user_id: int):
        with self._conn() as conn:
            conn.execute("DELETE FROM bans WHERE user_id = ?", (user_id,))

    def set_subscription(self, user_id: int, is_subscribed: bool):
        with self._conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO subscriptions (user_id, is_subscribed, last_check) VALUES (?, ?, ?)",
                (user_id, 1 if is_subscribed else 0, datetime.now().isoformat()),
            )

    def get_subscription(self, user_id: int) -> Optional[bool]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT is_subscribed FROM subscriptions WHERE user_id = ?", (user_id,)
            ).fetchone()
            return bool(row["is_subscribed"]) if row else None
