from __future__ import annotations

from dataclasses import dataclass

from app.ai_provider import OpenAICompatibleProvider, ProviderError
from app.plugin_base import Plugin
from app.plugins.calculator import CalculatorPlugin
from app.plugins.clock import ClockPlugin
from app.plugins.tasks import TaskPlugin


@dataclass(frozen=True)
class Assistant:
    id: str
    name: str
    description: str
    instructions: str
    plugin_ids: tuple[str, ...]


class AssistantManager:
    """Stores assistant profiles and dispatches messages to allowed plugins or AI."""

    def __init__(self, provider: OpenAICompatibleProvider | None = None) -> None:
        plugins: tuple[Plugin, ...] = (CalculatorPlugin(), ClockPlugin(), TaskPlugin())
        self.plugins: dict[str, Plugin] = {plugin.manifest.id: plugin for plugin in plugins}
        self.provider = provider or OpenAICompatibleProvider()
        self.assistants: dict[str, Assistant] = {
            "general": Assistant(
                id="general",
                name="Jarvis",
                description="A general-purpose assistant for everyday questions.",
                instructions="Be helpful, clear, and honest about your capabilities.",
                plugin_ids=("calculator", "clock", "tasks"),
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
                description="Help organize projects, tasks, and time.",
                instructions="Help break work into clear, actionable steps. Use the tasks plugin for explicit task-list commands.",
                plugin_ids=("clock", "tasks"),
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

    def respond(
        self, assistant_id: str, message: str, history: list[dict[str, str]] | None = None
    ) -> tuple[str, str | None]:
        assistant = self.assistants.get(assistant_id)
        if assistant is None:
            raise KeyError("Unknown assistant")

        for plugin_id in assistant.plugin_ids:
            plugin = self.plugins[plugin_id]
            if plugin.matches(message):
                return plugin.run(message), plugin_id

        if self.provider.is_configured:
            messages = [{"role": "system", "content": assistant.instructions}]
            for item in (history or [])[-20:]:
                if item.get("role") in ("user", "assistant") and isinstance(item.get("content"), str):
                    messages.append({"role": item["role"], "content": item["content"][:4000]})
            messages.append({"role": "user", "content": message})
            try:
                return self.provider.respond(messages), None
            except ProviderError:
                raise

        return (
            f"{assistant.name} is ready. Set OPENAI_API_KEY to enable AI conversations; "
            "local calculator, clock, and task-list commands work without an API key.",
            None,
        )
