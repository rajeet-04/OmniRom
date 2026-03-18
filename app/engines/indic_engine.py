"""
Indic language romanization engine.

Primary: AI4Bharat IndicXlit (if available).
Fallback: Rule-based character mapping for Devanagari and other Indic scripts.
"""

from typing import Optional


class IndicFallback:
    """Simple rule-based fallback for Indic scripts."""

    # Basic Devanagari to Latin mapping (ISO 15919 approximation)
    DEVA_MAP = {
        # Independent vowels
        "अ": "a",
        "आ": "aa",
        "इ": "i",
        "ई": "ee",
        "उ": "u",
        "ऊ": "oo",
        "ऋ": "ri",
        "ए": "e",
        "ऐ": "ai",
        "ओ": "o",
        "औ": "au",
        # Consonants (with inherent 'a' vowel)
        "क": "ka",
        "ख": "kha",
        "ग": "ga",
        "घ": "gha",
        "ङ": "nga",
        "च": "cha",
        "छ": "chha",
        "ज": "ja",
        "झ": "jha",
        "ञ": "nya",
        "ट": "ta",
        "ठ": "tha",
        "ड": "da",
        "ढ": "dha",
        "ण": "na",
        "त": "ta",
        "थ": "tha",
        "द": "da",
        "ध": "dha",
        "न": "na",
        "प": "pa",
        "फ": "pha",
        "ब": "ba",
        "भ": "bha",
        "म": "ma",
        "य": "ya",
        "र": "ra",
        "ल": "la",
        "व": "va",
        "श": "sha",
        "ष": "sha",
        "स": "sa",
        "ह": "ha",
        "ळ": "la",
        "क्ष": "ksha",
        "ज्ञ": "gnya",
        # Vowel signs (matras) - replace inherent 'a'
        "ा": "aa",
        "ि": "i",
        "ी": "ee",
        "ु": "u",
        "ू": "oo",
        "ृ": "ri",
        "े": "e",
        "ै": "ai",
        "ो": "o",
        "ौ": "au",
        # Special marks
        "्": None,  # virama: removes inherent 'a' from previous consonant
        "ं": "n",   # anusvara
        "ः": "h",   # visarga
        "ँ": "n",   # chandrabindu
        "।": ".",   # danda
        "॥": ".",   # double danda
    }

    @staticmethod
    def romanize(text: str, script_code: str = "deva") -> str:
        """Simple character-by-character romanization."""
        if not text:
            return ""

        mapping = IndicFallback.DEVA_MAP if script_code.lower() == "deva" else {}

        if not mapping:
            # For non-Devanagari Indic scripts, use unidecode
            try:
                from unidecode import unidecode
                return unidecode(text)
            except ImportError:
                return text

        result = []
        i = 0
        chars = list(text)
        while i < len(chars):
            # Try two-character combinations first (only actual 2-char combos)
            if i + 1 < len(chars):
                two_char = chars[i] + chars[i + 1]
                if two_char in mapping:
                    syllable = mapping[two_char]
                    if syllable is not None:
                        result.append(syllable)
                    i += 2
                    continue

            # Single character lookup
            char = chars[i]
            if char in mapping:
                syllable = mapping[char]
                if syllable is None:
                    # Virama: remove trailing 'a' from the last appended syllable
                    if result and result[-1].endswith("a"):
                        result[-1] = result[-1][:-1]
                else:
                    # Matra: replace inherent 'a' from previous consonant
                    if result and result[-1].endswith("a") and char in (
                        "ा", "ि", "ी", "ु", "ू", "ृ", "े", "ै", "ो", "ौ",
                    ):
                        result[-1] = result[-1][:-1]  # remove inherent 'a'
                    result.append(syllable)
            else:
                result.append(char)
            i += 1

        return "".join(result)


class IndicEngine:
    """Indic language transliteration engine."""

    # Script codes supported by this engine
    SCRIPT_CODES = {
        "deva",   # Devanagari
        "beng",   # Bengali
        "taml",   # Tamil
        "telu",   # Telugu
        "mlym",   # Malayalam
        "knda",   # Kannada
        "gujr",   # Gujarati
        "guru",   # Gurmukhi (Punjabi)
        "orya",   # Oriya
        "indic",  # Generic indic
    }

    def __init__(self):
        self.ai4bharat_available = False
        self._try_load_ai4bharat()

    def _try_load_ai4bharat(self):
        """Try to load AI4Bharat IndicXlit (optional heavy dependency)."""
        try:
            from ai4bharat.transliteration import Script  # noqa: F401
            self.ai4bharat_available = True
        except ImportError:
            self.ai4bharat_available = False

    def is_supported(self, script_code: str) -> bool:
        """Check if this engine handles the given script."""
        return script_code.lower() in self.SCRIPT_CODES

    def romanize(self, text: str, script_code: str) -> str:
        """
        Romanize Indic text.

        Args:
            text: Input text in Indic script
            script_code: ISO 15924 script code (deva, beng, taml, etc.)

        Returns:
            Romanized text
        """
        if not text:
            return ""

        sc = script_code.lower()

        # Try AI4Bharat if available
        if self.ai4bharat_available:
            try:
                from ai4bharat.transliteration import Script
                result = Script.get_instance(sc)
                romanized = result.transliterate(text, max_result_len=len(text) * 3)
                if romanized:
                    return romanized
            except Exception:
                pass

        # Use rule-based fallback
        return IndicFallback.romanize(text, sc)


_indic_engine: Optional[IndicEngine] = None


def get_indic_engine() -> IndicEngine:
    """Get or create Indic engine singleton."""
    global _indic_engine
    if _indic_engine is None:
        _indic_engine = IndicEngine()
    return _indic_engine
