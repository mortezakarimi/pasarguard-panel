# PasarGuard Extensions — Author Quickstart

This guide shows how to build and enable a PasarGuard extension.

## 1. Create a Python package

```text
my-extension/
├── pyproject.toml
└── my_extension/
    ├── __init__.py
    ├── extension.py
    ├── router.py
    └── static/ui/index.html
```

Register the extension entry point:

```toml
[project.entry-points."pasarguard.extensions"]
my_ext = "my_extension.extension:MyExtension"
```

## 2. Implement the extension contract

Subclass `BaseExtension` from `app.extensions` (or the future `pasarguard-ext` package):

```python
from app.extensions import BaseExtension, Hook

class MyExtension(BaseExtension):
    id = "my.vendor.feature"
    name = "My Feature"
    version = "1.0.0"
    permissions = ["extensions.my_vendor_feature.read"]

    def register_routes(self):
        from .router import router
        return router

    def register_hooks(self):
        return {Hook.USER_CREATED: self.on_user_created}

    async def on_user_created(self, user, admin, **_kwargs):
        ...
```

## 3. Install and enable

```bash
uv pip install -e ./my-extension
```

```env
EXTENSIONS_ENABLED=true
EXTENSIONS_ALLOWLIST=my.vendor.feature
```

## 4. Surfaces

| Surface | How |
|---------|-----|
| HTTP API | `register_routes()` → `/api/extensions/{id}/` |
| Admin UI | `get_ui_manifest()` + static files under `static/ui/` |
| Subscription page | `Hook.SUBSCRIPTION_PAGE_RENDER` returning `SubscriptionFragment` |
| Settings | `get_settings_schema()` + `/api/extensions/{id}/settings` |

## Reference implementation

See [`extensions/example/`](../../extensions/example/) in this repository.

## Further reading

- [architecture.md](./architecture.md)
- [hooks.md](./hooks.md)
- [admin-ui.md](./admin-ui.md)
- [subscription-ui.md](./subscription-ui.md)
- [migration-guide.md](./migration-guide.md)
