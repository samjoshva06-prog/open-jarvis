from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class PluginManifest:
    id: str
    name: str
    description: str
    version: str = "1.0.0"


class Plugin(ABC):
    """Base class for explicitly registered, permission-scoped plugins."""

    manifest: PluginManifest

    @abstractmethod
    def matches(self, message: str) -> bool:
        """Return whether this plugin can handle a user message."""

    @abstractmethod
    def run(self, message: str) -> str:
        """Run the plugin and return a user-visible result."""
