from fastapi import APIRouter, Depends

from app.db import AsyncSession, get_db
from app.extensions.exceptions import ExtensionDisabledError
from app.extensions.models import ExtensionEnabledUpdate, ExtensionInfo, ExtensionSettingsUpdate
from app.models.admin import AdminDetails
from app.operation import OperatorType
from app.operation.extension import ExtensionOperation
from app.utils import responses

from .authentication import require_owner, require_permission

extension_operator = ExtensionOperation(operator_type=OperatorType.API)
router = APIRouter(tags=["Extensions"], prefix="/api/extensions", responses={401: responses._401, 403: responses._403})


@router.get("", response_model=list[ExtensionInfo])
async def list_extensions(
    db: AsyncSession = Depends(get_db),
    _: AdminDetails = Depends(require_permission("extensions", "read")),
):
    return await extension_operator.list_extensions(db)


@router.get("/{extension_id}", response_model=ExtensionInfo)
async def get_extension(
    extension_id: str,
    db: AsyncSession = Depends(get_db),
    _: AdminDetails = Depends(require_permission("extensions", "read")),
):
    return await extension_operator.get_extension(db, extension_id)


@router.get("/{extension_id}/settings")
async def get_extension_settings(
    extension_id: str,
    db: AsyncSession = Depends(get_db),
    _: AdminDetails = Depends(require_permission("extensions", "manage")),
):
    try:
        return await extension_operator.get_settings(db, extension_id)
    except ExtensionDisabledError as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.put("/{extension_id}/settings")
async def update_extension_settings(
    extension_id: str,
    payload: ExtensionSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    _: AdminDetails = Depends(require_permission("extensions", "manage")),
):
    try:
        return await extension_operator.update_settings(db, extension_id, payload)
    except ExtensionDisabledError as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.put("/{extension_id}/enabled", response_model=ExtensionInfo)
async def set_extension_enabled(
    extension_id: str,
    payload: ExtensionEnabledUpdate,
    db: AsyncSession = Depends(get_db),
    _: AdminDetails = Depends(require_owner()),
):
    return await extension_operator.set_enabled(db, extension_id, payload)
