Plan — short steps before diving in:
1. Detection: recommend layered detection (script 10 language) and specific libs to use.
2. Transliteration engines: pick per language-family, list pros/cons and fallbacks.
3. Caching & background: Redis key design + TTL/eviction + background worker choice.
4. Container/build/testing: Docker multi-stage + native deps notes + pytest examples.
5. API / observability / deployment: concrete config hints and production sizing.
6. Phase plan: prioritized step-by-step Phase 1 10 Phase 2 rollout with verification.

**Detection Options**
- **Approach**: two-stage pipeline 10 fast Unicode script detection first; if ambiguous or multi-script, run statistical language detection.
- **Unicode Script Detection (fast)**: use character script counts (Python `regex` module support for `\p{Script=...}` or iterate `unicodedata`). 
  - Pros: deterministic, extremely fast, handles short snippets with high precision for script-level dispatch (Devanagari vs Latin vs Han).
  - Cons: won't disambiguate languages that share a script (e.g., Serbian vs Croatian) or short Latin text.
- **Statistical Language Detection**: 
  - Recommend: `pycld3` (pip: `pycld3`) as primary (small, C++ backend, good for short text) and `langid` (pip: `langid`) as fallback if you want pure-Python.
  - Pros (`pycld3`): fast, good for short text; Cons: C++ build dependency. `langid`: no native deps, slightly less accurate on very short text.
- **Hybrid logic**:
  - If >80% characters belong to a single Unicode script 10 skip expensive detection and route to engine for that script.
  - Otherwise run `pycld3` and require a confidence threshold (e.g., >0.6). If below, mark as "ambiguous" and either fall back to a conservative engine (ICU/Unidecode) or ask user for source language.
- **Edge cases**: mixed-language input 10 split by script segments and transliterate each segment independently.

**Best Transliteration Engines (by family)**
- **General / many languages**
  - `PyICU` (pip: `PyICU`) 10 ICU transliterator `Any-Latin` etc.
    - Pros: broad coverage, well-tested; Cons: heavy native `libicu` dependency; some language-specific rules may be approximate.
- **Indic languages (Devanagari, Bengali, Tamil, etc.)**
  - `Aksharamukha` (pip: `aksharamukha`) 10 rule-based, many Indian scripts.
  - `ai4bharat` Indic transliteration (GitHub: ai4bharat/indic-transliteration; pip: `indic-transliteration` / `indic_transliteration`) 10 model-based and rule-based components.
    - Pros: high quality for Indic scripts, community-tested; Cons: different libs for different scripts and models may need extra data.
- **Chinese**
  - `pypinyin` (pip: `pypinyin`) for Mandarin Pinyin (tone removal/diacritics configuration).
  - `pycantonese` (pip: `pycantonese`) for Cantonese romanization.
    - Pros: tuned to phonetics, configurable style; Cons: need word segmentation for multi-character accuracy (use `jieba`).
- **Japanese**
  - `MeCab` tokenization (system package + `fugashi` pip) + `pykakasi` (pip: `pykakasi`) for kana 10 romaji.
    - Pros: accurate morphological segmentation + romaji conversion; Cons: MeCab native install and dictionary choice (Unidic recommended).
- **Korean**
  - `hangul-romanize` or `korean_romanizer` (check pip availability for your preferred style) OR small rule-based conversion using `jamo` decomposition.
    - Pros: deterministic Hangul decomposition; Cons: fewer maintained high-level libraries 10 prefer building on `jamo` for control.
- **Arabic / Hebrew**
  - `epitran` (pip: `epitran`) for many phonetic transliterations; for Arabic specifically `Buckwalter` transliteration (implement or use `camel-tools` for morphological context).
    - Pros: phonetic quality; Cons: installation of language data, and may require normalization/diacritic handling.
- **Fallbacks**
  - `Unidecode` (pip: `Unidecode`) 10 simple fallback for unknown scripts (best-effort).
  - **Recommendation**: implement an engine adapter layer so you can plug/unplug engines per language and version.

