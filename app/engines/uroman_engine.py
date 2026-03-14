"""
Universal fallback romanization engine.

Uses uroman (if available) or unidecode as a catch-all romanizer
for scripts not handled by specialized engines.
"""

import subprocess
import unicodedata
from typing import Optional


class UromanEngine:
    """Universal romanizer - uroman or unidecode fallback."""

    def __init__(self):
        self.uroman_available = self._check_uroman()

    def _check_uroman(self) -> bool:
        """Check if uroman CLI tool is available."""
        try:
            result = subprocess.run(
                ["uroman", "--help"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def romanize(self, text: str) -> str:
        """
        Romanize text using uroman or unidecode fallback.

        Args:
            text: Input text to romanize

        Returns:
            Romanized text
        """
        if not text:
            return ""

        if self.uroman_available:
            try:
                result = subprocess.run(
                    ["uroman"],
                    input=text,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode == 0:
                    return result.stdout.strip()
            except (subprocess.TimeoutExpired, Exception):
                pass

        # Fallback: unidecode
        try:
            from unidecode import unidecode
            return unidecode(text)
        except ImportError:
            pass

        # Last resort: strip combining marks
        return self._strip_combining(text)

    def _strip_combining(self, text: str) -> str:
        """Remove combining marks (diacritics) and keep base characters."""
        normalized = unicodedata.normalize("NFD", text)
        return "".join(c for c in normalized if unicodedata.category(c) != "Mn")


_uroman_engine: Optional[UromanEngine] = None


def get_uroman_engine() -> UromanEngine:
    """Get or create uroman engine singleton."""
    global _uroman_engine
    if _uroman_engine is None:
        _uroman_engine = UromanEngine()
    return _uroman_engine
