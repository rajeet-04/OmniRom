# Architecture

**Analysis Date:** 2026-03-18

## Pattern Overview

**Overall:** Layered API Architecture with Engine Router Pattern

**Key Characteristics:**
- FastAPI-based REST API
- Router-based engine selection
- Modular engine system for different scripts
- Optional caching layer
- Stateless request processing

## Layers

**API Layer (`app/api/`):**
- Purpose: HTTP request handling
- Location: `app/api/`
- Contains: Route handlers, request/response schemas
- Depends on: Core services, engines
- Used by: FastAPI application

**Core Services (`app/core/`):**
- Purpose: Business logic components
- Location: `app/core/`
- Contains: Language detection, caching, stats, styling
- Depends on: External libraries
- Used by: API layer

**Engine Layer (`app/engines/`):**
- Purpose: Script-specific romanization
- Location: `app/engines/`
- Contains: Multiple engine implementations (ICU, Chinese, Japanese, Korean, Indic, etc.)
- Depends on: External transliteration libraries
- Used by: Router

**Middleware (`app/middleware/`):**
- Purpose: Cross-cutting concerns
- Location: `app/middleware/`
- Contains: Logging middleware

## Data Flow

**Romanization Request Flow:**

1. Client POSTs to `/v1/romanize` with text
2. API validates request using Pydantic schema
3. Cache check (if Redis enabled) - return cached if hit
4. Script detection via `detect_script()` in `app/core/detector.py`
5. Router selects appropriate engine based on script type
6. Engine romanizes the text
7. Style transformation applied (optional)
8. Result cached (if enabled)
9. Stats recorded
10. Response returned

**State Management:**
- Stateless API (no session state)
- Redis for caching romanization results
- In-memory stats tracking

## Key Abstractions

**Romanization Engine:**
- Purpose: Abstract interface for different script types
- Examples: `ICUEngine`, `ChineseEngine`, `JapaneseEngine`, `KoreanEngine`, `IndicEngine`, `UromanEngine`
- Pattern: Class with `romanize(text, ...)` method

**Router:**
- Purpose: Select appropriate engine based on script
- Location: `app/engines/router.py`
- Pattern: Priority-based routing with fallback chain

**Cache Manager:**
- Purpose: Redis-backed caching
- Location: `app/core/cache.py`
- Pattern: Singleton with graceful degradation

## Entry Points

**Main Application:**
- Location: `app/main.py`
- Triggers: uvicorn startup
- Responsibilities: FastAPI app initialization, router registration, middleware setup

**API Endpoints:**
- `/v1/romanize` - Single text romanization
- `/v1/romanize/batch` - Batch processing
- `/v1/romanize/file` - File upload processing
- `/v1/languages` - Supported languages
- `/v1/engines` - Engine information
- `/v1/stats` - Usage statistics
- `/v1/cache/*` - Cache management

## Error Handling

**Strategy:** Exception catching with HTTPException

**Patterns:**
- Input validation via Pydantic
- Empty text validation (HTTP 400)
- Generic error catching with detailed messages (HTTP 500)
- Silent failure for cache/optional features

## Cross-Cutting Concerns

**Logging:** Custom LoggingMiddleware (`app/middleware/logging.py`)
**Validation:** Pydantic models in `app/schemas/`
**Authentication:** None (public API)

---

*Architecture analysis: 2026-03-18*
