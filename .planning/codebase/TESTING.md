# Testing Patterns

**Analysis Date:** 2026-03-18

## Test Framework

**Runner:**
- pytest 8.0.0
- Config: `pytest.ini`

**Assertion Library:**
- pytest built-in assertions

**Run Commands:**
```bash
pytest tests/ -v               # Run all tests with verbose output
pytest tests/ -v --tb=short   # With short traceback
uv run pytest tests/ -v       # Using uv
```

## Test File Organization

**Location:**
- `tests/` directory (separate from source)

**Naming:**
- `test_*.py` pattern
- Organized by module: `test_api.py`, `test_engines.py`, `test_detector.py`

**Structure:**
```
tests/
├── test_api.py        # API endpoint tests
├── test_engines.py   # Engine unit tests
└── test_detector.py  # Script detection tests
```

## Test Structure

**Suite Organization:**
- Use pytest classes to group related tests
- Classes follow `Test*` naming convention
- Methods follow `test_*` naming convention

**Patterns:**

**Setup/Teardown:**
```python
def setup_method(self):
    """Called before each test method."""
    self.engine = ICUEngine()
```

**Example from `tests/test_engines.py`:**
```python
class TestICUEngine:
    """Tests for ICU/transliterate engine."""

    def setup_method(self):
        self.engine = ICUEngine()

    def test_cyrillic_romanization(self):
        result = self.engine.romanize("Привет", "cyrillic")
        assert result
        assert all(ord(c) < 128 for c in result.strip())
```

## Mocking

**Framework:** pytest (built-in)

**Patterns:**
- No mocking framework explicitly used
- Tests use actual engine implementations
- Redis cache gracefully degrades if not available

**What to Mock:**
- Not currently using mocks
- Consider mocking Redis for deterministic cache tests

**What NOT to Mock:**
- Romanization engines (test actual behavior)
- Script detection (test actual behavior)

## Fixtures and Factories

**Test Data:**
- Inline test strings
- No external fixtures or factories

**Location:**
- Inline in test methods

**Example:**
```python
def test_cyrillic_romanization(self):
    result = self.engine.romanize("Привет", "cyrillic")
    assert result
    assert all(ord(c) < 128 for c in result.strip())
```

## Coverage

**Requirements:** None enforced

**View Coverage:**
```bash
# Not currently configured
pytest --cov=app tests/
```

## Test Types

**Unit Tests:**
- Engine tests in `test_engines.py`
- Detector tests in `test_detector.py`
- Focus on individual components

**Integration Tests:**
- API tests in `test_api.py`
- Test full request/response cycle
- Use FastAPI TestClient

**Example from `tests/test_api.py`:**
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_romanize_cyrillic(self):
    response = client.post("/v1/romanize", json={"text": "Привет"})
    assert response.status_code == 200
    data = response.json()
    assert "romanized" in data
```

## Common Patterns

**Async Testing:**
- Uses `pytest-asyncio` (configured in `pytest.ini` with `asyncio_mode = auto`)
- TestClient handles async internally

**Error Testing:**
```python
def test_romanize_empty_text(self):
    response = client.post("/v1/romanize", json={"text": ""})
    assert response.status_code in (400, 422)
```

---

*Testing analysis: 2026-03-18*
