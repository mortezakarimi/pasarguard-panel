"""Extension registry singleton."""

from __future__ import annotations

from typing import Iterator

from app.extensions.exceptions import ExtensionNotFoundError
from app.extensions.protocols import PasarGuardExtension


class ExtensionRegistry:
    """
    Registry of loaded extensions.

    Single source of truth for extension discovery at runtime.
    """

    def __init__(self) -> None:
        self._extensions: dict[str, PasarGuardExtension] = {}

    def register(self, extension: PasarGuardExtension) -> None:
        """Register an extension instance, replacing any prior registration with the same id."""
        if not extension.id:
            raise ValueError("Extension id must be non-empty")
        self._extensions[extension.id] = extension

    def get(self, extension_id: str) -> PasarGuardExtension:
        """Return extension by id or raise ExtensionNotFoundError."""
        extension = self._extensions.get(extension_id)
        if extension is None:
            raise ExtensionNotFoundError(f"Extension '{extension_id}' is not registered")
        return extension

    def get_optional(self, extension_id: str) -> PasarGuardExtension | None:
        """Return extension by id or None."""
        return self._extensions.get(extension_id)

    def all(self) -> list[PasarGuardExtension]:
        """Return all registered extensions."""
        return list(self._extensions.values())

    def __iter__(self) -> Iterator[PasarGuardExtension]:
        return iter(self._extensions.values())

    def clear(self) -> None:
        """Remove all extensions (used in tests)."""
        self._extensions.clear()

    def has(self, extension_id: str) -> bool:
        return extension_id in self._extensions


extension_registry = ExtensionRegistry()
