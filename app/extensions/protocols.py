"""Extension capability protocols and the composed extension contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Awaitable, Callable

from fastapi import APIRouter
from pydantic import BaseModel

from app.extensions.hooks import Hook
from app.extensions.models import ExtensionUIManifest

if TYPE_CHECKING:
    from app.extensions.context import ExtensionContext

HookHandler = Callable[..., Awaitable[Any]]


class RouteProvider(ABC):
    """Capability: expose HTTP routes."""

    @abstractmethod
    def register_routes(self) -> APIRouter:
        """Return a FastAPI router mounted under /api/extensions/{id}/."""


class HookProvider(ABC):
    """Capability: subscribe to core lifecycle hooks."""

    @abstractmethod
    def register_hooks(self) -> dict[Hook, HookHandler]:
        """Return hook name to async handler mapping."""


class UIProvider(ABC):
    """Capability: declare admin and subscription UI surfaces."""

    @abstractmethod
    def get_ui_manifest(self) -> ExtensionUIManifest:
        """Return UI manifest for dashboard and subscription integration."""


class SettingsProvider(ABC):
    """Capability: validate and expose extension settings schema."""

    def get_settings_schema(self) -> type[BaseModel] | None:
        """Return Pydantic model for extension settings, or None if not configurable."""
        return None


class MigrationProvider(ABC):
    """Capability: run database migrations owned by the extension."""

    async def run_migrations(self, ctx: ExtensionContext) -> None:
        """Apply extension-owned migrations."""


class LifecycleProvider(ABC):
    """Capability: run startup and shutdown hooks."""

    async def on_startup(self, ctx: ExtensionContext) -> None:
        """Called once when the extension is loaded at application startup."""

    async def on_shutdown(self, ctx: ExtensionContext) -> None:
        """Called once when the application shuts down."""


class PasarGuardExtension(
    RouteProvider,
    HookProvider,
    UIProvider,
    SettingsProvider,
    MigrationProvider,
    LifecycleProvider,
    ABC,
):
    """
    Composed extension contract.

    Extensions must define identity fields and may override any capability method.
    Unimplemented capabilities use BaseExtension no-op defaults.
    """

    id: str
    name: str
    version: str
    description: str = ""
    sdk_version: str = "1.0"
    permissions: list[str]

    @property
    @abstractmethod
    def static_directory(self) -> str | None:
        """Absolute path to static assets directory, if any."""
