"""Tests for HookBus."""

import pytest

from app.extensions.hooks import Hook, HookBus, collect_subscription_assets, group_subscription_fragments
from app.extensions.models import ExtensionAsset, SubscriptionFragment, SubscriptionSlot


@pytest.mark.asyncio
async def test_emit_isolates_handler_failures():
    bus = HookBus()

    async def failing_handler(**_kwargs):
        raise RuntimeError("boom")

    async def ok_handler(**_kwargs):
        return None

    bus.register("ext.a", Hook.USER_CREATED, failing_handler)
    bus.register("ext.b", Hook.USER_CREATED, ok_handler)
    await bus.emit(Hook.USER_CREATED, user="u")


@pytest.mark.asyncio
async def test_emit_collect_gathers_results():
    bus = HookBus()

    async def handler_a(**_kwargs):
        return SubscriptionFragment(slot=SubscriptionSlot.HEAD, html="<a>")

    async def handler_b(**_kwargs):
        return [SubscriptionFragment(slot=SubscriptionSlot.FOOTER, html="<b>")]

    bus.register("ext.a", Hook.SUBSCRIPTION_PAGE_RENDER, handler_a)
    bus.register("ext.b", Hook.SUBSCRIPTION_PAGE_RENDER, handler_b)

    results = await bus.emit_collect(Hook.SUBSCRIPTION_PAGE_RENDER)
    assert len(results) == 2


def test_group_subscription_fragments():
    fragments = [
        SubscriptionFragment(slot=SubscriptionSlot.HEAD, html="h"),
        SubscriptionFragment(slot=SubscriptionSlot.AFTER_APPS, html="a"),
    ]
    grouped = group_subscription_fragments(fragments)
    assert len(grouped["head"]) == 1
    assert len(grouped["after_apps"]) == 1


def test_collect_subscription_assets_deduplicates():
    fragments = [
        SubscriptionFragment(
            slot=SubscriptionSlot.HEAD,
            assets=[ExtensionAsset(url="/a.css", type="css"), ExtensionAsset(url="/a.css", type="css")],
        ),
        SubscriptionFragment(
            slot=SubscriptionSlot.FOOTER,
            assets=[ExtensionAsset(url="/b.js", type="js")],
        ),
    ]
    assets = collect_subscription_assets(fragments)
    assert assets["css"] == ["/a.css"]
    assert assets["js"] == ["/b.js"]
