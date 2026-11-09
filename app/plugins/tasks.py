from __future__ import annotations

import os
import re
import sqlite3
from pathlib import Path

from app.plugin_base import Plugin, PluginManifest


class TaskPlugin(Plugin):
    """Local SQLite task list. Tasks are private to this server instance."""

    manifest = PluginManifest(
        id="tasks",
        name="Tasks & Reminders",
        description="Create, list, and complete personal tasks; optional due dates are stored as text.",
    )
    _add = re.compile(r"^\s*(?:add|create)\s+task\s*:\s*(.+?)\s*$", re.IGNORECASE)
    _complete = re.compile(r"^\s*(?:complete|finish|done)\s+task\s+#?(\d+)\s*$", re.IGNORECASE)
    _list = re.compile(r"^\s*(?:list|show|view)\s+(?:my\s+)?tasks\s*$", re.IGNORECASE)

    def __init__(self, database_path: str | Path | None = None) -> None:
        configured_path = database_path or os.getenv("OPEN_JARVIS_DATABASE", "data/open_jarvis.sqlite3")
        self.database_path = Path(configured_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS tasks ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, "
                "due TEXT, completed INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def matches(self, message: str) -> bool:
        return bool(self._add.match(message) or self._complete.match(message) or self._list.match(message))

    def run(self, message: str) -> str:
        add_match = self._add.match(message)
        if add_match:
            title = add_match.group(1).strip()
            if len(title) > 500:
                return "Task titles must be 500 characters or fewer."
            due = None
            if " | due:" in title.lower():
                split_at = title.lower().rfind(" | due:")
                title, due = title[:split_at].strip(), title[split_at + 7 :].strip()
                if not due:
                    due = None
            if not title:
                return "Please include a task title, for example: add task: prepare project plan."
            with self._connect() as connection:
                cursor = connection.execute("INSERT INTO tasks (title, due) VALUES (?, ?)", (title, due))
                task_id = cursor.lastrowid
            suffix = f" (due: {due})" if due else ""
            return f"Added task #{task_id}: {title}{suffix}"

        complete_match = self._complete.match(message)
        if complete_match:
            task_id = int(complete_match.group(1))
            with self._connect() as connection:
                cursor = connection.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
            return f"Marked task #{task_id} complete." if cursor.rowcount else f"I couldn't find task #{task_id}."

        with self._connect() as connection:
            tasks = connection.execute(
                "SELECT id, title, due FROM tasks WHERE completed = 0 ORDER BY id LIMIT 100"
            ).fetchall()
        if not tasks:
            return "You have no open tasks. Add one with: add task: your task here."
        lines = [
            f"#{task['id']} {task['title']}" + (f" (due: {task['due']})" if task["due"] else "")
            for task in tasks
        ]
        return "Your open tasks:\n" + "\n".join(lines)
