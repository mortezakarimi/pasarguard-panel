"""
PasarGuard extension framework.

Provides discovery, registration, hooks, and a controlled API surface for third-party extensions.
"""

from app.extensions.base import BaseExtension
from app.extensions.context import ExtensionContext
from app.extensions.exceptions import (
    ExtensionDisabledError,
    ExtensionError,
    ExtensionLoadError,
    ExtensionNotFoundError,
    ExtensionSettingsError,
)
from app.extensions.hooks import Hook, hook_bus
from app.extensions.loader import load_extensions
from app.extensions.models import (
    ExtensionAssetsPayload,
    ExtensionEnabledUpdate,
    ExtensionFragmentsPayload,
    ExtensionInfo,
    ExtensionSettingsUpdate,
    ExtensionUIManifest,
    SubscriptionFragment,
    SubscriptionSlot,
)
from app.extensions.protocols import PasarGuardExtension
from app.extensions.registry import ExtensionRegistry, extension_registry
from app.extensions.router import register_extension_routes

__all__ = [
    "BaseExtension",
    "ExtensionAssetsPayload",
    "ExtensionContext",
    "ExtensionDisabledError",
    "ExtensionEnabledUpdate",
    "ExtensionError",
    "ExtensionFragmentsPayload",
    "ExtensionInfo",
    "ExtensionLoadError",
    "ExtensionNotFoundError",
    "ExtensionRegistry",
    "ExtensionSettingsError",
    "ExtensionSettingsUpdate",
    "ExtensionUIManifest",
    "Hook",
    "PasarGuardExtension",
    "SubscriptionFragment",
    "SubscriptionSlot",
    "extension_registry",
    "hook_bus",
    "load_extensions",
    "register_extension_routes",
]