**Caching Strategies**
- **Store**: both detection results and transliteration outputs.
- **Backend**: Redis (single source for cache + optional job broker).
- **Key design**:
  - Use a stable canonicalization first: normalize text (Unicode NFKC), trim, collapse whitespace, and remove ignorable chars.
  - Key format example:
    - `rom:cache:v1:det:{sha256(normalized_text)}`
    - `rom:cache:v1:trans:{sha256(normalized_text)}:{src_lang}:{engine}:{engine_version}`
  - Store JSON value: {result, engine, engine_version, created_at, input_len, meta}.
- **TTL & Eviction**:
  - Detection (fast): TTL short 10 1 hour to 24 hours (e.g., 1h) because language detection outcomes can vary with upstream changes.
  - Transliteration results: TTL longer 10 7 days to 30 days depending on storage budget. Consider infinite TTL for deterministic engines but set TTL if memory-limited.
  - Redis config: `maxmemory` set, `maxmemory-policy` = `allkeys-lru` (or `volatile-lru` if you attach TTLs). For production prefer Redis Cluster or managed Redis with eviction policies.
- **Cache invalidation**:
  - Version engine into keys (engine_version) so updating rules/models invalidates old cached entries automatically.
- **Sizing**:
  - Estimate average output size 10 expected QPS 10 TTL window to pick Redis memory.

**Background Processing**
- **Options**:
  - FastAPI `BackgroundTasks`: good for light, short-lived non-critical tasks (e.g., async cache writes, metrics increments).
    - Pros: no external broker; Cons: tied to worker process lifecycle — not reliable for long-running tasks or retries.
  - RQ (Redis Queue; pip: `rq`): simple, Redis-only job queue.
    - Pros: small operational surface, easy to run, good for Phase 1 async tasks (batch transliteration, post-processing).
    - Cons: fewer features vs Celery (scheduling plugins exist).
  - Celery (pip: `celery`) with Redis or RabbitMQ broker:
    - Pros: mature, feature-rich (retries, scheduling, chord/chain workflows), observability support; Cons: heavier operationally and more moving parts.
- **Recommendation**:
  - Phase 1: use `RQ` for background batch jobs and scheduled reprocessing + FastAPI `BackgroundTasks` for in-request lightweight tasks.
  - Phase 2 (if you need complex workflows / high scale): migrate to Celery.
- **Worker sizing & concurrency**:
  - Start with 1 worker per CPU core, adjust based on job duration; use concurrency pools (threads/processes) depending on engine thread-safety.

