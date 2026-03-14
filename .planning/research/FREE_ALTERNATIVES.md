# Free Alternatives Research: OmniRom Project

**Project:** Universal Romanization Service (OmniRom)
**Researched:** March 14, 2026
**Overall Confidence:** HIGH

## Executive Summary

The OmniRom project (a universal romanization/transliteration API) can be built entirely with free resources. The key finding is that every component in the roadmap has a free alternative, though some platforms have usage limits. The best approach is a combination of **Render** (web hosting), **Aiven/Valkey** (Redis alternative), and **GitHub Container Registry** (Docker images).

---

## Free Stack Recommendations

### 1. API Hosting (Backend)

| Option | Free Tier | Limitations | Verdict |
|--------|-----------|-------------|---------|
| **Render** | Free web service | 750 hrs/month, 30-60s cold starts | ✅ Best for FastAPI |
| **Railway** | $5/month credits ($20 with referral) | Usage-based, stops after credits | ⚠️ Good, needs billing |
| **Vercel** | Serverless functions | 100hrs compute, requires CC | ⚠️ Cold starts |
| **Deta Space** | Free personal cloud | Limited scaling | ⚠️ New platform |

**Recommendation:** Render - no credit card required, straightforward FastAPI deployment, 750 free hours/month is enough for personal use.

