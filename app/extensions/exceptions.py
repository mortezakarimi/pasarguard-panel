"""Extension framework exception hierarchy."""


class ExtensionError(Exception):
    """Base exception for extension framework errors."""


class ExtensionNotFoundError(ExtensionError):
    """Raised when a requested extension is not registered."""


class ExtensionLoadError(ExtensionError):
    """Raised when an extension fails to load from an entry point."""


class ExtensionSettingsError(ExtensionError):
    """Raised when extension settings validation fails."""


class ExtensionDisabledError(ExtensionError):
    """Raised when an operation targets a disabled extension."""
