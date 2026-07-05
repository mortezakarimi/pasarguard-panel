"""Tests for ExtensionRegistry."""

from app.extensions.base import BaseExtension
from app.extensions.exceptions import ExtensionNotFoundError
from app.extensions.registry import ExtensionRegistry


class _DummyExtension(BaseExtension):
    id = "test.dummy"
    name = "Dummy"
    version = "0.0.1"
    permissions = []


def test_register_and_get():
    registry = ExtensionRegistry()
    extension = _DummyExtension()
    registry.register(extension)
    assert registry.get("test.dummy") is extension


def test_get_raises_for_missing():
    registry = ExtensionRegistry()
    try:
        registry.get("missing")
        assert False, "Expected ExtensionNotFoundError"
    except ExtensionNotFoundError:
        pass


def test_all_returns_registered_extensions():
    registry = ExtensionRegistry()
    ext1 = _DummyExtension()
    registry.register(ext1)
    assert len(registry.all()) == 1


def test_default_hooks_empty():
    extension = _DummyExtension()
    assert extension.register_hooks() == {}
