"""Controlled API surface exposed to extensions."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from app.db import AsyncSession
from app.db.crud.extension import get_extension_settings_row, upsert_extension_settings
from app.models.admin import AdminDetails
from app.models.user import UserCreate, UserModify, UserResponse
from app.operation import OperatorType
from app.operation.user import UserOperation
from app.utils.logger import get_logger


class ExtensionContext:
    """
    Facade providing a safe, versioned API for extension code.

    Extensions should use this context instead of importing core CRUD modules directly.
    """

    def __init__(self, db: AsyncSession, extension_id: str) -> None:
        self._db = db
        self._extension_id = extension_id
        self._user_operation = UserOperation(operator_type=OperatorType.SYSTEM)
        self._logger = get_logger(f"extension.{extension_id}")

    @property
    def db(self) -> AsyncSession:
        return self._db

    @property
    def extension_id(self) -> str:
        return self._extension_id

    @property
    def logger(self):
        return self._logger

    async def get_user(self, username: str) -> UserResponse:
        """Load a user by username."""
        from app.db.crud.user import get_user

        db_user = await get_user(self._db, username)
        if db_user is None:
            raise ValueError(f"User '{username}' not found")
        return UserResponse.model_validate(db_user)

    async def create_user(self, data: UserCreate, admin: AdminDetails) -> UserResponse:
        """Create a user via core business logic."""
        return await self._user_operation.create_user(self._db, data, admin)

    async def modify_user(self, username: str, data: UserModify, admin: AdminDetails) -> UserResponse:
        """Modify a user via core business logic."""
        from app.db.crud.user import get_user

        db_user = await get_user(self._db, username)
        if db_user is None:
            raise ValueError(f"User '{username}' not found")
        return await self._user_operation.modify_user_by_id(self._db, db_user.id, data, admin)

    async def get_settings(self) -> dict[str, Any]:
        """Return persisted settings for this extension."""
        row = await get_extension_settings_row(self._db, self._extension_id)
        return dict(row.settings) if row else {}

    async def set_settings(self, data: dict[str, Any], schema: type[BaseModel] | None = None) -> dict[str, Any]:
        """Validate and persist settings for this extension."""
        if schema is not None:
            validated = schema.model_validate(data)
            data = validated.model_dump()
        row = await upsert_extension_settings(self._db, self._extension_id, data)
        await self._db.commit()
        return dict(row.settings)
