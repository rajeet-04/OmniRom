"""Languages and styles listing endpoint."""

from fastapi import APIRouter

router = APIRouter(prefix="/v1", tags=["languages"])


@router.get("/languages")
async def list_supported_languages():
    """List all supported languages, scripts, and styles."""
    return {
        "languages": [
            {"code": "ru", "name": "Russian", "script": "Cyrillic", "engine": "icu"},
            {"code": "uk", "name": "Ukrainian", "script": "Cyrillic", "engine": "icu"},
            {"code": "bg", "name": "Bulgarian", "script": "Cyrillic", "engine": "icu"},
            {"code": "el", "name": "Greek", "script": "Greek", "engine": "icu"},
            {"code": "ar", "name": "Arabic", "script": "Arabic", "engine": "icu"},
            {"code": "he", "name": "Hebrew", "script": "Hebrew", "engine": "icu"},
            {"code": "hi", "name": "Hindi", "script": "Devanagari", "engine": "indic"},
            {"code": "bn", "name": "Bengali", "script": "Bengali", "engine": "indic"},
            {"code": "ta", "name": "Tamil", "script": "Tamil", "engine": "indic"},
            {"code": "te", "name": "Telugu", "script": "Telugu", "engine": "indic"},
            {"code": "ml", "name": "Malayalam", "script": "Malayalam", "engine": "indic"},
            {"code": "kn", "name": "Kannada", "script": "Kannada", "engine": "indic"},
            {"code": "gu", "name": "Gujarati", "script": "Gujarati", "engine": "indic"},
            {"code": "pa", "name": "Punjabi", "script": "Gurmukhi", "engine": "indic"},
            {"code": "zh", "name": "Chinese", "script": "Han", "engine": "pypinyin"},
            {"code": "ja", "name": "Japanese", "script": "Japanese", "engine": "japanese"},
            {"code": "ko", "name": "Korean", "script": "Hangul", "engine": "korean-romanizer"},
            {"code": "*", "name": "Universal fallback", "script": "Any", "engine": "uroman"},
        ],
        "styles": [
            {
                "id": "standard",
                "description": "Standard romanization output",
                "example": {"input": "नमस्ते", "output": "namaste"},
            },
            {
                "id": "academic",
                "description": "Academic style with diacritics (macrons, dots)",
                "example": {"input": "नमस्ते", "output": "namāstē"},
            },
            {
                "id": "chat",
                "description": "Informal chat/social-media style (no diacritics)",
                "example": {"input": "नमस्ते", "output": "namaste"},
            },
            {
                "id": "phonetic",
                "description": "Simplified phonetic approximation",
                "example": {"input": "東京", "output": "Dong Jing"},
            },
        ],
    }
