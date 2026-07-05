"""Pydantic models for the extension framework."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SubscriptionSlot(StrEnum):
    """Injection slots on the public subscription HTML page."""

    HEAD = "head"
    BEFORE_CONTENT = "before_content"
    AFTER_USER_INFO = "after_user_info"
    AFTER_APPS = "after_apps"
    FOOTER = "footer"


class ExtensionAsset(BaseModel):
    """Static asset reference served by an extension."""

    url: str
    type: str = Field(description="Asset type: css or js")


class SubscriptionFragment(BaseModel):
    """HTML fragment returned by subscription.page.render hook handlers."""

    slot: SubscriptionSlot
    html: str = ""
    extension_id: str = ""
    assets: list[ExtensionAsset] = Field(default_factory=list)


class AdminPage(BaseModel):
    """Admin dashboard page exposed by an extension."""

    path: str
    label: str
    permissions: list[str] = Field(default_factory=list)


class AdminUI(BaseModel):
    """Admin dashboard UI manifest for an extension."""

    label: str
    icon: str | None = None
    pages: list[AdminPage] = Field(default_factory=list)
    settings_schema: dict[str, Any] | None = None


class SubscriptionUI(BaseModel):
    """Subscription page UI manifest for an extension."""

    slots: list[SubscriptionSlot] = Field(default_factory=list)


class ExtensionUIManifest(BaseModel):
    """UI manifest describing how an extension surfaces in the panel."""

    admin: AdminUI | None = None
    subscription: SubscriptionUI | None = None


class ExtensionInfo(BaseModel):
    """Public metadata for a registered extension."""

    id: str
    name: str
    version: str
    description: str = ""
    sdk_version: str = ""
    permissions: list[str] = Field(default_factory=list)
    enabled: bool = True
    ui: ExtensionUIManifest = Field(default_factory=ExtensionUIManifest)

    model_config = ConfigDict(from_attributes=True)


class ExtensionSettingsUpdate(BaseModel):
    """Payload for updating extension settings."""

    settings: dict[str, Any]


class ExtensionEnabledUpdate(BaseModel):
    """Payload for enabling or disabling an extension."""

    enabled: bool


class ExtensionFragmentsPayload(BaseModel):
    """Grouped subscription page fragments keyed by slot name."""

    head: list[SubscriptionFragment] = Field(default_factory=list)
    before_content: list[SubscriptionFragment] = Field(default_factory=list)
    after_user_info: list[SubscriptionFragment] = Field(default_factory=list)
    after_apps: list[SubscriptionFragment] = Field(default_factory=list)
    footer: list[SubscriptionFragment] = Field(default_factory=list)


class ExtensionAssetsPayload(BaseModel):
    """Collected CSS/JS asset URLs for the subscription page."""

    css: list[str] = Field(default_factory=list)
    js: list[str] = Field(default_factory=list)
