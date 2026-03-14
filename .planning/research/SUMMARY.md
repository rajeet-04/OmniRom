# Research Summary: Free OmniRom Implementation

**Project:** Universal Romanization Service (OmniRom)
**Researched:** March 14, 2026
**Overall Confidence:** HIGH

## Executive Summary

This project can be built **100% free** with no paid resources. Every component in the original roadmap has a free alternative. The recommended stack uses Render for hosting, Aiven Valkey (Redis-compatible) for caching, and GitHub's free services for everything else.

## Key Findings

### Free Stack Recommendation

| Original Component | Free Alternative | Cost |
|-------------------|------------------|------|
| FastAPI Backend | Python + FastAPI | $0 |
| Hosting (was paid option) | **Render** | Free |
| Redis Cache | **Aiven Valkey** | Free (30MB) |
| RabbitMQ | Redis (built-in) | $0 |
| Docker Registry | **GitHub Container Registry** | Free |
| CI/CD | **GitHub Actions** | Free |
| NLP Engines | ICU, uroman, pypinyin, etc. | $0 (open source) |

## Roadmap Implications

All 4 phases can be completed with **zero cost**:

1. **Phase 1 (Foundation)** - Deploy to Render, use Aiven Valkey for caching, ICU+uroman for fallback
2. **Phase 2 (Specialists)** - Add AI4Bharat, pypinyin, MeCab - all open source
3. **Phase 3 (Performance)** - Celery runs alongside FastAPI on Render
4. **Phase 4 (Advanced)** - Style parameters in code; skip LLM or use Ollama locally

## Phase-Specific Notes

| Phase | Free Implementation | Potential Issue |
|-------|---------------------|-----------------|
| Phase 1 | Render + Aiven | None |
| Phase 2 | Same stack + open source NLP libs | None |
| Phase 3 | Add Celery worker | May need hobby tier ($5/mo) for background tasks |
| Phase 4 | Add Prometheus + Grafana | Use free UptimeRobot instead |

## Confidence Assessment

| Area | Level | Reason |
|------|-------|--------|
| Hosting | HIGH | Render documented, free tier works |
| Caching | HIGH | Aiven Valkey confirmed free without CC |
| Container Registry | HIGH | GHCR fully free |
| CI/CD | HIGH | GitHub Actions generous |
| NLP Libraries | HIGH | All open source verified |

## Gaps to Address

- **Celery on Render:** Single worker on free tier may have limitations. Test and upgrade to hobby ($5/mo) only if needed.
- **LLM for chat style:** Skipping for free tier - would need GPU. Could explore Ollama on local machine for development.

## Files Created

| File | Purpose |
|------|---------|
| `.planning/research/FREE_ALTERNATIVES.md` | Detailed free stack research |

## Quick Start

```bash
# 1. Deploy to Render (free, no CC)
# Connect GitHub → New Web Service → Select repo
# Build: pip install -r requirements.txt
# Start: uvicorn main:app --host 0.0.0.0 --port $PORT

# 2. Get free Redis cache
# Sign up at aiven.io → Create Valkey → Get connection string

# 3. Set environment variables in Render:
# REDIS_URL = <aiven_connection_string>
```
