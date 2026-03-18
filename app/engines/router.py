"""
Romanization router - routes input text to the best engine.

Priority order:
1. Google Translate (for Arabic/Urdu/Persian) - BEST romanization
2. Korean (Hangul) -> KoreanEngine
3. Japanese (Hiragana/Katakana/Kanji) -> JapaneseEngine
4. Chinese (Han/CJK) -> ChineseEngine
5. Indic scripts -> IndicEngine
6. Cyrillic/Greek/Arabic/Hebrew -> ICUEngine (transliterate + unidecode)
7. Everything else -> UromanEngine (uroman or unidecode)
"""

from typing import Tuple, Optional

from app.engines.icu_engine import get_icu_engine
from app.engines.uroman_engine import get_uroman_engine
from app.engines.indic_engine import get_indic_engine
from app.engines.chinese_engine import get_chinese_engine
from app.engines.japanese_engine import get_japanese_engine
from app.engines.korean_engine import get_korean_engine
from app.engines.google_translate import translate_text as google_translate_text
from app.engines.arabic_urdu_romanizer import romanize_arabic_urdu
from app.core.styler import get_styler

# ICU handles these script types
ICU_SCRIPTS = {"cyrillic", "greek", "arabic", "hebrew"}

# Script codes that indicate CJK Chinese
CHINESE_SCRIPT_CODES = {"hans", "hant", "hanzi", "han", "cjk"}

# Script codes that indicate Japanese
JAPANESE_SCRIPT_CODES = {"jpan", "hiragana", "katakana"}

# Indic script codes
INDIC_SCRIPT_CODES = {
    "deva",
    "beng",
    "taml",
    "telu",
    "mlym",
    "knda",
    "gujr",
    "guru",
    "orya",
    "indic",
}

# Scripts that benefit from Google Translate romanization
# Google provides much better romanization for these scripts
GOOGLE_TRANSLATE_SCRIPTS = {"arabic", "ur", "fa", "persian"}

# Global flag to enable/disable Google Translate as primary
_USE_GOOGLE_TRANSLATE_PRIMARY = True


def _route_to_engine(
    text: str,
    script_type: str,
    script_code: str = None,
) -> Tuple[str, str]:
    """Route text to the appropriate engine and return (romanized, engine_name)."""
    sc = (script_code or "").lower()

    # 0. Google Translate - PRIMARY for Arabic/Urdu/Persian (best romanization)
    if _USE_GOOGLE_TRANSLATE_PRIMARY and (
        script_type == "arabic" or sc in GOOGLE_TRANSLATE_SCRIPTS
    ):
        try:
            result = google_translate_text(text, source_lang="auto", target_lang="en")
            if result.get("romanized"):
                # Check if it's actually romanized (Urdu in Latin) vs English translation
                romanized_text = result["romanized"]
                # If it contains Arabic script or looks like a translation, use fallback
                if any(
                    "\u0600" <= c <= "\u06ff" for c in romanized_text if c.isalpha()
                ):
                    # Contains Arabic script - use fallback romanizer
                    romanized_text = romanize_arabic_urdu(text)
                    return romanized_text, "arabic-urdu-romanizer"
                # If it looks like English translation (common words), use fallback
                english_indicators = ["the ", "is ", "are ", "have ", "will ", "can "]
                if any(
                    romanized_text.lower().startswith(w) for w in english_indicators
                ):
                    # Likely a translation, not romanization - use fallback
                    romanized_text = romanize_arabic_urdu(text)
                    return romanized_text, "arabic-urdu-romanizer"
                return romanized_text, "google-translate"
            # Fallback if no romanized available
            romanized_text = romanize_arabic_urdu(text)
            return romanized_text, "arabic-urdu-romanizer"
        except Exception:
            pass

    # 1. Korean
    if script_type == "hangul" or sc == "hangul":
        engine = get_korean_engine()
        try:
            result = engine.romanize(text)
            if result and result != text:
                return result, "korean-romanizer"
        except Exception:
            pass

    # 2. Japanese
    if script_type in ("hiragana", "katakana") or sc in JAPANESE_SCRIPT_CODES:
        engine = get_japanese_engine()
        try:
            result = engine.romanize(text)
            if result and result != text:
                return result, "japanese"
        except Exception:
            pass

    # 3. Chinese
    if script_type == "cjk" or sc in CHINESE_SCRIPT_CODES:
        engine = get_chinese_engine()
        try:
            result = engine.romanize(text)
            if result and result != text:
                return result, "pypinyin"
        except Exception:
            pass

    # 4. Indic scripts
    if script_type == "indic" or sc in INDIC_SCRIPT_CODES:
        engine = get_indic_engine()
        try:
            # Use script_code for indic routing, fall back to "deva"
            effective_code = sc if sc in INDIC_SCRIPT_CODES else "deva"
            result = engine.romanize(text, effective_code)
            if result and result != text:
                return result, "indic"
        except Exception:
            pass

    # 5. ICU (Cyrillic, Greek, Arabic, Hebrew)
    if script_type in ICU_SCRIPTS:
        engine = get_icu_engine()
        try:
            result = engine.romanize(text, script_type)
            if result and result != text:
                return result, "icu"
        except Exception:
            pass

    # 6. Universal fallback (uroman / unidecode)
    fallback = get_uroman_engine()
    result = fallback.romanize(text)
    return result, "uroman"


def route_romanization(
    text: str,
    script_type: str,
    script_code: str = None,
    style: str = "standard",
) -> Tuple[str, str]:
    """
    Route text to the best romanization engine and apply style.

    Returns:
        Tuple of (romanized_text, engine_name)
    """
    romanized, engine_used = _route_to_engine(text, script_type, script_code)

    # Apply style transformation
    if style and style != "standard":
        styler = get_styler()
        romanized = styler.transform(romanized, style)
        engine_used = f"{engine_used}+{style}"

    return romanized, engine_used


def get_supported_engines() -> dict:
    """Get information about all supported engines."""
    icu = get_icu_engine()
    return {
        "google-translate": {
            "display_name": "Google Translate (Primary for Arabic/Urdu)",
            "supported_scripts": list(GOOGLE_TRANSLATE_SCRIPTS),
        },
        "arabic-urdu-romanizer": {
            "display_name": "Arabic/Urdu Romanizer (rule-based)",
            "supported_scripts": ["arabic", "ur", "fa"],
        },
        "icu": {
            "display_name": "ICU (transliterate + unidecode)",
            "supported_scripts": list(ICU_SCRIPTS),
        },
        "pypinyin": {
            "display_name": "pypinyin (Chinese Pinyin)",
            "supported_scripts": list(CHINESE_SCRIPT_CODES),
        },
        "japanese": {
            "display_name": "Japanese (kana mapping + unidecode)",
            "supported_scripts": list(JAPANESE_SCRIPT_CODES),
        },
        "indic": {
            "display_name": "Indic engine (rule-based)",
            "supported_scripts": list(INDIC_SCRIPT_CODES),
        },
        "korean-romanizer": {
            "display_name": "Korean Romanizer (unidecode fallback)",
            "supported_scripts": ["hangul"],
        },
        "uroman": {
            "display_name": "uroman (universal fallback)",
            "supported_scripts": ["universal"],
        },
    }
