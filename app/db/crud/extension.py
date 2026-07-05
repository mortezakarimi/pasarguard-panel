"""Database operations for extension settings and migrations."""

from datetime import datetime as dt, timezone as tz

from sqlalchemy import select

from app.db import AsyncSession
from app.db.models import ExtensionMigration, ExtensionSettingsRow


async def get_extension_settings_row(db: AsyncSession, extension_id: str) -> ExtensionSettingsRow | None:
    result = await db.execute(select(ExtensionSettingsRow).where(ExtensionSettingsRow.extension_id == extension_id))
    return result.scalar_one_or_none()


async def list_extension_settings_rows(db: AsyncSession) -> list[ExtensionSettingsRow]:
    result = await db.execute(select(ExtensionSettingsRow))
    return list(result.scalars().all())


async def upsert_extension_settings(
    db: AsyncSession,
    extension_id: str,
    settings: dict,
    *,
    enabled: bool | None = None,
) -> ExtensionSettingsRow:
    row = await get_extension_settings_row(db, extension_id)
    if row is None:
        row = ExtensionSettingsRow(
            extension_id=extension_id,
            settings=settings,
            enabled=True if enabled is None else enabled,
        )
        db.add(row)
    else:
        row.settings = settings
        row.updated_at = dt.now(tz.utc)
        if enabled is not None:
            row.enabled = enabled
    await db.flush()
    return row


async def set_extension_enabled(db: AsyncSession, extension_id: str, enabled: bool) -> ExtensionSettingsRow:
    row = await get_extension_settings_row(db, extension_id)
    if row is None:
        row = ExtensionSettingsRow(extension_id=extension_id, settings={}, enabled=enabled)
        db.add(row)
    else:
        row.enabled = enabled
        row.updated_at = dt.now(tz.utc)
    await db.flush()
    return row


async def get_applied_migrations(db: AsyncSession, extension_id: str) -> list[ExtensionMigration]:
    result = await db.execute(
        select(ExtensionMigration).where(ExtensionMigration.extension_id == extension_id)
    )
    return list(result.scalars().all())


async def record_migration(db: AsyncSession, extension_id: str, revision: str) -> ExtensionMigration:
    row = ExtensionMigration(extension_id=extension_id, revision=revision)
    db.add(row)
    await db.flush()
    return row
