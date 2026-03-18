# Codebase Concerns

**Analysis Date:** 2026-03-18

## Tech Debt

**Optional Dependencies Without Proper Type Guards:**
- Issue: `app/core/cache.py` has type errors when Redis is not available
- Files: `app/core/cache.py`, `app/engines/japanese_engine.py`
- Impact: LSP/type checker warnings, but runtime gracefully handles missing optional deps
- Fix approach: Add proper `TYPE_CHECKING` guards or use `None` checks consistently

**Missing Type Hints:**
- Issue: Some functions lack complete type annotations
- Files: `app/core/detector.py` (line 92: `import math` inside function)
- Impact: Reduced code clarity, harder static analysis
- Fix approach: Add complete type hints, move imports to module level

**LSP Errors in Core Files:**
- Issue: Multiple LSP type errors in `app/engines/router.py`, `app/core/cache.py`, `app/engines/japanese_engine.py`
- Files: `app/engines/router.py` (lines 42, 108: None not assignable to str)
- Impact: Developer confusion, potential runtime issues if assumptions are wrong
- Fix approach: Fix null handling and type annotations

## Known Bugs

**No bugs identified in current codebase.**

## Security Considerations

**CORS Allows All Origins:**
- Risk: `allow_origins=["*"]` in `app/main.py`
- Files: `app/main.py` (lines 20-26)
- Current mitigation: None
- Recommendations: Restrict to specific origins in production

**No Input Rate Limiting:**
- Risk: No protection against abuse/DoS
- Files: `.env.example` mentions rate limiting as "not yet implemented"
- Current mitigation: None
- Recommendations: Add rate limiting middleware

## Performance Bottlenecks

**Script Detection Uses String Operations:**
- Problem: Unicode name lookups for every character
- Files: `app/core/detector.py` (`_detect_script_from_unicode` function)
- Cause: Iterating characters and checking Unicode names is O(n)
- Improvement path: Use Unicode block ranges instead of name matching

**No Request Size Limits:**
- Problem: No explicit limit on single request text size
- Files: `app/api/romanize.py`
- Cause: Not configured
- Improvement path: Add request size validation

## Fragile Areas

**Engine Fallback Chain:**
- Files: `app/engines/router.py` (`_route_to_engine` function)
- Why fragile: If an engine fails silently, falls through to next engine - might give unexpected output
- Safe modification: Test each engine individually before adding new fallback
- Test coverage: Basic engine tests exist

**Arabic/Urdu Romanizer:**
- Files: `app/engines/arabic_urdu_romanizer.py` (361 lines, complex algorithm)
- Why fragile: Complex rule-based algorithm with many edge cases
- Safe modification: Add comprehensive test cases before changing rules
- Test coverage: No dedicated tests (relies on integration tests)

## Scaling Limits

**Stateless but Cache-Dependent:**
- Current capacity: Scales horizontally easily
- Limit: Redis becomes single point of failure or bottleneck
- Scaling path: Use Redis cluster or remove cache dependency

**In-Memory Stats:**
- Current capacity: Single instance works fine
- Limit: Stats reset on restart, not shared across instances
- Scaling path: Use Redis for stats or accept per-instance stats

## Dependencies at Risk

**langid:**
- Risk: May not detect all languages accurately
- Impact: Incorrect routing to wrong engine
- Migration plan: Consider `fasttext-langdetect` or language-specific detection

**cutlet (Japanese):**
- Risk: Optional dependency that requires MeCab
- Impact: Japanese romanization falls back to basic mapping
- Migration plan: Document MeCab installation for production

## Missing Critical Features

**Rate Limiting:**
- Problem: No rate limiting configured
- Blocks: Safe production deployment without external protection

**Request Validation:**
- Problem: No max text length validation
- Blocks: Protection against memory exhaustion attacks

**Structured Logging:**
- Problem: Basic logging, no structured logs for monitoring
- Blocks: Easy integration with log aggregation systems

## Test Coverage Gaps

**No Cache Tests:**
- What's not tested: Cache hit/miss behavior, TTL, clear operations
- Files: `app/core/cache.py`
- Risk: Cache bugs not caught until production
- Priority: Medium

**No Batch Performance Tests:**
- What's not tested: Large batch handling (100 texts)
- Files: `app/api/batch.py`
- Risk: Performance issues with max batch size
- Priority: Low

**No File Upload Tests:**
- What's not tested: File processing endpoints
- Files: `app/api/files.py`
- Risk: File handling bugs not caught
- Priority: Medium

**No Style Transformation Tests:**
- What's not tested: Different romanization styles (academic, chat, phonetic)
- Files: `app/core/styler.py`
- Risk: Style transformations may not work correctly
- Priority: Low

---

*Concerns audit: 2026-03-18*
