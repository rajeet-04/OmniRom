"""
Korean Hangul romanization engine.

Primary: hangul-romanizer library if available.
Fallback: unidecode.
"""

from typing import Optional


class KoreanEngine:
    """Korean Hangul romanization engine."""

    def __init__(self):
        self.romanizer = None
        self.available = False
        self._try_load()

    def _try_load(self):
        """Try to load hangul-romanizer."""
        try:
            # Try different possible package names
            try:
                from hangul_romanize import Transliter
                self.romanizer = Transliter()
                self.available = True
                self._mode = "hangul_romanize"
                return
            except (ImportError, AttributeError):
                pass

            try:
                import hangul_romanize
                self.romanizer = hangul_romanize
                self.available = True
                self._mode = "hangul_romanize_module"
                return
            except ImportError:
                pass

        except Exception:
            pass

        self.available = False

    def romanize(self, text: str, style: str = "revised") -> str:
        """
        Romanize Korean Hangul text.

        Args:
            text: Input Korean text
            style: 'revised' (official Revised Romanization of Korean)

        Returns:
            Romanized text
        """
        if not text:
            return ""

        if self.available:
            try:
                if self._mode == "hangul_romanize":
                    result = self.romanizer.translit(text)
                    if result:
                        return result
                elif self._mode == "hangul_romanize_module":
                    result = self.romanizer.romanize(text)
                    if result:
                        return result
            except Exception:
                pass

        return self._fallback_romanize(text)

    def _fallback_romanize(self, text: str) -> str:
        """Fallback using unidecode."""
        try:
            from unidecode import unidecode
            return unidecode(text)
        except ImportError:
            return text


_korean_engine: Optional[KoreanEngine] = None


def get_korean_engine() -> KoreanEngine:
    """Get or create Korean engine singleton."""
    global _korean_engine
    if _korean_engine is None:
        _korean_engine = KoreanEngine()
    return _korean_engine