**Source:** [Render Free Tier](https://render.com/docs/deploy-fastapi), [DeployBase Comparison](https://deploybase.app/blog/render-free-tier-complete-guide-2026)

---

### 2. Caching (Redis Alternative)

| Option | Free Tier | Type | Notes |
|--------|-----------|------|-------|
| **Aiven Valkey** | 30MB, 1 entry | Redis-compatible | ✅ Best free option |
| **Redis Cloud** | 30MB, 30 connections | Redis | ✅ Requires CC |
| **Upstash** | 10K commands/day | Redis + HTTP API | ⚠️ Limited daily |
| **Railway Redis** | $5 credit | Redis | ⚠️ Requires billing |

**Recommendation:** Aiven Valkey - truly free (no CC), Redis-compatible, 30MB is plenty for caching romanization results.

**Source:** [Aiven Free Valkey](https://aiven.io/free-redis-database), [HostAdvice Free Redis](https://hostadvice.com/dedicated-servers/redis-hosting/free/)

---

### 3. Task Queue (Celery + RabbitMQ Alternative)

| Option | Free Tier | Type |
|--------|-----------|------|
| **Redis** | 30MB (Aiven) | Broker + Result Backend |
| **QStash (Upstash)** | 1K messages/day | Serverless MQ |
| **CloudAMQP** | Free tier (Lemur) | RabbitMQ |

**Recommendation:** Use Redis as both cache AND Celery broker. Celery can use Redis as a message broker without extra cost. No need for separate RabbitMQ.

**Source:** [Upstash QStash](https://buildmvpfast.com/alternatives/upstash)

---

### 4. Container Registry

| Option | Free Tier | Notes |
|--------|-----------|-------|
| **GitHub Container Registry (GHCR)** | Unlimited public, 500MB private | ✅ Best option |
| **Docker Hub** | 1 private repo | Rate limits apply |
| **GitLab Container Registry** | 10GB storage | With GitLab account |

**Recommendation:** GitHub Container Registry - free, unlimited public images, integrates with GitHub Actions.

**Source:** [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

---

### 5. CI/CD (GitHub Actions)

| Option | Free Tier | Notes |
|--------|-----------|-------|
| **GitHub Actions** | 2000 min/month (public), 500 min (private) | ✅ Excellent |
| **GitLab CI/CD** | Unlimited | Also free |

**Recommendation:** GitHub Actions - free for public repos, generous for private, native Docker build/push support.

---

### 6. NLP Engines (All Free Already!)

All the romanization libraries in your roadmap are already **open source and free**:

- **ICU (PyICU)** - ✅ Open source
- **uroman** - ✅ Open source  
- **AI4Bharat Indic-Xlit** - ✅ Open source (Apache 2.0)
- **pypinyin** - ✅ Open source (MIT)
- **MeCab** - ✅ Open source (BSD/GPL)
- **Cutlet** - ✅ Open source

---

## Architecture for Free Deployment

```
┌─────────────────────────────────────────────────────┐
│                    RENDER (Free)                    │
│  ┌─────────────────────────────────────────────┐    │
│  │              FastAPI App                    │    │
│  │  • Input Normalization                      │    │
│  │  • Script Detection (pycld3/langid)        │    │
│  │  • Router/Switchboard                       │    │
│  │  • Engine Layer (ICU, uroman, etc.)         │    │
│  │  • Post-processing                          │    │
│  │  • Celery (Redis broker)                    │    │
│  └─────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          │                              │
          ▼                              ▼
┌─────────────────┐            ┌─────────────────┐
│  AIVEN VALKEY   │            │  CELERY WORKER  │
│  (Redis Cache)  │            │  (Background    │
│  30MB Free      │            │   Tasks)        │
└─────────────────┘            │  Runs on same   │
                               │  Render service │
                               └─────────────────┘
```

---

## Recommended Free Stack Summary

| Component | Recommended Free Option | Notes |
|-----------|------------------------|-------|
| **Backend** | Python 3 + FastAPI | Local dev |
| **API Hosting** | Render | 750 hrs/mo free |
| **Caching** | Aiven Valkey | 30MB free, Redis-compatible |
| **Task Queue** | Celery + Redis | Same Redis as cache |
| **Container Registry** | GHCR (GitHub) | Unlimited public images |
| **CI/CD** | GitHub Actions | 2000 min/mo |
| **NLP Engines** | Open source libs | All free |

---

## Phase-by-Phase Free Implementation

### Phase 1: Foundation & MVP
- **Hosting:** Deploy to Render (free)
- **Caching:** Use Aiven Valkey (free)
- **Engines:** ICU + uroman (both open source)
- **Total Cost:** $0

### Phase 2: Integrating Specialists
- **Indic Languages:** AI4Bharat Indic-Xlit (free, self-hosted)
- **Chinese:** pypinyin (free)
- **Japanese:** MeCab + Cutlet (free)
- **Korean:** korean-romanizer (free)
- **Total Cost:** $0

### Phase 3: Performance & Reliability
- **Caching:** Already using Aiven Valkey
- **Batch Processing:** Celery worker on Render (background tasks)
- **File Processing:** Same - no extra cost
- **Total Cost:** $0

### Phase 4: Advanced Features
- **Style Parameters:** Built into your code (no cost)
- **LLM Post-processing:** ⚠️ Requires GPU - consider Ollama locally or skip for MVP
- **Monitoring:** UptimeRobot (free) + basic logging
- **Total Cost:** $0 (or ~$0 if skipping LLM)

---

## Potential Costs & Mitigations

| Potential Cost | When It Happens | Mitigation |
|----------------|-----------------|------------|
| Render limits exceeded | >750 hrs/month or high CPU | Use cache aggressively |
| Aiven Valkey limits | >30MB cache | Clear old entries |
| GitHub Actions minutes | >500 min private | Make repo public |
| Domain + SSL | Want custom domain | Render provides free SSL |

---

## Critical Notes

1. **Credit Card:** You can get running on Render without a credit card. Railway requires a small $1-5 payment.

2. **Cold Starts:** Render has 30-60s cold starts on free tier. Not ideal for production but fine for learning/MVP.

3. **Self-Hosting Engines:** All NLP engines run locally in your Python app - no API costs for things like Google Translate API.

4. **Scaling:** For high traffic, you'd eventually need to pay. But for personal use/MVP, the free tiers are generous.

---

## Confidence Assessment

| Area | Confidence | Reason |
|------|------------|--------|
| Hosting | HIGH | Render documentation verified |
| Caching | HIGH | Aiven Valkey confirmed free |
| Container Registry | HIGH | GHCR verified |
| NLP Libraries | HIGH | All open source confirmed |
| CI/CD | HIGH | GitHub Actions verified |

---

## Open Questions

- **Q:** Can Celery workers run on Render's free tier?
  - **A:** Render free tier is single-threaded. May need to upgrade to hobby ($5/mo) for background workers, or use synchronous processing initially.

- **Q:** Is 30MB cache enough?
  - **A:** For text romanization, yes. Each cached entry is small (text → romanized). 30MB holds hundreds of thousands of entries.

---

## Sources

- [Render FastAPI Deployment](https://render.com/docs/deploy-fastapi)
- [Aiven Free Valkey](https://aiven.io/free-redis-database)
- [GitHub Container Registry Docs](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [DeployBase Free Tier Comparison 2026](https://deploybase.app/blog/vercel-render-railway-netlify-free-tier-comparison-2026)
