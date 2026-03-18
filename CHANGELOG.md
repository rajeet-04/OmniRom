# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- `render.yaml` - One-click Render deployment configuration
- Graceful shutdown handler for clean Redis connection closure
- Rate limiting middleware (configurable via environment variables)
- MAX_FILE_LINES limit (default: 200 lines)

### Changed
- `Dockerfile`: Added `--timeout-keep-alive 30` to uvicorn command for load balancer compatibility
- `.env.example`: Left `REDIS_URL` blank by default, added rate limiting and file line limit settings
- `README.md`: Updated deployment instructions for Render
- `arabic_urdu_romanizer.py`: Fixed Urdu transliteration (implicit vowels, common word patterns)

### Fixed
- Urdu romanization: Added implicit 'a' vowel between consonant clusters (زخم → zakham)
- Urdu romanization: Fixed ہیں → hai (existential)
- Urdu romanization: Fixed پہ → pe (location marker)
- Urdu romanization: Fixed دوا → dua (not "do")
- Urdu romanization: Fixed دل → dil (not "dal")
