import os
import sqlite3
from typing import List, Dict, Any, Optional


class StorageService:
    def __init__(self, db_path: Optional[str] = None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = db_path or os.path.join(base_dir, "..", "client_data.db")
        self.db_path = os.path.abspath(self.db_path)
        self._ensure_schema()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    completed INTEGER DEFAULT 0
                );
                """
            )
            conn.commit()

    def list_tasks(self) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT id, title, description, created_at, completed FROM tasks ORDER BY id ASC").fetchall()
            return [dict(row) for row in rows]

    def create_task(self, title: str, description: str = "") -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO tasks (title, description, completed) VALUES (?, ?, 0)",
                (title, description),
            )
            conn.commit()
            return int(cur.lastrowid)

    def update_task(self, task_id: int, **fields):
        if not fields:
            return
        keys = []
        values = []
        for k, v in fields.items():
            keys.append(f"{k} = ?")
            values.append(v)
        values.append(task_id)
        with self._connect() as conn:
            conn.execute(f"UPDATE tasks SET {', '.join(keys)} WHERE id = ?", values)
            conn.commit()

    def delete_task(self, task_id: int):
        with self._connect() as conn:
            conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()