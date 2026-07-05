"""Business logic for extension management."""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException

from app.db import AsyncSession
from app.db.crud.extension import (
    get_extension_settings_row,
    list_extension_settings_rows,
    set_extension_enabled,
    upsert_extension_settings,
)
from app.extensions.exceptions import ExtensionDisabledError, ExtensionNotFoundError
from app.extensions.models import ExtensionEnabledUpdate, ExtensionInfo, ExtensionSettingsUpdate
from app.extensions.registry import extension_registry
from app.operation import BaseOperation, OperatorType


class ExtensionOperation(BaseOperation):
    """Manage installed extensions and their persisted settings."""

    def __init__(self, operator_type: OperatorType = OperatorType.API):
        super().__init__(operator_type=operator_type)

    async def list_extensions(self, db: AsyncSession) -> list[ExtensionInfo]:
        rows = {row.extension_id: row for row in await list_extension_settings_rows(db)}
        items: list[ExtensionInfo] = []
        for extension in extension_registry.all():
            row = rows.get(extension.id)
            enabled = row.enabled if row else True
            items.append(
                ExtensionInfo(
                    id=extension.id,
                    name=extension.name,
                    version=extension.version,
                    description=extension.description,
                    sdk_version=extension.sdk_version,
                    permissions=list(extension.permissions),
                    enabled=enabled,
                    ui=extension.get_ui_manifest(),
                )
            )
        return items

    async def get_extension(self, db: AsyncSession, extension_id: str) -> ExtensionInfo:
        extension = self._get_extension_or_404(extension_id)
        row = await get_extension_settings_row(db, extension_id)
        return ExtensionInfo(
            id=extension.id,
            name=extension.name,
            version=extension.version,
            description=extension.description,
            sdk_version=extension.sdk_version,
            permissions=list(extension.permissions),
            enabled=row.enabled if row else True,
            ui=extension.get_ui_manifest(),
        )

    async def get_settings(self, db: AsyncSession, extension_id: str) -> dict[str, Any]:
        extension = self._get_extension_or_404(extension_id)
        await self._ensure_enabled(db, extension_id)
        row = await get_extension_settings_row(db, extension_id)
        settings = dict(row.settings) if row else {}
        schema = extension.get_settings_schema()
        if schema is not None:
            return schema.model_validate(settings).model_dump()
        return settings

    async def update_settings(
        self,
        db: AsyncSession,
        extension_id: str,
        payload: ExtensionSettingsUpdate,
    ) -> dict[str, Any]:
        extension = self._get_extension_or_404(extension_id)
        await self._ensure_enabled(db, extension_id)
        settings = payload.settings
        schema = extension.get_settings_schema()
        if schema is not None:
            settings = schema.model_validate(settings).model_dump()
        row = await upsert_extension_settings(db, extension_id, settings)
        await db.commit()
        return dict(row.settings)

    async def set_enabled(
        self,
        db: AsyncSession,
        extension_id: str,
        payload: ExtensionEnabledUpdate,
    ) -> ExtensionInfo:
        self._get_extension_or_404(extension_id)
        await set_extension_enabled(db, extension_id, payload.enabled)
        await db.commit()
        return await self.get_extension(db, extension_id)

    def _get_extension_or_404(self, extension_id: str):
        try:
            return extension_registry.get(extension_id)
        except ExtensionNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    async def _ensure_enabled(self, db: AsyncSession, extension_id: str) -> None:
        row = await get_extension_settings_row(db, extension_id)
        if row is not None and not row.enabled:
            raise ExtensionDisabledError(f"Extension '{extension_id}' is disabled")
