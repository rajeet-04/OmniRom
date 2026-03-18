"""Tests for script detection module."""

import pytest

from app.core.detector import detect_script, get_script_type


class TestDetectScript:
    """Tests for script detection."""

    def test_detect_cyrillic(self):
        result = detect_script("Привет мир")
        assert result["script"].lower() in ("cyrillic",)

    def test_detect_greek(self):
        result = detect_script("Γεια σου")
        assert result["script"].lower() in ("greek",)

    def test_detect_arabic(self):
        result = detect_script("مرحبا بالعالم")
        assert result["script"].lower() in ("arabic",)

    def test_detect_hindi_devanagari(self):
        result = detect_script("नमस्ते दुनिया")
        assert result["script_code"] == "deva"

    def test_detect_chinese(self):
        result = detect_script("你好世界")
        assert result["script_code"] in ("hans", "hant")

    def test_detect_hangul(self):
        result = detect_script("안녕하세요")
        assert result["script_code"] == "hangul"

    def test_detect_hiragana(self):
        result = detect_script("こんにちは")
        assert result["script_code"] in ("hiragana", "katakana")

    def test_detect_latin(self):
        result = detect_script("Hello World")
        # Latin text passes through
        assert result["language"] is not None

    def test_empty_text(self):
        result = detect_script("")
        assert result["language"] == "und"
        assert result["reliable"] is False

    def test_whitespace_only(self):
        result = detect_script("   ")
        assert result["language"] == "und"
        assert result["reliable"] is False


class TestGetScriptType:
    """Tests for script type mapping."""

    def test_cyrillic(self):
        assert get_script_type("ru", "Cyrillic") == "cyrillic"

    def test_greek(self):
        assert get_script_type("el", "Greek") == "greek"

    def test_arabic(self):
        assert get_script_type("ar", "Arabic") == "arabic"

    def test_hebrew(self):
        assert get_script_type("he", "Hebrew") == "hebrew"

    def test_devanagari(self):
        assert get_script_type("hi", "Devanagari") == "indic"

    def test_bengali(self):
        assert get_script_type("bn", "Bengali") == "indic"

    def test_hangul(self):
        assert get_script_type("ko", "Hangul") == "hangul"

    def test_cjk(self):
        assert get_script_type("zh", "Hans") == "cjk"

    def test_latin(self):
        assert get_script_type("en", "Latin") == "latin"

    def test_unknown(self):
        assert get_script_type("xx", "Unknown") == "other"
