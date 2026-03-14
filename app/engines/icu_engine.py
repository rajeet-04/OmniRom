"""
ICU-based romanization engine.

Uses the `transliterate` library for Cyrillic and other scripts
with rule-based transliteration. Falls back to unidecode for
unsupported scripts.
"""

from typing import Optional


# Scripts supported by the transliterate library
_TRANSLITERATE_LANG_MAP = {
    "cyrillic": "ru",   # Russian/Cyrillic
    "greek": "el",      # Greek
}

# Additional script codes that map to transliterate languages
_SCRIPT_CODE_TO_LANG = {
    "cyrillic": "ru",
    "greek": "el",
}


class ICUEngine:
    """Rule-based transliteration using the transliterate library."""

    SUPPORTED_SCRIPTS = {"cyrillic", "greek", "arabic", "hebrew"}

    def __init__(self):
        self._available_scripts: set = set()
        self._load_engines()

    def _load_engines(self):
        """Determine which scripts are available."""
        try:
            from transliterate import translit, get_available_language_codes
            from transliterate.discover import autodiscover
            autodiscover()
            available_codes = get_available_language_codes()
            if "ru" in available_codes or "bg" in available_codes:
                self._available_scripts.add("cyrillic")
            if "el" in available_codes:
                self._available_scripts.add("greek")
        except ImportError:
            pass

        # unidecode is always available as fallback for Arabic/Hebrew
        try:
            from unidecode import unidecode  # noqa: F401
            self._available_scripts.add("arabic")
            self._available_scripts.add("hebrew")
        except ImportError:
            pass

    def romanize(self, text: str, script_type: str) -> str:
        """
        Romanize text using appropriate transliterator.

        Args:
            text: Input text to romanize
            script_type: Script type (cyrillic, greek, arabic, hebrew, etc.)

        Returns:
            Romanized text
        """
        if not text:
            return ""

        if script_type in ("cyrillic", "greek"):
            lang_code = _TRANSLITERATE_LANG_MAP.get(script_type)
            if lang_code:
                try:
                    from transliterate import translit
                    return translit(text, lang_code, reversed=True)
                except Exception:
                    pass

        # Fallback: use unidecode for Arabic, Hebrew, and other scripts
        try:
            from unidecode import unidecode
            return unidecode(text)
        except ImportError:
            pass

        return text

    def is_supported(self, script_type: str) -> bool:
        """Check if script is supported by this engine."""
        return script_type in self.SUPPORTED_SCRIPTS


_icu_engine: Optional[ICUEngine] = None


def get_icu_engine() -> ICUEngine:
    """Get or create ICU engine singleton."""
    global _icu_engine
    if _icu_engine is None:
        _icu_engine = ICUEngine()
    return _icu_engine
