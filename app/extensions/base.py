"""Base extension with template-method defaults."""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import APIRouter

from app.extensions.hooks import Hook, HookHandler
from app.extensions.models import ExtensionUIManifest
from app.extensions.protocols import PasarGuardExtension

if TYPE_CHECKING:
    from app.extensions.context import ExtensionContext


class BaseExtension(PasarGuardExtension):
    """
    Default extension implementation.

    Subclasses override only the capabilities they need; all others are no-ops.
    """

    description: str = ""
    sdk_version: str = "1.0"
    permissions: list[str] = []
    _static_directory: str | None = None

    def __init__(self, static_directory: str | None = None) -> None:
        self._static_directory = static_directory

    @property
    def static_directory(self) -> str | None:
        if self._static_directory:
            return self._static_directory
        try:
            module_file = Path(inspect.getfile(self.__class__))
            static = module_file.parent / "static"
            if static.is_dir():
                return str(static.resolve())
        except (TypeError, OSError):
            pass
        return None

    def register_routes(self) -> APIRouter:
        return APIRouter()

    def register_hooks(self) -> dict[Hook, HookHandler]:
        return {}

    def get_ui_manifest(self) -> ExtensionUIManifest:
        return ExtensionUIManifest()

    async def on_startup(self, ctx: ExtensionContext) -> None:
        return None

    async def on_shutdown(self, ctx: ExtensionContext) -> None:
        return None

    async def run_migrations(self, ctx: ExtensionContext) -> None:
        return None
