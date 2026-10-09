# Renewal Bot

Auto keepalive and renewal for free VPS services (Lunes Host, Katabump).

## Deploy to blitz.cloud

1. Push this repo to GitHub
2. In blitz.cloud dashboard, deploy via GitHub or use MCP
3. Set environment variables:
   - `LUNES_EMAIL`, `LUNES_PASSWORD`
   - `KATABUMP_EMAIL`, `KATABUMP_PASSWORD`
4. Run as background worker (no web port needed, but /health on 8080)

## Endpoints

- `/` - status and last results
- `/health` - health check
- `/trigger/lunes` - manually trigger Lunes renewal
- `/trigger/katabump` - manually trigger Katabump renewal
