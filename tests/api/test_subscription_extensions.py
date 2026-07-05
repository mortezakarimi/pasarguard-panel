"""Subscription page extension slot integration tests."""

from fastapi import status

from app.extensions.base import BaseExtension
from app.extensions.hooks import Hook
from app.extensions.models import SubscriptionFragment, SubscriptionSlot
from app.extensions.registry import extension_registry
from tests.api import client
from tests.api.helpers import auth_headers, create_group, create_user, unique_name


class _SubscriptionTestExtension(BaseExtension):
    id = "test.subscription"
    name = "Subscription Test"
    version = "0.0.1"
    permissions = []

    def register_hooks(self):
        return {Hook.SUBSCRIPTION_PAGE_RENDER: self.render_banner}

    async def render_banner(self, user, **_kwargs):
        return SubscriptionFragment(
            slot=SubscriptionSlot.AFTER_APPS,
            extension_id=self.id,
            html='<div id="ext-test-banner">extension-banner</div>',
        )


def setup_function():
    extension_registry.clear()


def teardown_function():
    extension_registry.clear()


def test_subscription_page_includes_extension_fragment(access_token):
    extension_registry.register(_SubscriptionTestExtension())
    from app.extensions.hooks import hook_bus
    from app.extensions.loader import _register_hooks

    _register_hooks(_SubscriptionTestExtension())

    group = create_group(access_token, name=unique_name("ext-sub"))
    user = create_user(access_token, group_ids=[group["id"]], username=unique_name("extsub"))

    response = client.get(
        f"{user['subscription_url']}/",
        headers={"Accept": "text/html"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert "extension-banner" in response.text
    assert 'id="ext-test-banner"' in response.text

    hook_bus.clear()
