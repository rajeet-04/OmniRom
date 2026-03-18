"""Script and language detection module."""

import unicodedata
from typing import Optional


def _detect_script_from_unicode(text: str) -> str:
    """
    Detect script type from Unicode character properties.
    Returns the most common script found in the text.
    """
    script_counts: dict = {}

    for char in text:
        if not char.strip():
            continue
        cat = unicodedata.category(char)
        if cat.startswith("L") or cat.startswith("M"):
            # Get Unicode block name to infer script
            name = unicodedata.name(char, "").lower()
            if "cyrillic" in name:
                script_counts["cyrillic"] = script_counts.get("cyrillic", 0) + 1
            elif "greek" in name:
                script_counts["greek"] = script_counts.get("greek", 0) + 1
            elif "arabic" in name:
                script_counts["arabic"] = script_counts.get("arabic", 0) + 1
            elif "hebrew" in name:
                script_counts["hebrew"] = script_counts.get("hebrew", 0) + 1
            elif "devanagari" in name:
                script_counts["deva"] = script_counts.get("deva", 0) + 1
            elif "bengali" in name:
                script_counts["beng"] = script_counts.get("beng", 0) + 1
            elif "tamil" in name:
                script_counts["taml"] = script_counts.get("taml", 0) + 1
            elif "telugu" in name:
                script_counts["telu"] = script_counts.get("telu", 0) + 1
            elif "malayalam" in name:
                script_counts["mlym"] = script_counts.get("mlym", 0) + 1
            elif "kannada" in name:
                script_counts["knda"] = script_counts.get("knda", 0) + 1
            elif "gujarati" in name:
                script_counts["gujr"] = script_counts.get("gujr", 0) + 1
            elif "gurmukhi" in name:
                script_counts["guru"] = script_counts.get("guru", 0) + 1
            elif "oriya" in name:
                script_counts["orya"] = script_counts.get("orya", 0) + 1
            elif "hangul" in name:
                script_counts["hangul"] = script_counts.get("hangul", 0) + 1
            elif "hiragana" in name:
                script_counts["hiragana"] = script_counts.get("hiragana", 0) + 1
            elif "katakana" in name:
                script_counts["katakana"] = script_counts.get("katakana", 0) + 1
            elif "cjk" in name or "han" in name or "kanji" in name:
                script_counts["hans"] = script_counts.get("hans", 0) + 1
            elif "latin" in name or (ord(char) < 0x250 and ord(char) > 0x40):
                script_counts["latn"] = script_counts.get("latn", 0) + 1
            else:
                script_counts["other"] = script_counts.get("other", 0) + 1

    if not script_counts:
        return "Unknown"

    return max(script_counts, key=lambda k: script_counts[k])


def detect_script(text: str) -> dict:
    """
    Detect the script/language of input text.

    Returns dict with:
    - language: ISO 639-1 code
    - script: Script name
    - reliable: Whether detection is reliable
    - probability: Confidence score
    - script_code: ISO 15924 script code
    """
    if not text or not text.strip():
        return {
            "language": "und",
            "script": "Unknown",
            "reliable": False,
            "probability": 0.0,
            "script_code": "",
        }

    # Use langid for language detection
    try:
        import langid

        lang, confidence = langid.classify(text)
        # langid returns a log-probability; convert to 0-1 range
        import math

        probability = 1.0 / (1.0 + math.exp(-abs(confidence / 10.0)))
    except Exception:
        lang = "und"
        probability = 0.0

    # Use Unicode properties for script detection
    script_code = _detect_script_from_unicode(text)

    # Map script code to display name
    script_display_map = {
        "cyrillic": "Cyrillic",
        "greek": "Greek",
        "arabic": "Arabic",
        "hebrew": "Hebrew",
        "deva": "Devanagari",
        "beng": "Bengali",
        "taml": "Tamil",
        "telu": "Telugu",
        "mlym": "Malayalam",
        "knda": "Kannada",
        "gujr": "Gujarati",
        "guru": "Gurmukhi",
        "orya": "Oriya",
        "hangul": "Hangul",
        "hiragana": "Hiragana",
        "katakana": "Katakana",
        "hans": "Hans",
        "latn": "Latin",
        "other": "Other",
    }
    script_display = script_display_map.get(script_code, script_code.capitalize())

    return {
        "language": lang,
        "script": script_display,
        "script_code": script_code,
        "reliable": probability > 0.7,
        "probability": round(probability, 4),
    }


def get_script_type(language: str, script: str) -> str:
    """
    Categorize the script type for routing.

    Returns: 'cyrillic', 'greek', 'arabic', 'hebrew', 'cjk', 'hangul',
             'hiragana', 'katakana', 'indic', 'latin', 'other'
    """
    script_lower = script.lower() if script else ""

    if script_lower == "cyrillic":
        return "cyrillic"
    elif script_lower == "greek":
        return "greek"
    elif script_lower == "arabic":
        return "arabic"
    elif script_lower == "hebrew":
        return "hebrew"
    elif script_lower in ("hans", "hant", "hanzi", "han"):
        return "cjk"
    elif script_lower == "hangul":
        return "hangul"
    elif script_lower == "hiragana":
        return "hiragana"
    elif script_lower == "katakana":
        return "katakana"
    elif script_lower in (
        "devanagari",
        "deva",
        "bengali",
        "beng",
        "tamil",
        "taml",
        "telugu",
        "telu",
        "malayalam",
        "mlym",
        "kannada",
        "knda",
        "gujarati",
        "gujr",
        "gurmukhi",
        "guru",
        "oriya",
        "orya",
    ):
        return "indic"
    elif script_lower in ("latn", "latin"):
        return "latin"
    else:
        return "other"
