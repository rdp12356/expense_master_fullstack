from typing import List, Optional, Dict, Any
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="SuperApp API")

DB_PATH = "./server_data.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_schema():
    with get_conn() as conn:
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


class TaskIn(BaseModel):
    title: str
    description: Optional[str] = ""
    completed: Optional[bool] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    created_at: Optional[str]
    completed: bool


@app.on_event("startup")
async def startup():
    ensure_schema()


@app.get("/tasks", response_model=List[TaskOut])
async def list_tasks():
    with get_conn() as conn:
        rows = conn.execute("SELECT id, title, description, created_at, completed FROM tasks ORDER BY id ASC").fetchall()
        return [
            {
                "id": r["id"],
                "title": r["title"],
                "description": r["description"],
                "created_at": r["created_at"],
                "completed": bool(r["completed"]),
            }
            for r in rows
        ]


@app.post("/tasks", response_model=TaskOut)
async def create_task(task: TaskIn):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO tasks (title, description, completed) VALUES (?, ?, ?)",
            (task.title.strip(), task.description or "", int(bool(task.completed))) if task.completed is not None else (task.title.strip(), task.description or "", 0),
        )
        conn.commit()
        new_id = int(cur.lastrowid)
        row = conn.execute("SELECT id, title, description, created_at, completed FROM tasks WHERE id = ?", (new_id,)).fetchone()
        return {
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "created_at": row["created_at"],
            "completed": bool(row["completed"]),
        }


@app.patch("/tasks/{task_id}", response_model=TaskOut)
async def update_task(task_id: int, task: TaskUpdate):
    fields: Dict[str, Any] = {}
    if task.title is not None and task.title != "":
        fields["title"] = task.title
    if task.description is not None:
        fields["description"] = task.description
    if task.completed is not None:
        fields["completed"] = int(bool(task.completed))
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    keys = ", ".join([f"{k} = ?" for k in fields.keys()])
    values = list(fields.values()) + [task_id]

    with get_conn() as conn:
        cur = conn.execute("UPDATE tasks SET " + keys + " WHERE id = ?", values)
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task not found")
        conn.commit()
        row = conn.execute("SELECT id, title, description, created_at, completed FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return {
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "created_at": row["created_at"],
            "completed": bool(row["completed"]),
        }


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task not found")
        conn.commit()
        return {"status": "ok"}