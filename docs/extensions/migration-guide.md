# Extension Database Migrations

## Core tables

The framework provides:

- `extension_settings` — settings and enabled state
- `extension_migrations` — revision tracking

## Extension-owned tables

Use the naming convention:

```text
ext_{extension_id_with_underscores}_{table}
```

Example for `payment.stripe`:

```text
ext_payment_stripe_transactions
```

## Implementing migrations

Override `run_migrations()` on your extension:

```python
async def run_migrations(self, ctx: ExtensionContext) -> None:
    from app.db.crud.extension import get_applied_migrations, record_migration

    revision = "001_init"
    applied = {m.revision for m in await get_applied_migrations(ctx.db, self.id)}
    if revision in applied:
        return

    await ctx.db.execute(text("CREATE TABLE IF NOT EXISTS ext_example_events (...)"))
    await record_migration(ctx.db, self.id, revision)
    await ctx.db.commit()
```

## Idempotency

Migrations must be safe to re-check on every startup. Always consult `extension_migrations` before applying DDL.
