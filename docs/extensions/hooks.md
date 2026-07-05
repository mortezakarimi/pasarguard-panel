# Extension Hooks

Hooks are stable event names emitted by the core. Register handlers via `register_hooks()`.

## Catalog

| Hook | Emitted from | Payload |
|------|--------------|---------|
| `user.created` | `UserOperation.create_user` | `user`, `admin` |
| `user.modified` | `UserOperation._apply_modified_user` | `user`, `admin` |
| `user.deleted` | `UserOperation._remove_user` | `user`, `admin` |
| `user.expired` | `review_users.change_status` | `user` |
| `user.data_limited` | `review_users.change_status` | `user` |
| `subscription.page.render` | `SubscriptionOperation._enrich_subscription_payload` | `ctx`, `user`, `links`, `announce`, `apps` |
| `admin.manifest` | reserved | — |

## Fire-and-forget vs collect

- **emit** — used for side effects (`user.*` hooks). Non-blocking via `asyncio.create_task`.
- **emit_collect** — used when core needs return values (`subscription.page.render`).

## Example

```python
from app.extensions import Hook, SubscriptionFragment, SubscriptionSlot

async def on_subscription_render(self, user, **_kwargs):
    return SubscriptionFragment(
        slot=SubscriptionSlot.AFTER_APPS,
        extension_id=self.id,
        html="<div>Buy renewal</div>",
    )
```

## Error handling

Hook handler exceptions are caught and logged. Never raise into core request paths.