**Containerization & Dependency Management**
- **Base image**: `python:3.11-slim` (or your org's supported Python).
- **Multi-stage Dockerfile pattern**:
  - Stage 1: builder 10 install `build-essential`, `libicu-dev`, `mecab`, `mecab-ipadic-utf8`/`unidic` + other dev-libs, install wheels with `pip wheel -r requirements.txt`.
  - Stage 2: runtime 10 copy wheels, install via `pip install --no-index --find-links /wheels ...`, minimal apt packages only for runtime (e.g., `libicu`).
- **Native deps**:
  - Document required apt packages in Dockerfile with pinned apt versions where necessary:
    - `libicu-dev` for PyICU
    - `mecab`, `mecab-ipadic-utf8` or `unidic` for Japanese tokenization
    - `build-essential`, `python3-dev` for building wheels
  - Use `--no-cache` for apt and `--no-cache-dir` for pip installs.
- **Example Dockerfile skeleton**:
  - Brief: install system deps 10 build wheel stage 10 copy minimal runtime.
- **Dependency pinning**:
  - Use `requirements.txt` with strict pins or a `constraints.txt` file; produce and commit a `requirements.lock` (from `pip freeze`) for reproducibility.
- **Binary packaging**:
  - For heavy native libraries consider building wheels in CI and hosting them (or use manylinux wheels).
- **Security**:
  - Run as non-root user in container; scan images with `trivy`.

**Testing Recommendations**
- **Unit tests**:
  - Use `pytest`.
  - Mock transliteration engines using `pytest-mock` to isolate code paths.
  - Test canonicalization, redis key building, and error-handling branches.
- **Integration tests**:
  - Use FastAPI `TestClient` (starlette) for endpoint tests.
  - Run a test Redis instance (use `pytest-redis` or `docker-compose` test setup) for cache behavior validation.
  - Include golden test cases (input 10 exact expected romanization) for top 10 languages.
- **Sample test cases to include (phase 1)**:
  - Hindi (Devanagari): "हेलो दुनिया" 10 expected romanization using configured engine.
  - Mandarin: "中文测试" 10 expected pinyin.
  - Japanese mixed script: "東京大学" 10 expected romaji.
  - Korean Hangul: "안녕하세요" 10 expected.
  - Mixed Latin + non-Latin: "Hello 世界" 10 transliterate Chinese segment only.
- **CI**:
  - GitHub Actions: lint (flake8/ruff), unit tests, integration tests in matrix (Python versions).
- **Load & smoke tests**:
  - Use `locust` or `k6` to simulate transliteration QPS and queue/backlog behavior.

**API Design Refinements**
- **Endpoint**:
  - POST `/v1/transliterate` request body:
    - `text` (string, required), `source` (optional ISO code), `target` (e.g., `Latin`), `engine` (optional), `options` (tones, case, punctuation), `async` (bool for background job).
- **Responses**:
  - Success: `{result: string, segments: [{text, src_script, src_lang, engine}], meta: {...}}`
  - Error format: `{code: "ERR_CODE", message: "Human message", details: {...}}`
- **Error handling**:
  - 400: invalid input, missing text.
  - 413: payload too large (enforce `max_chars`).
  - 422: invalid option value.
  - 429: rate-limited.
  - 500: internal error with request-id for tracing.
- **Rate limiting**:
  - Implement via Redis-based token bucket. Libraries: `slowapi` (pip: `slowapi`), or `fastapi-limiter` (Redis-backed).
  - Default suggestion: 60 req/min per IP with burst 120; also implement per-API-key limits for authenticated clients.
- **Size limits & safety**:
  - Default `max_chars` 10_000; configurable via env var.
  - Reject single requests that exceed a hard cap (e.g., 100k).
- **Batching & streaming**:
  - Support batch lists with per-item keys and progressive responses; use streaming WebSocket or server-sent events for long batches.

**Observability**
- **Metrics**:
  - Use `prometheus_client` to expose `/metrics`.
  - Key metrics: `requests_total`, `requests_duration_seconds` (histogram by language/engine), `cache_hit_total`, `cache_miss_total`, `queue_length`.
- **Logging**:
  - Structured JSON logs via `python-json-logger` or `structlog`.
  - Include request-id, user/client-id, engine and engine_version, input length.
- **Tracing**:
  - Integrate OpenTelemetry (pip: `opentelemetry-api`, `opentelemetry-sdk`, `opentelemetry-instrumentation-fastapi`) and export to Jaeger.
- **Dashboards & alerts**:
  - Grafana dashboards for latency, cache hit ratio, queue depth. Alerts for high error rate (>1%) and queue backlog > threshold.
- **Profiling**:
  - Use `py-spy` or `scalene` in staging to find CPU hotspots in transliteration.

**Deployment & Production Sizing**
- **Runtime**:
  - Use Uvicorn workers behind Gunicorn or use `uvicorn` with multiple workers via process manager.
  - Worker count: start with `workers = 2 * CPU + 1` (tune).
  - Use async I/O for requests but call CPU-bound transliteration via thread/process pools or background workers.
- **Machine sizing (starter guidance)**:
  - Lightweight config (low throughput): 1 vCPU, 2 GB RAM (for lightweight engines + cache remote).
  - Medium (mixed engines like PyICU, pykakasi): 2	6 vCPU, 4	8 GB RAM.
  - Heavy (epitran, large engineered pipelines): 4+ vCPU, 8	16 GB RAM.
- **Autoscaling hints**:
  - Horizontal scale API pods in Kubernetes using CPU + custom metrics (Prometheus adapter) such as queue length or request latency.
  - Autoscale worker set based on queue backlog.
- **Storage & network**:
  - Use managed Redis (for HA) and store logs centrally (ELK / Loki).
- **High availability**:
  - Run multiple API pods behind a load balancer, use Redis Sentinel/Cluster or managed provider.

**Recommended Stack (concise)**
- **Web**: FastAPI + Uvicorn/Gunicorn
- **Detection**: `regex` script detection + `pycld3`
- **Transliteration engines**: `PyICU`, `Aksharamukha`, `pypinyin`, `pykakasi` + `fugashi/MeCab`, `epitran`, `Unidecode` fallback
- **Cache & Broker**: Redis (cache + RQ broker)
- **Async jobs**: RQ (Phase 1), migrate to Celery if needed
- **Testing**: pytest + TestClient, GitHub Actions
- **Observability**: `prometheus_client`, OpenTelemetry, Grafana, structured JSON logs
- **Container**: Docker multi-stage, apt install native libs (libicu, mecab)
- **CI/CD**: GitHub Actions + image scanning (trivy) + deployment to Kubernetes (recommended) or ECS.

**Phase-by-Phase Implementation Plan (priority + verifications)**

Phase 1 10 Minimal viable service (deliverable within weeks)
1. Implement detection pipeline:
   - Script detector 10 `pycld3` fallback.
   - Verification: unit tests + sample inputs produce expected `script` and `lang` fields.
2. Build engine adapter layer:
   - Define interface `transliterate(text, src_lang, options)` and adapter for `PyICU`, `pypinyin`, `pykakasi`, `aksharamukha`.
   - Verification: golden integration tests (Hindi, Chinese, Japanese, Korean).
3. API endpoint `/v1/transliterate`:
   - Support sync & async (`async` flag).
   - Add input validation, size limit enforcement.
   - Verification: fastapi TestClient tests + CI.
4. Redis cache for transliterations:
   - Implement key schema and TTL (default 7d).
   - Use `BackgroundTasks` to write cache asynchronously.
   - Verification: test cache hit/miss metrics and key schema correctness.
5. Containerize with Dockerfile multi-stage; include native deps for chosen engines.
   - Verification: build image in CI, run integration container tests.
6. Add basic observability:
   - Expose `/metrics`, structured logging, simple Prometheus dashboard.
   - Verification: metrics present; example dashboard visualized in staging.

Phase 2 10 Scale, reliability, and extended coverage
1. Introduce RQ workers (or Celery if needed) for heavy/batch jobs; add retry/backoff.
   - Verification: queue backlog processing under load tests.
2. Expand language coverage adding `epitran`, additional Indic models, Cantonese, Arabic refinements.
   - Verification: add golden tests, CI extended integration matrix.
3. Harden caching, configure Redis cluster and eviction policy.
   - Verification: soak test under traffic with eviction and TTL behavior monitored.
4. Add rate limiting, API keys, quotas and billing hooks if needed.
   - Verification: abuse tests (simulate bursts), validate quota enforcement.
5. Improve observability: OpenTelemetry traces, alerts for suspicious error/latency patterns.
   - Verification: end-to-end tracing, alert firing in staging.
6. Autoscaling & infra:
   - Deploy on Kubernetes with HPA using CPU + custom Prometheus metric (queue length).
   - Verification: scale-up/scale-down tests with load controller.

**Concrete config hints / snippets**
- Redis key example (Python):
  - `key = f"rom:cache:v1:trans:{sha256(normalized_text).hexdigest()}:{src_lang}:{engine}:{engine_version}"`
- Rate-limit suggestion (env):
  - `RATE_LIMIT=60/min` and burst `120`.
- Max payload config (env):
  - `MAX_CHARS=10000`
- Docker apt snippet (builder stage):
  - `apt-get update && apt-get install -y build-essential libicu-dev mecab libmecab-dev mecab-ipadic-utf8 && rm -rf /var/lib/apt/lists/*`

Final small checklist to start Phase 1 (actionable)
- Create `/v1/transliterate` FastAPI endpoint scaffold (input validation).
- Add detection module (script + `pycld3`), and write unit tests.
- Implement engine adapter interface and add `PyICU` + `pypinyin` + `pykakasi` adapters.
- Add Redis caching layer and background cache writes.
- Add Dockerfile multi-stage and CI job to build/test image.
- Add Prometheus metrics endpoints and basic Grafana dashboard stub.

Would you like me to scaffold the FastAPI project (endpoints, detection module, adapters, tests) now, or produce the Dockerfile + requirements.txt and sample CI config to commit first?
