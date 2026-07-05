"""Extension discovery and loading via Python entry points."""

from __future__ import annotations

import sys
from importlib.metadata import entry_points

from app import on_shutdown, on_startup
from app.extensions.exceptions import ExtensionLoadError
from app.extensions.hooks import Hook, hook_bus
from app.extensions.registry import extension_registry
from app.utils.logger import get_logger
from config import extension_settings

logger = get_logger("extensions.loader")

ENTRY_POINT_GROUP = "pasarguard.extensions"
_loaded = False
_repo_example_loaded = False


def _try_load_repo_example(allowlist: set[str] | None, loaded_ids: list[str]) -> None:
    """Load in-repo example extension when available (development convenience)."""
    global _repo_example_loaded
    if _repo_example_loaded:
        return
    if allowlist is not None and "example.demo" not in allowlist:
        return

    import sys
    from pathlib import Path

    repo_example = Path(__file__).resolve().parents[2] / "extensions" / "example"
    if not repo_example.is_dir():
        return

    example_path = str(repo_example)
    if example_path not in sys.path:
        sys.path.insert(0, example_path)

    try:
        from pasarguard_ext_example.extension import ExampleExtension

        extension = ExampleExtension()
        extension_registry.register(extension)
        _register_hooks(extension)
        _register_lifecycle(extension)
        loaded_ids.append(extension.id)
        _repo_example_loaded = True
        logger.info("Loaded in-repo example extension %s", extension.id)
    except ImportError:
        logger.debug("In-repo example extension not importable")


def _parse_allowlist(raw: str) -> set[str] | None:
    """Parse comma-separated allowlist. Empty string means allow all discovered extensions."""
    if not raw.strip():
        return None
    return {item.strip() for item in raw.split(",") if item.strip()}


def _discover_entry_points() -> list:
    """Discover extension entry points across Python versions."""
    if sys.version_info >= (3, 12):
        return list(entry_points().select(group=ENTRY_POINT_GROUP))
    return list(entry_points().get(ENTRY_POINT_GROUP, []))


def _is_allowed(extension_id: str, allowlist: set[str] | None) -> bool:
    if allowlist is None:
        return True
    return extension_id in allowlist


def load_extensions(force: bool = False) -> list[str]:
    """
    Load extensions from entry points and register hooks and lifecycle handlers.

    Returns list of loaded extension ids.
    """
    global _loaded
    if _loaded and not force:
        return [ext.id for ext in extension_registry.all()]

    if not extension_settings.enabled:
        logger.info("Extensions are disabled via EXTENSIONS_ENABLED")
        _loaded = True
        return []

    allowlist = _parse_allowlist(extension_settings.allowlist)
    loaded_ids: list[str] = []

    for entry_point in _discover_entry_points():
        try:
            extension_cls = entry_point.load()
            extension = extension_cls() if callable(extension_cls) else extension_cls
            extension_id = extension.id

            if not _is_allowed(extension_id, allowlist):
                logger.debug("Extension %s skipped (not in allowlist)", extension_id)
                continue

            extension_registry.register(extension)
            _register_hooks(extension)
            _register_lifecycle(extension)
            loaded_ids.append(extension_id)
            logger.info("Loaded extension %s v%s", extension.name, extension.version)
        except Exception as exc:
            raise ExtensionLoadError(f"Failed to load extension '{entry_point.name}': {exc}") from exc

    _try_load_repo_example(allowlist, loaded_ids)

    _loaded = True
    return loaded_ids


def _register_hooks(extension) -> None:
    for hook, handler in extension.register_hooks().items():
        hook_bus.register(extension.id, hook, handler)


def _register_lifecycle(extension) -> None:
    @on_startup
    async def _startup():
        from app.db import GetDB
        from app.extensions.context import ExtensionContext

        async with GetDB() as db:
            ctx = ExtensionContext(db=db, extension_id=extension.id)
            await extension.on_startup(ctx)
            await extension.run_migrations(ctx)

    @on_shutdown
    async def _shutdown():
        from app.db import GetDB
        from app.extensions.context import ExtensionContext

        async with GetDB() as db:
            ctx = ExtensionContext(db=db, extension_id=extension.id)
            await extension.on_shutdown(ctx)
