"""
Chinese romanization engine using pypinyin.

Converts Chinese characters (Hanzi) to Pinyin with optional tone marks.
"""

from typing import Optional


class ChineseEngine:
    """Chinese to Pinyin romanization using pypinyin."""

    def __init__(self):
        self._available = False
        self._try_load()

    def _try_load(self):
        """Check if pypinyin is available."""
        try:
            from pypinyin import pinyin  # noqa: F401
            self._available = True
        except ImportError:
            self._available = False

    @property
    def available(self) -> bool:
        """Whether pypinyin is available."""
        return self._available

    def romanize(self, text: str, style: str = "standard") -> str:
        """
        Romanize Chinese text to Pinyin.

        Args:
            text: Input Chinese text
            style: 'standard' (tone marks), 'numbers' (tone numbers),
                   'academic' (tone marks), 'chat' (no tones), 'phonetic' (no tones)

        Returns:
            Pinyin romanization
        """
        if not text:
            return ""

        if not self._available:
            return self._unidecode_fallback(text)

        try:
            from pypinyin import pinyin, Style

            if style in ("numbers",):
                pinyin_style = Style.TONE3
            elif style in ("chat", "phonetic"):
                pinyin_style = Style.NORMAL
            else:
                # standard / academic: use tone marks
                pinyin_style = Style.TONE

            result = pinyin(text, style=pinyin_style, heteronym=False)
            return " ".join(item[0] for item in result)
        except Exception:
            return self._unidecode_fallback(text)

    def _unidecode_fallback(self, text: str) -> str:
        """Fallback when pypinyin unavailable."""
        try:
            from unidecode import unidecode
            return unidecode(text)
        except ImportError:
            return text


_chinese_engine: Optional[ChineseEngine] = None


def get_chinese_engine() -> ChineseEngine:
    """Get or create Chinese engine singleton."""
    global _chinese_engine
    if _chinese_engine is None:
        _chinese_engine = ChineseEngine()
    return _chinese_engine
