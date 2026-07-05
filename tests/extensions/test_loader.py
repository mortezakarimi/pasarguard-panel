"""Tests for extension loader allowlist behavior."""

from app.extensions.base import BaseExtension
from app.extensions.loader import _is_allowed, _parse_allowlist
from app.extensions.registry import ExtensionRegistry


class _SampleExtension(BaseExtension):
    id = "sample.test"
    name = "Sample"
    version = "1.0.0"
    permissions = []


def test_parse_allowlist_empty_means_all():
    assert _parse_allowlist("") is None
    assert _parse_allowlist("  ") is None


def test_parse_allowlist_splits_ids():
    assert _parse_allowlist("a,b, c") == {"a", "b", "c"}


def test_is_allowed_without_allowlist():
    assert _is_allowed("any.id", None) is True


def test_is_allowed_with_allowlist():
    allowlist = {"sample.test"}
    assert _is_allowed("sample.test", allowlist) is True
    assert _is_allowed("other.test", allowlist) is False


def test_registry_replace_on_duplicate_id():
    registry = ExtensionRegistry()
    registry.register(_SampleExtension())
    other = _SampleExtension()
    other.version = "2.0.0"
    registry.register(other)
    assert registry.get("sample.test").version == "2.0.0"
