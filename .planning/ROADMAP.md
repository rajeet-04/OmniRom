# OmniRom Roadmap

## Project: Universal Romanization Service

### Phase 1: Foundation & MVP
**Goal:** Establish the API shell, detection, and a universal fallback

**Requirements:**
- [F1-01] Initialize Git repository and Python virtual environment
- [F1-02] Set up FastAPI project structure (app/api, app/engines, app/core)
- [F1-03] Implement script detection (pycld3 or langid)
- [F1-04] Integrate ICU (PyICU) for rule-based transliteration
- [F1-05] Integrate uroman as universal fallback
- [F1-06] Build /v1/romanize POST endpoint
- [F1-07] Create Dockerfile and basic deployment config

**Plans:**
- [ ] 01-01-PLAN.md — Project setup and FastAPI shell
- [ ] 01-02-PLAN.md — Script detection + ICU integration
- [ ] 01-03-PLAN.md — uroman fallback + API endpoint

---

### Phase 2: Integrating the "Specialists"
**Goal:** Improve accuracy for complex language families

**Requirements:**
- [F2-01] Integrate AI4Bharat/Indic-Xlit (Hindi, Bengali, Tamil, etc.)
- [F2-02] Integrate pypinyin for Chinese
- [F2-03] Integrate MeCab + Cutlet for Japanese
- [F2-04] Integrate Korean Hangul romanizer
- [F2-05] Update Router logic for seamless engine handoff

**Plans:**
- [ ] 02-01-PLAN.md — Indic languages (AI4Bharat)
- [ ] 02-02-PLAN.md — Chinese (pypinyin) + Japanese (MeCab/Cutlet)
- [ ] 02-03-PLAN.md — Korean + Router update

---

### Phase 3: Performance & Reliability
**Goal:** Make the service production-ready and fast

**Requirements:**
- [F3-01] Implement Redis caching with hash lookups
- [F3-02] Add batch processing endpoint (/v1/romanize/batch)
- [F3-03] Implement file processing endpoint (.txt, .csv, .srt)
- [F3-04] Write unit tests (pytest)

**Plans:**
- [ ] 03-01-PLAN.md — Redis caching layer
- [ ] 03-02-PLAN.md — Batch and file processing
- [ ] 03-03-PLAN.md — Tests and reliability

---

### Phase 4: Advanced Features
**Goal:** Differentiate from Google/Azure APIs

**Requirements:**
- [F4-01] Add style parameter (academic, chat, phonetic)
- [F4-02] Explore lightweight LLM for chat style post-processing (OPTIONAL - requires GPU)
- [F4-03] Setup monitoring (UptimeRobot + basic logging)

**Plans:**
- [ ] 04-01-PLAN.md — Style parameters
- [ ] 04-02-PLAN.md — Monitoring and polish

---

## Dependencies
- Phase 1 must complete before Phase 2
- Phase 2 must complete before Phase 3
- Phase 3 must complete before Phase 4
