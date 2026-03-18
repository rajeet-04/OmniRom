# External Integrations

**Analysis Date:** 2026-03-18

## APIs & External Services

**Romanization Libraries:**
- `langid` - Language detection (embedded library)
- `pypinyin` - Chinese pinyin conversion
- `transliterate` - ICU-based transliteration
- `unidecode` - Fallback transliteration

**Optional Runtime:**
- `cutlet` - Advanced Japanese romanization (with MeCab)

## Data Storage

**Caching:**
- Redis/Valkey (optional)
  - Connection: `REDIS_URL` env var
  - Default: `redis://localhost:6379/0`
  - Client: `redis` Python library

**File Storage:**
- None (stateless processing)
- File uploads processed in-memory

## Authentication & Identity

**Auth Provider:**
- Not applicable (public API)

## Monitoring & Observability

**Error Tracking:**
- Not configured

**Logs:**
- Python logging module
- Configurable via `LOG_LEVEL` env var (default: INFO)

## CI/CD & Deployment

**Hosting:**
- Docker container
- Tested for: Render, Fly.io

**CI Pipeline:**
- GitHub Actions (`.github/workflows/test.yml`)
- Runs on: Python 3.11, 3.12
- Test command: `pytest tests/`

## Environment Configuration

**Required env vars:**
- None strictly required (Redis optional)

**Optional env vars:**
- `REDIS_URL` - Cache backend connection
- `DEBUG` - Enable debug mode
- `LOG_LEVEL` - Logging level
- `APP_HOST` - Server host
- `APP_PORT` - Server port

**Secrets location:**
- `.env` file (local)
- Platform environment variables (deployment)

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

---

*Integration audit: 2026-03-18*
