"""Example extension implementation."""

from pathlib import Path

from pydantic import BaseModel, Field

from app.extensions import BaseExtension, Hook, SubscriptionFragment, SubscriptionSlot
from app.extensions.models import AdminPage, AdminUI, ExtensionUIManifest, SubscriptionUI

from .router import router


class ExampleSettings(BaseModel):
    banner_text: str = Field(default="Powered by PasarGuard Example Extension")
    show_banner: bool = Field(default=True)


class ExampleExtension(BaseExtension):
    id = "example.demo"
    name = "Example Extension"
    version = "1.0.0"
    description = "Reference extension demonstrating hooks, admin iframe UI, and subscription slots."
    sdk_version = "1.0"
    permissions = ["extensions.example_demo.read"]

    def __init__(self) -> None:
        super().__init__(static_directory=str(Path(__file__).parent / "static"))

    def register_routes(self):
        return router

    def register_hooks(self):
        return {Hook.USER_CREATED: self.on_user_created, Hook.SUBSCRIPTION_PAGE_RENDER: self.on_subscription_render}

    def get_ui_manifest(self) -> ExtensionUIManifest:
        return ExtensionUIManifest(
            admin=AdminUI(
                label="Example",
                icon="puzzle",
                pages=[AdminPage(path="dashboard", label="Dashboard", permissions=["extensions.example_demo.read"])],
            ),
            subscription=SubscriptionUI(slots=[SubscriptionSlot.AFTER_APPS]),
        )

    def get_settings_schema(self):
        return ExampleSettings

    async def on_user_created(self, user, admin, **_kwargs):
        return None

    async def on_subscription_render(self, user, **_kwargs):
        settings = ExampleSettings()
        if not settings.show_banner:
            return None
        return SubscriptionFragment(
            slot=SubscriptionSlot.AFTER_APPS,
            extension_id=self.id,
            html=(
                f'<div style="margin-top:16px;padding:12px;border-radius:8px;'
                f'background:hsl(var(--card));border:1px solid hsl(var(--border));text-align:center;">'
                f"{settings.banner_text} — {user.username}</div>"
            ),
        )
