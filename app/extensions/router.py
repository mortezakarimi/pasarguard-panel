"""Extension route adapter and core extension API mounting."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.extensions.registry import extension_registry
from app.utils.logger import get_logger

logger = get_logger("extensions.router")


def register_extension_routes(app: FastAPI) -> None:
    """
    Mount extension-owned routers and static assets on the FastAPI application.

    Each extension router is mounted at /api/extensions/{extension_id}/.
    Static assets are mounted at /api/extensions/{extension_id}/assets/.
    """
    for extension in extension_registry.all():
        router = extension.register_routes()
        prefix = f"/api/extensions/{extension.id}"
        app.include_router(router, prefix=prefix, tags=[f"Extension:{extension.id}"])

        static_dir = extension.static_directory
        if static_dir and Path(static_dir).is_dir():
            app.mount(
                f"{prefix}/assets",
                StaticFiles(directory=static_dir),
                name=f"extension_assets_{extension.id.replace('.', '_')}",
            )
            logger.debug("Mounted extension assets for %s at %s/assets", extension.id, prefix)

        ui_static = Path(static_dir) / "ui" if static_dir else None
        if ui_static and ui_static.is_dir():
            app.mount(
                f"{prefix}/ui",
                StaticFiles(directory=str(ui_static), html=True),
                name=f"extension_ui_{extension.id.replace('.', '_')}",
            )
            logger.debug("Mounted extension UI for %s at %s/ui", extension.id, prefix)
