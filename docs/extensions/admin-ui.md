# Admin Dashboard UI

Extensions expose admin UI through a **hybrid shell**:

1. **Native shell** — PasarGuard dashboard renders list page, header, enable toggle, RBAC.
2. **Iframe content** — extension serves UI from `/api/extensions/{id}/ui/`.

## UI manifest

```python
from app.extensions.models import AdminPage, AdminUI, ExtensionUIManifest

def get_ui_manifest(self):
    return ExtensionUIManifest(
        admin=AdminUI(
            label="Payments",
            icon="credit-card",
            pages=[AdminPage(path="dashboard", label="Dashboard")],
        )
    )
```

## Routes

| Dashboard route | Purpose |
|-----------------|---------|
| `/extensions` | List installed extensions |
| `/extensions/{id}` | Extension host with iframe |

## Static UI files

Place admin UI in `static/ui/` inside your extension package. The core mounts it at:

```text
/api/extensions/{extension_id}/ui/
```

## Iframe sandbox

The dashboard iframe uses:

```html
sandbox="allow-scripts allow-forms allow-same-origin"
```

## Permissions

Declare permissions in your extension manifest. Gate dashboard routes with `extensions.read` and settings with `extensions.manage`.
