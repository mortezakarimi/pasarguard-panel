"""Helpers for emitting extension hooks from core operations."""

from __future__ import annotations

import asyncio
from typing import Any

from app.extensions.hooks import Hook, hook_bus
from app.utils.logger import get_logger

logger = get_logger("extensions.emit")


def emit_hook(hook: Hook, **payload: Any) -> None:
    """Fire-and-forget hook emission safe for request handlers."""
    asyncio.create_task(_emit_safe(hook, **payload))


async def _emit_safe(hook: Hook, **payload: Any) -> None:
    try:
        await hook_bus.emit(hook, **payload)
    except Exception as exc:
        logger.warning("Failed to emit hook %s: %s", hook, exc, exc_info=exc)


async def collect_hook(hook: Hook, **payload: Any) -> list[Any]:
    """Await hook handlers and collect return values."""
    return await hook_bus.emit_collect(hook, **payload)
