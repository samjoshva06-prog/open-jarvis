from __future__ import annotations

from datetime import datetime, timezone

from app.plugin_base import Plugin, PluginManifest


class ClockPlugin(Plugin):
    manifest = PluginManifest(
        id="clock",
        name="Clock & Date",
        description="Reports the current date and time in UTC.",
    )
    _keywords = ("time", "date", "clock", "utc", "today")

    def matches(self, message: str) -> bool:
        lowered = message.lower()
        return any(keyword in lowered for keyword in self._keywords)

    def run(self, message: str) -> str:
        now = datetime.now(timezone.utc)
        return f"The current time is {now.strftime('%A, %B %d, %Y at %H:%M:%S UTC')}."
