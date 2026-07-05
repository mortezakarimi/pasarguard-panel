# Subscription Page UI

The public subscription page is server-rendered Jinja2. Extensions inject HTML via hooks and optional static assets.

## Slots

| Slot | Location |
|------|----------|
| `head` | Inside `<head>` (CSS, meta) |
| `before_content` | Start of `<body>` |
| `after_user_info` | After user info card |
| `after_apps` | After recommended apps |
| `footer` | Before closing `</body>` |

## Hook handler

```python
from app.extensions import SubscriptionFragment, SubscriptionSlot, Hook

async def on_render(self, user, **_kwargs):
    return SubscriptionFragment(
        slot=SubscriptionSlot.AFTER_APPS,
        extension_id=self.id,
        html="<div>Renew plan</div>",
        assets=[ExtensionAsset(url="/api/extensions/my.id/assets/banner.js", type="js")],
    )
```

## Template injection

The default template [`app/templates/subscription/index.html`](../../app/templates/subscription/index.html) includes:

```jinja
{% for fragment in extension_fragments.after_apps %}{{ fragment.html | safe }}{% endfor %}
```

## Static assets

Serve files from your extension `static/` directory:

```text
/api/extensions/{extension_id}/assets/{path}
```

## XSS responsibility

HTML fragments are rendered with `| safe`. Extension authors must sanitize or trust their own output. Do not include unsanitized user input in fragments.
