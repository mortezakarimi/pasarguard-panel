# Example PasarGuard Extension

Reference implementation for the PasarGuard extension framework.

## Install (development)

```bash
uv pip install -e extensions/example
```

## Enable

```env
EXTENSIONS_ENABLED=true
EXTENSIONS_ALLOWLIST=example.demo
```

## Surfaces demonstrated

- Hook: `user.created`
- Hook: `subscription.page.render` (after_apps slot banner)
- Admin iframe UI at `/dashboard/#/extensions/example.demo`
- Health endpoint at `/api/extensions/example.demo/health`
