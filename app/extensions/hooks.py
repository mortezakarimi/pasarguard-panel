"""Hook definitions and the HookBus observer."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from enum import StrEnum
from typing import Any, Awaitable, Callable

from app.extensions.models import SubscriptionFragment
from app.utils.logger import get_logger

logger = get_logger("extensions.hooks")

HookHandler = Callable[..., Awaitable[Any]]


class Hook(StrEnum):
    """Stable, versioned hook names emitted by the core."""

    USER_CREATED = "user.created"
    USER_MODIFIED = "user.modified"
    USER_DELETED = "user.deleted"
    USER_EXPIRED = "user.expired"
    USER_DATA_LIMITED = "user.data_limited"
    SUBSCRIPTION_PAGE_RENDER = "subscription.page.render"
    ADMIN_MANIFEST = "admin.manifest"


class HookBus:
    """
    Observer-style event bus for extension hooks.

    Handlers are registered per hook name. emit() fans out asynchronously and
    isolates failures so one extension cannot break core request handling.
    """

    def __init__(self) -> None:
        self._handlers: dict[Hook, list[tuple[str, HookHandler]]] = defaultdict(list)

    def register(self, extension_id: str, hook: Hook, handler: HookHandler) -> None:
        """Register a handler for a hook from a specific extension."""
        self._handlers[hook].append((extension_id, handler))

    def clear(self) -> None:
        """Remove all registered handlers (used in tests)."""
        self._handlers.clear()

    async def emit(self, hook: Hook, **payload: Any) -> None:
        """Fire-and-forget hook emission with fault isolation."""
        handlers = self._handlers.get(hook, [])
        if not handlers:
            return

        results = await asyncio.gather(
            *(self._safe_invoke(extension_id, hook, handler, payload) for extension_id, handler in handlers),
            return_exceptions=True,
        )
        for result in results:
            if isinstance(result, Exception):
                logger.warning("Hook %s handler failed: %s", hook, result, exc_info=result)

    async def emit_collect(self, hook: Hook, **payload: Any) -> list[Any]:
        """
        Await all handlers and collect non-None return values.

        Used when the core needs aggregated results (e.g. subscription fragments).
        """
        handlers = self._handlers.get(hook, [])
        if not handlers:
            return []

        results = await asyncio.gather(
            *(self._safe_invoke(extension_id, hook, handler, payload) for extension_id, handler in handlers),
            return_exceptions=True,
        )
        collected: list[Any] = []
        for result in results:
            if isinstance(result, Exception):
                logger.warning("Hook %s collect handler failed: %s", hook, result, exc_info=result)
                continue
            if result is None:
                continue
            if isinstance(result, list):
                collected.extend(result)
            else:
                collected.append(result)
        return collected

    async def _safe_invoke(
        self,
        extension_id: str,
        hook: Hook,
        handler: HookHandler,
        payload: dict[str, Any],
    ) -> Any:
        try:
            return await handler(**payload)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.warning(
                "Extension %s hook %s failed: %s",
                extension_id,
                hook,
                exc,
                exc_info=(type(exc), exc, exc.__traceback__),
            )
            raise


def group_subscription_fragments(fragments: list[Any]) -> dict[str, list[SubscriptionFragment]]:
    """Group subscription fragments by slot name."""
    grouped: dict[str, list[SubscriptionFragment]] = defaultdict(list)
    for item in fragments:
        if isinstance(item, SubscriptionFragment):
            grouped[item.slot.value].append(item)
        elif isinstance(item, dict):
            fragment = SubscriptionFragment.model_validate(item)
            grouped[fragment.slot.value].append(fragment)
    return dict(grouped)


def collect_subscription_assets(fragments: list[Any]) -> dict[str, list[str]]:
    """Extract unique CSS and JS asset URLs from subscription fragments."""
    css_urls: list[str] = []
    js_urls: list[str] = []
    seen: set[str] = set()

    for item in fragments:
        fragment = item if isinstance(item, SubscriptionFragment) else SubscriptionFragment.model_validate(item)
        for asset in fragment.assets:
            if asset.url in seen:
                continue
            seen.add(asset.url)
            if asset.type == "css":
                css_urls.append(asset.url)
            elif asset.type == "js":
                js_urls.append(asset.url)

    return {"css": css_urls, "js": js_urls}


hook_bus = HookBus()
