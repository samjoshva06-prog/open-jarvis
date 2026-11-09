from __future__ import annotations

from app.assistant_manager import AssistantManager
from app.plugins.tasks import TaskPlugin


class DisabledProvider:
    is_configured = False


def test_assistants_have_separate_plugin_permissions(tmp_path):
    manager = AssistantManager(provider=DisabledProvider())
    manager.plugins["tasks"] = TaskPlugin(tmp_path / "tasks.sqlite3")
    assert manager.respond("general", "What is 12 * (3 + 4)?")[1] == "calculator"
    assert manager.respond("developer", "What time is it?")[1] is None
    assert manager.respond("planner", "What time is it?")[1] == "clock"


def test_task_plugin_create_list_complete(tmp_path):
    plugin = TaskPlugin(tmp_path / "tasks.sqlite3")
    created = plugin.run("add task: prepare release | due: Friday")
    assert created == "Added task #1: prepare release (due: Friday)"
    assert "#1 prepare release (due: Friday)" in plugin.run("list tasks")
    assert plugin.run("complete task 1") == "Marked task #1 complete."
    assert plugin.run("list tasks") == "You have no open tasks. Add one with: add task: your task here."
