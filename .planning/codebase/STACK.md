# Technology Stack

**Analysis Date:** 2026-03-18

## Languages

**Primary:**
- Python 3.11+ - Core application and API

**Secondary:**
- None

## Runtime

**Environment:**
- Python 3.11, 3.12

**Package Manager:**
- uv (modern Python package manager)
- Lockfile: `uv.lock` (present)

## Frameworks

**Core:**
- FastAPI 0.115.0 - Web framework
- Uvicorn 0.32.0 - ASGI server

**Testing:**
- pytest 8.0.0 - Test runner
- pytest-asyncio 0.23.0 - Async test support

**Build/Dev:**
- Hatchling - Build backend (from pyproject.toml)
- Docker - Containerization

## Key Dependencies

**Critical:**
- pypinyin 0.53.0 - Chinese pinyin romanization
- langid 1.1.6 - Language detection
- unidecode 1.3.8 - Unicode to ASCII transliteration
- transliterate 1.10.2 - General transliteration

**Infrastructure:**
- redis 5.0.0 - Caching layer
- httpx 0.27.0 - HTTP client
- python-multipart 0.0.22 - File upload handling
- python-dotenv 1.0.0 - Environment configuration

## Configuration

**Environment:**
- `.env` file for local development
- `.env.example` for reference
- Key configs: REDIS_URL, DEBUG, LOG_LEVEL

**Build:**
- `pyproject.toml` - Project metadata and dependencies
- `Dockerfile` - Container build configuration

## Platform Requirements

**Development:**
- Python 3.11+
- uv package manager
- Redis (optional, for caching)

**Production:**
- Docker container deployment
- Redis/Valkey for caching (optional)
- Supports deployment to Render, Fly.io, or similar

---

*Stack analysis: 2026-03-18*
