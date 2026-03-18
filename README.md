# OmniRom

**Universal Romanization Service** - Convert text from any script to Latin characters.

## Features

- 🌐 **Multi-script support**: Cyrillic, Greek, Arabic, Hebrew, Devanagari, Bengali, Tamil, Telugu, Malayalam, Kannada, Gujarati, Punjabi, Chinese, Japanese, Korean, and more
- 🎨 **Multiple styles**: standard, academic (diacritics), chat (informal), phonetic
- ⚡ **Redis caching**: Repeated requests return instantly (Aiven Valkey)
- 📦 **Batch processing**: Up to 100 texts in a single request
- 📁 **File processing**: Upload `.txt`, `.csv`, or `.srt` files
- 📊 **Usage stats**: Built-in request tracking

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API
uvicorn app.main:app --reload

# Or with uv
uv run uvicorn app.main:app --reload
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Welcome message |
| `POST` | `/` | Romanize single text (main endpoint) |
| `GET` | `/health` | Health check |
| `POST` | `/v1/romanize` | Romanize single text |
| `POST` | `/v1/romanize/batch` | Romanize up to 100 texts |
| `POST` | `/v1/romanize/file` | Romanize a file (.txt, .csv, .srt) |
| `GET` | `/v1/languages` | List supported languages & styles |
| `GET` | `/v1/engines` | List available romanization engines |
| `GET` | `/v1/stats` | API usage statistics |
| `GET` | `/v1/cache/stats` | Cache statistics |
| `POST` | `/v1/cache/clear` | Clear all cached results |
| `GET` | `/docs` | Interactive API docs (Swagger UI) |

## Examples

### Root Endpoint (Main Romanization)

```bash
# Basic romanization
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Привет мир"}'

# With style option
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{"text": "مرحبا بالعالم", "style": "standard"}'

# Urdu lyrics romanization
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{"text": "[00:14.06] زخم دل پہ ہیں، دوا کرو", "style": "standard"}'
```

Response:
```json
{
  "original": "[00:14.06] زخم دل پہ ہیں، دوا کرو",
  "romanized": "[00:14.06] zam dal pe hai, do karo",
  "detected_lang": "ur",
  "detected_script": "Arabic",
  "engine_used": "arabic-urdu-romanizer"
}
```

### Single Romanization

```bash
curl -X POST http://localhost:8000/v1/romanize \
  -H "Content-Type: application/json" \
  -d '{"text": "Привет мир"}'
```

Response:
```json
{
  "original": "Привет мир",
  "romanized": "Privet mir",
  "metadata": {
    "detected_lang": "ru",
    "detected_script": "Cyrillic",
    "engine_used": "icu",
    "cached": false,
    "processing_time_ms": 42
  }
}
```

### Style Options

```bash
# Academic style (diacritics)
curl -X POST http://localhost:8000/v1/romanize \
  -d '{"text": "नमस्ते", "style": "academic"}'

# Chat style (no diacritics)
curl -X POST http://localhost:8000/v1/romanize \
  -d '{"text": "नमस्ते", "style": "chat"}'
```

### Batch Processing

```bash
curl -X POST http://localhost:8000/v1/romanize/batch \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Привет", "你好", "안녕하세요", "こんにちは"]}'
```

## Supported Scripts

| Language | Script | Engine |
|----------|--------|--------|
| Arabic, Urdu, Persian | Arabic | Google Translate + Arabic/Urdu Romanizer |
| Russian, Ukrainian, Bulgarian | Cyrillic | transliterate |
| Greek | Greek | transliterate |
| Hebrew | Hebrew | unidecode |
| Hindi | Devanagari | rule-based |
| Chinese | Han | pypinyin |
| Japanese | Kana/Kanji | kana-map + unidecode |
| Korean | Hangul | unidecode |
| Any other | Universal | unidecode |

> **Note**: For Arabic/Urdu/Persian, the system first tries Google Translate for romanization. If Google returns an English translation instead of romanized text, it automatically falls back to the rule-based Arabic/Urdu Romanizer.

## Testing Examples

### Python

```python
import requests

url = "http://localhost:8000/"
payload = {
    "text": "[00:14.06] زخم دل پہ ہیں، دوا کرو\n[00:16.70] آؤ، مل کے رسمِ محبت ادا کرو",
    "style": "standard"
}

response = requests.post(url, json=payload)
result = response.json()

print(result["romanized"])
# Output: [00:14.06] zam dal pe hai, do karo
#         [00:16.70] aao, mil ke rasami mohabbat da karo
```

## Deployment

### Render (Free Tier) - One-Click Deploy

1. Connect your GitHub repository to Render
2. Render will auto-detect the `render.yaml` configuration
3. Optionally set environment variables in Render dashboard:
   - `REDIS_URL`: Leave blank to disable caching (or add Aiven Valkey for caching)
   - `RATE_LIMIT_REQUESTS`: Maximum number of requests allowed per client within each rate limit window (uses an internal default if unset)
   - `RATE_LIMIT_WINDOW`: Length of the rate limit window in seconds (uses an internal default if unset)
   - `MAX_FILE_LINES`: Maximum number of lines accepted per uploaded file before processing is rejected (uses an internal default if unset)

Or manually configure:
1. Connect your GitHub repository
2. Set **Build Command**: `pip install -r requirements.txt`
3. Set **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --timeout-keep-alive 30`

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `REDIS_URL` | Aiven Valkey connection string (leave blank to disable caching) | No |
| `RATE_LIMIT_REQUESTS` | Maximum number of requests allowed per client within each rate limit window (uses an internal default if unset) | No |
| `RATE_LIMIT_WINDOW` | Length of the rate limit window in seconds (uses an internal default if unset) | No |
| `MAX_FILE_LINES` | Maximum number of lines accepted per uploaded file before processing is rejected (uses an internal default if unset) | No |

## Development

```bash
# Install dev dependencies
uv sync

# Run tests
uv run pytest tests/ -v

# Run with hot reload
uv run uvicorn app.main:app --reload
```

## License

    GNU GENERAL PUBLIC LICENSE
    Version 3, 29 June 2007
