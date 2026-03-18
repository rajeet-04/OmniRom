"""Style transformation module for romanized text."""

import re
from typing import Optional


class StyleTransformer:
    """Transform romanized text to different output styles."""

    # Common diacritic normalizations (standard -> chat)
    CHAT_SIMPLIFICATIONS = {
        "ā": "a",
        "ē": "e",
        "ī": "i",
        "ō": "o",
        "ū": "u",
        "Ā": "A",
        "Ē": "E",
        "Ī": "I",
        "Ō": "O",
        "Ū": "U",
        "ṇ": "n",
        "ṅ": "n",
        "ñ": "n",
        "ś": "sh",
        "ṣ": "sh",
        "ṭ": "t",
        "ḍ": "d",
        "ḥ": "h",
        "ḫ": "h",
        "ẓ": "z",
        "ġ": "gh",
        "ḷ": "l",
    }

    # Long vowel patterns for academic style (e.g., aa -> ā)
    ACADEMIC_PATTERNS = [
        (r"(?<!\w)aa(?!\w)", "ā"),
        (r"(?<!\w)ee(?!\w)", "ē"),
        (r"(?<!\w)oo(?!\w)", "ō"),
        (r"(?<!\w)uu(?!\w)", "ū"),
        (r"(?<!\w)ii(?!\w)", "ī"),
        # inline long vowels
        (r"aa", "ā"),
        (r"ee", "ē"),
        (r"oo", "ō"),
        (r"uu", "ū"),
        (r"ii", "ī"),
    ]

    def transform(self, text: str, style: str) -> str:
        """Transform romanized text to requested style."""
        if not text or not style or style == "standard":
            return text

        if style == "academic":
            return self._to_academic(text)
        elif style == "chat":
            return self._to_chat(text)
        elif style == "phonetic":
            return self._to_phonetic(text)

        return text

    def _to_academic(self, text: str) -> str:
        """Add proper diacritics for academic/scholarly style."""
        result = text
        # Only apply simple patterns (aa -> ā, ee -> ē etc.)
        # Apply only if not already romanized with diacritics
        for pattern, replacement in self.ACADEMIC_PATTERNS:
            result = re.sub(pattern, replacement, result)
        return result

    def _to_chat(self, text: str) -> str:
        """Convert to informal chat-friendly style (remove diacritics)."""
        result = text
        for old, new in self.CHAT_SIMPLIFICATIONS.items():
            result = result.replace(old, new)
        return result

    def _to_phonetic(self, text: str) -> str:
        """Simplified phonetic approximation using unidecode."""
        try:
            from unidecode import unidecode

            return unidecode(text)
        except ImportError:
            return self._to_chat(text)


_styler: Optional[StyleTransformer] = None


def get_styler() -> StyleTransformer:
    """Get style transformer singleton."""
    global _styler
    if _styler is None:
        _styler = StyleTransformer()
    return _styler
