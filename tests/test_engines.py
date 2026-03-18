"""Tests for romanization engines."""

import pytest

from app.engines.icu_engine import ICUEngine, get_icu_engine
from app.engines.indic_engine import IndicEngine, IndicFallback, get_indic_engine
from app.engines.chinese_engine import ChineseEngine, get_chinese_engine
from app.engines.japanese_engine import JapaneseEngine, get_japanese_engine
from app.engines.korean_engine import KoreanEngine, get_korean_engine
from app.engines.uroman_engine import UromanEngine, get_uroman_engine
from app.engines.router import route_romanization


class TestICUEngine:
    """Tests for ICU/transliterate engine."""

    def setup_method(self):
        self.engine = ICUEngine()

    def test_cyrillic_romanization(self):
        result = self.engine.romanize("Привет", "cyrillic")
        assert result
        assert all(ord(c) < 128 for c in result.strip())

    def test_greek_romanization(self):
        result = self.engine.romanize("Γεια", "greek")
        assert result
        assert len(result) > 0

    def test_empty_text(self):
        result = self.engine.romanize("", "cyrillic")
        assert result == ""

    def test_is_supported(self):
        assert self.engine.is_supported("cyrillic")
        assert self.engine.is_supported("greek")
        assert self.engine.is_supported("arabic")
        assert self.engine.is_supported("hebrew")
        assert not self.engine.is_supported("unknown_script")


class TestIndicEngine:
    """Tests for Indic languages engine."""

    def setup_method(self):
        self.engine = IndicEngine()
        self.fallback = IndicFallback()

    def test_devanagari_romanization(self):
        result = self.engine.romanize("नमस्ते", "deva")
        assert result
        assert len(result) > 0

    def test_indic_fallback_devanagari(self):
        result = IndicFallback.romanize("नमस्ते", "deva")
        assert result
        assert len(result) > 0

    def test_empty_text(self):
        result = self.engine.romanize("", "deva")
        assert result == ""

    def test_is_supported(self):
        assert self.engine.is_supported("deva")
        assert self.engine.is_supported("beng")
        assert self.engine.is_supported("taml")
        assert not self.engine.is_supported("cyrillic")


class TestChineseEngine:
    """Tests for Chinese pypinyin engine."""

    def setup_method(self):
        self.engine = ChineseEngine()

    def test_chinese_romanization(self):
        result = self.engine.romanize("你好")
        assert result
        assert len(result) > 0

    def test_chinese_no_tones(self):
        result = self.engine.romanize("你好", style="chat")
        assert result
        # Should not contain tone numbers
        for digit in "12345":
            assert digit not in result

    def test_empty_text(self):
        result = self.engine.romanize("")
        assert result == ""


class TestJapaneseEngine:
    """Tests for Japanese engine."""

    def setup_method(self):
        self.engine = JapaneseEngine()

    def test_hiragana_romanization(self):
        result = self.engine.romanize("こんにちは")
        assert result
        assert len(result) > 0

    def test_katakana_romanization(self):
        result = self.engine.romanize("コンニチハ")
        assert result
        assert len(result) > 0

    def test_empty_text(self):
        result = self.engine.romanize("")
        assert result == ""


class TestKoreanEngine:
    """Tests for Korean engine."""

    def setup_method(self):
        self.engine = KoreanEngine()

    def test_hangul_romanization(self):
        result = self.engine.romanize("안녕하세요")
        assert result
        assert len(result) > 0

    def test_empty_text(self):
        result = self.engine.romanize("")
        assert result == ""


class TestUromanEngine:
    """Tests for universal fallback engine."""

    def setup_method(self):
        self.engine = UromanEngine()

    def test_cyrillic_fallback(self):
        result = self.engine.romanize("Привет")
        assert result
        assert len(result) > 0

    def test_empty_text(self):
        result = self.engine.romanize("")
        assert result == ""

    def test_latin_passthrough(self):
        result = self.engine.romanize("Hello")
        assert "Hello" in result or result.lower() == "hello"


class TestRouter:
    """Tests for romanization router."""

    def test_route_cyrillic(self):
        romanized, engine = route_romanization("Привет", "cyrillic")
        assert romanized
        assert "icu" in engine or "uroman" in engine

    def test_route_hindi(self):
        romanized, engine = route_romanization("नमस्ते", "indic", "deva")
        assert romanized
        assert len(romanized) > 0

    def test_route_chinese(self):
        romanized, engine = route_romanization("你好", "cjk", "hans")
        assert romanized
        assert len(romanized) > 0

    def test_route_japanese(self):
        romanized, engine = route_romanization("こんにちは", "hiragana", "hiragana")
        assert romanized
        assert len(romanized) > 0

    def test_route_korean(self):
        romanized, engine = route_romanization("안녕", "hangul", "hangul")
        assert romanized
        assert len(romanized) > 0

    def test_style_chat(self):
        # Chat style should remove diacritics
        romanized, engine = route_romanization("Привет", "cyrillic", style="chat")
        assert romanized
        # Engine name should contain style info
        assert "chat" in engine

    def test_empty_text_falls_back(self):
        romanized, engine = route_romanization("", "cyrillic")
        # Empty text may return empty or pass through
        assert isinstance(romanized, str)
