from __future__ import annotations

from dataclasses import dataclass

from app.plugin_base import Plugin, PluginManifest
from app.plugins.calculator import CalculatorPlugin
from app.plugins.clock import ClockPlugin


@dataclass(frozen=True)
class Assistant:
    id: str
    name: str
    description: str
    instructions: str
    plugin_ids: tuple[str, ...]


class AssistantManager:
    """Stores assistant profiles and dispatches messages to allowed plugins."""

    def __init__(self) -> None:
        plugins: tuple[Plugin, ...] = (CalculatorPlugin(), ClockPlugin())
        self.plugins: dict[str, Plugin] = {plugin.manifest.id: plugin for plugin in plugins}
        self.assistants: dict[str, Assistant] = {
            "general": Assistant(
                id="general",
                name="Jarvis",
                description="A general-purpose assistant for everyday questions.",
                instructions="Be helpful, clear, and honest about your capabilities.",
                plugin_ids=("calculator", "clock"),
            ),
            "developer": Assistant(
                id="developer",
                name="Dev Assistant",
                description="A focused assistant for software development tasks.",
                instructions="Give practical, concise software development guidance.",
                plugin_ids=("calculator",),
            ),
            "planner": Assistant(
                id="planner",
                name="Work Planner",
                description="A focused assistant for organizing work and time.",
                instructions="Help break work into clear, actionable steps.",
                plugin_ids=("clock",),
            ),
        }

    def list_assistants(self) -> list[dict[str, str]]:
        return [
            {"id": item.id, "name": item.name, "description": item.description}
            for item in self.assistants.values()
        ]

    def list_plugins(self) -> list[dict[str, str]]:
        return [
            {
                "id": plugin.manifest.id,
                "name": plugin.manifest.name,
                "description": plugin.manifest.description,
                "version": plugin.manifest.version,
            }
            for plugin in self.plugins.values()
        ]

    def respond(self, assistant_id: str, message: str) -> tuple[str, str | None]:
        assistant = self.assistants.get(assistant_id)
        if assistant is None:
            raise KeyError("Unknown assistant")

        for plugin_id in assistant.plugin_ids:
            plugin = self.plugins[plugin_id]
            if plugin.matches(message):
                return plugin.run(message), plugin_id

        return (
            f"{assistant.name} is ready to help. This starter version can use its enabled "
            "plugins; connect a language-model provider to enable open-ended AI conversations.",
            None,
        )
