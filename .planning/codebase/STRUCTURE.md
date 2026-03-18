# Codebase Structure

**Analysis Date:** 2026-03-18

## Directory Layout

```
OmniRom/
├── app/                    # Main application package
│   ├── api/               # API route handlers
│   ├── core/              # Core business logic
│   ├── engines/           # Romanization engines
│   ├── middleware/        # Custom middleware
│   ├── schemas/          # Pydantic schemas
│   └── main.py           # FastAPI app entry point
├── tests/                 # Test suite
├── .github/workflows/    # CI/CD configuration
├── pyproject.toml        # Project configuration
├── requirements.txt      # Dependencies
└── Dockerfile           # Container build
```

## Directory Purposes

**`app/api/`:**
- Purpose: HTTP route handlers
- Contains: `romanize.py`, `batch.py`, `files.py`, `languages.py`, `cache.py`, `stats.py`
- Key files: `app/api/romanize.py` (main endpoint)

**`app/core/`:**
- Purpose: Business logic components
- Contains: `detector.py`, `cache.py`, `stats.py`, `styler.py`
- Key files: `app/core/detector.py` (script detection), `app/core/cache.py` (Redis cache)

**`app/engines/`:**
- Purpose: Script-specific romanization implementations
- Contains: `router.py`, `icu_engine.py`, `chinese_engine.py`, `japanese_engine.py`, `korean_engine.py`, `indic_engine.py`, `uroman_engine.py`, `arabic_urdu_romanizer.py`
- Key files: `app/engines/router.py` (routing logic)

**`app/middleware/`:**
- Purpose: Cross-cutting request/response handling
- Contains: `logging.py`
- Key files: `app/middleware/logging.py`

**`app/schemas/`:**
- Purpose: Request/response data validation
- Contains: `romanize.py`

**`tests/`:**
- Purpose: Test suite
- Contains: `test_api.py`, `test_engines.py`, `test_detector.py`

## Key File Locations

**Entry Points:**
- `app/main.py`: FastAPI application initialization, router registration
- `app/api/romanize.py`: Main `/v1/romanize` endpoint

**Configuration:**
- `pyproject.toml`: Project metadata, dependencies, build config
- `Dockerfile`: Container build configuration
- `.env.example`: Environment variable reference

**Core Logic:**
- `app/core/dector.py`: Script and language detection
- `app/engines/router.py`: Engine selection logic
- `app/core/cache.py`: Redis caching layer

**Testing:**
- `tests/`: All test files

## Naming Conventions

**Files:**
- Python modules: `lowercase_with_underscores.py`
- Test files: `test_*.py`
- Schemas: `*.py` (singular, e.g., `romanize.py`)

**Directories:**
- Python packages: `lowercase_with_underscores/`

**Classes:**
- PascalCase (e.g., `RomanizeRequest`, `ICUEngine`)

**Functions/Methods:**
- snake_case (e.g., `detect_script`, `route_romanization`)

## Where to Add New Code

**New API Endpoint:**
- Primary code: `app/api/{feature}.py`
- Schema: `app/schemas/{feature}.py`
- Tests: `tests/test_{feature}.py`

**New Romanization Engine:**
- Implementation: `app/engines/{script}_engine.py`
- Register in: `app/engines/router.py`
- Tests: Add to `tests/test_engines.py`

**New Core Service:**
- Implementation: `app/core/{service}.py`
- Tests: `tests/test_{service}.py`

## Special Directories

**`.venv/`:**
- Purpose: Python virtual environment
- Generated: Yes (local development)
- Committed: No (in .gitignore)

**`.pytest_cache/`:**
- Purpose: pytest cache
- Generated: Yes
- Committed: No

**`.ruff_cache/`:**
- Purpose: Ruff linter cache
- Generated: Yes
- Committed: No

---

*Structure analysis: 2026-03-18*
