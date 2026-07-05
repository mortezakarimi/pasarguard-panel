"""API tests for extension management endpoints."""

import asyncio

from fastapi import status
from sqlalchemy import delete

from app.db.models import ExtensionSettingsRow
from app.extensions.base import BaseExtension
from app.extensions.registry import extension_registry
from tests.api import TestSession, client
from tests.api.helpers import auth_headers


class _ApiTestExtension(BaseExtension):
    id = "test.api"
    name = "API Test Extension"
    version = "0.0.1"
    permissions = []


def _clear_extension_settings() -> None:
    async def _run() -> None:
        async with TestSession() as session:
            await session.execute(delete(ExtensionSettingsRow))
            await session.commit()

    asyncio.run(_run())


def setup_function():
    extension_registry.clear()
    _clear_extension_settings()


def teardown_function():
    extension_registry.clear()
    _clear_extension_settings()


def test_list_extensions_empty(access_token):
    response = client.get("/api/extensions", headers=auth_headers(access_token))
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_list_extensions_with_registered_extension(access_token):
    extension_registry.register(_ApiTestExtension())
    response = client.get("/api/extensions", headers=auth_headers(access_token))
    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["id"] == "test.api"
    assert payload[0]["name"] == "API Test Extension"


def test_get_extension_not_found(access_token):
    response = client.get("/api/extensions/missing.ext", headers=auth_headers(access_token))
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_extension_settings(access_token):
    extension_registry.register(_ApiTestExtension())
    response = client.put(
        "/api/extensions/test.api/settings",
        headers=auth_headers(access_token),
        json={"settings": {"banner_text": "hello"}},
    )
    assert response.status_code == status.HTTP_200_OK

    get_response = client.get("/api/extensions/test.api/settings", headers=auth_headers(access_token))
    assert get_response.status_code == status.HTTP_200_OK
    assert get_response.json() == {"banner_text": "hello"}


def test_set_extension_enabled_owner_only(access_token):
    extension_registry.register(_ApiTestExtension())
    response = client.put(
        "/api/extensions/test.api/enabled",
        headers=auth_headers(access_token),
        json={"enabled": False},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["enabled"] is False
