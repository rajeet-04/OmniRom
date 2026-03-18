# Coding Conventions

**Analysis Date:** 2026-03-18

## Naming Patterns

**Files:**
- Python modules: lowercase with underscores (e.g., `romanize.py`, `cache_manager.py`)
- Test files: `test_*.py` prefix

**Functions:**
- snake_case (e.g., `detect_script`, `route_romanization`, `get_cache`)

**Variables:**
- snake_case (e.g., `romanized_text`, `script_type`)

**Types/Classes:**
- PascalCase (e.g., `RomanizeRequest`, `ICUEngine`, `CacheManager`)

**Constants:**
- UPPER_SNAKE_CASE for module-level constants (e.g., `ICU_SCRIPTS`, `HIRAGANA_MAP`)

## Code Style

**Formatting:**
- No explicit formatter configured (no ruff, black, or pre-commit)
- Standard Python PEP 8 conventions expected

**Linting:**
- Not configured (no ruff or pylint in use)

**Type Hints:**
- Used in function signatures (e.g., `def romanize(text: str) -> str`)
- Not enforced with mypy

## Import Organization

**Order:**
1. Standard library imports (e.g., `import time`, `import re`)
2. Third-party imports (e.g., `from fastapi import ...`, `import redis`)
3. Local application imports (e.g., `from app.core.detector import ...`)

**Path Aliases:**
- None configured
- Relative imports from `app` package

**Example from `app/api/romanize.py`:**
```python
import time
from fastapi import APIRouter, HTTPException
from app.schemas.romanize import RomanizeRequest, RomanizeResponse
from app.core.detector import detect_script, get_script_type
from app.engines.router import route_romanization, get_supported_engines
from app.core.cache import get_cache
from app.core.stats import get_stats
```

## Error Handling

**Patterns:**
- Use FastAPI's `HTTPException` for HTTP errors
- Catch generic `Exception` in endpoint handlers
- Return HTTP 400 for validation errors
- Return HTTP 500 for processing failures
- Cache failures silently degrade (no exception)

**Example from `app/api/romanize.py`:**
```python
try:
    # ... processing ...
except Exception as e:
    stats.record_error()
    raise HTTPException(
        status_code=500, detail=f"Romanization failed: {str(e)}"
    )
```

## Logging

**Framework:** Python `logging` module

**Patterns:**
- Custom `LoggingMiddleware` in `app/middleware/logging.py`
- Configurable via `LOG_LEVEL` environment variable (default: INFO)
- Use in endpoint handlers for timing information

## Comments

**When to Comment:**
- Complex algorithms (see `arabic_urdu_romanizer.py`)
- Document strategy/approach at module level
- Explain non-obvious behavior

**Docstrings:**
- Use Google-style docstrings in some files
- Not consistently applied across codebase

**Example from `app/core/detector.py`:**
```python
def detect_script(text: str) -> dict:
    """
    Detect the script/language of input text.

    Returns dict with:
    - language: ISO 639-1 code
    - script: Script name
    - reliable: Whether detection is reliable
    - probability: Confidence score
    - script_code: ISO 15924 script code
    """
```

## Function Design

**Size:** Varies; typically one responsibility per function

**Parameters:**
- Type hinted
- Default values where appropriate

**Return Values:**
- Type hinted
- Use tuples for multiple returns (e.g., `Tuple[str, str]`)

## Module Design

**Exports:**
- Use explicit imports from modules
- No `__all__` defined

**Barrel Files:**
- Not used (`__init__.py` files are empty or minimal)

---

*Convention analysis: 2026-03-18*
