"""
Japanese romanization engine.

Primary: Cutlet (MeCab-based) if available.
Fallback: Basic hiragana/katakana character mapping.
"""

from typing import Optional


# Hiragana to romaji mapping (Hepburn style)
HIRAGANA_MAP = {
    "あ": "a", "い": "i", "う": "u", "え": "e", "お": "o",
    "か": "ka", "き": "ki", "く": "ku", "け": "ke", "こ": "ko",
    "さ": "sa", "し": "shi", "す": "su", "せ": "se", "そ": "so",
    "た": "ta", "ち": "chi", "つ": "tsu", "て": "te", "と": "to",
    "な": "na", "に": "ni", "ぬ": "nu", "ね": "ne", "の": "no",
    "は": "ha", "ひ": "hi", "ふ": "fu", "へ": "he", "ほ": "ho",
    "ま": "ma", "み": "mi", "む": "mu", "め": "me", "も": "mo",
    "や": "ya", "ゆ": "yu", "よ": "yo",
    "ら": "ra", "り": "ri", "る": "ru", "れ": "re", "ろ": "ro",
    "わ": "wa", "ゐ": "wi", "ゑ": "we", "を": "wo", "ん": "n",
    # Voiced consonants
    "が": "ga", "ぎ": "gi", "ぐ": "gu", "げ": "ge", "ご": "go",
    "ざ": "za", "じ": "ji", "ず": "zu", "ぜ": "ze", "ぞ": "zo",
    "だ": "da", "ぢ": "ji", "づ": "zu", "で": "de", "ど": "do",
    "ば": "ba", "び": "bi", "ぶ": "bu", "べ": "be", "ぼ": "bo",
    "ぱ": "pa", "ぴ": "pi", "ぷ": "pu", "ぺ": "pe", "ぽ": "po",
    # Combined sounds
    "きゃ": "kya", "きゅ": "kyu", "きょ": "kyo",
    "しゃ": "sha", "しゅ": "shu", "しょ": "sho",
    "ちゃ": "cha", "ちゅ": "chu", "ちょ": "cho",
    "にゃ": "nya", "にゅ": "nyu", "にょ": "nyo",
    "ひゃ": "hya", "ひゅ": "hyu", "ひょ": "hyo",
    "みゃ": "mya", "みゅ": "myu", "みょ": "myo",
    "りゃ": "rya", "りゅ": "ryu", "りょ": "ryo",
    "ぎゃ": "gya", "ぎゅ": "gyu", "ぎょ": "gyo",
    "じゃ": "ja", "じゅ": "ju", "じょ": "jo",
    "びゃ": "bya", "びゅ": "byu", "びょ": "byo",
    "ぴゃ": "pya", "ぴゅ": "pyu", "ぴょ": "pyo",
    # Small tsu (double consonant marker)
    "っ": "",  # handled separately
    # Prolonged sound mark
    "ー": "-",
}

# Katakana to romaji (same sounds as hiragana equivalents)
KATAKANA_MAP = {
    "ア": "a", "イ": "i", "ウ": "u", "エ": "e", "オ": "o",
    "カ": "ka", "キ": "ki", "ク": "ku", "ケ": "ke", "コ": "ko",
    "サ": "sa", "シ": "shi", "ス": "su", "セ": "se", "ソ": "so",
    "タ": "ta", "チ": "chi", "ツ": "tsu", "テ": "te", "ト": "to",
    "ナ": "na", "ニ": "ni", "ヌ": "nu", "ネ": "ne", "ノ": "no",
    "ハ": "ha", "ヒ": "hi", "フ": "fu", "ヘ": "he", "ホ": "ho",
    "マ": "ma", "ミ": "mi", "ム": "mu", "メ": "me", "モ": "mo",
    "ヤ": "ya", "ユ": "yu", "ヨ": "yo",
    "ラ": "ra", "リ": "ri", "ル": "ru", "レ": "re", "ロ": "ro",
    "ワ": "wa", "ヲ": "wo", "ン": "n",
    "ガ": "ga", "ギ": "gi", "グ": "gu", "ゲ": "ge", "ゴ": "go",
    "ザ": "za", "ジ": "ji", "ズ": "zu", "ゼ": "ze", "ゾ": "zo",
    "ダ": "da", "ヂ": "ji", "ヅ": "zu", "デ": "de", "ド": "do",
    "バ": "ba", "ビ": "bi", "ブ": "bu", "ベ": "be", "ボ": "bo",
    "パ": "pa", "ピ": "pi", "プ": "pu", "ペ": "pe", "ポ": "po",
    "キャ": "kya", "キュ": "kyu", "キョ": "kyo",
    "シャ": "sha", "シュ": "shu", "ショ": "sho",
    "チャ": "cha", "チュ": "chu", "チョ": "cho",
    "ニャ": "nya", "ニュ": "nyu", "ニョ": "nyo",
    "ヒャ": "hya", "ヒュ": "hyu", "ヒョ": "hyo",
    "ミャ": "mya", "ミュ": "myu", "ミョ": "myo",
    "リャ": "rya", "リュ": "ryu", "リョ": "ryo",
    "ギャ": "gya", "ギュ": "gyu", "ギョ": "gyo",
    "ジャ": "ja", "ジュ": "ju", "ジョ": "jo",
    "ビャ": "bya", "ビュ": "byu", "ビョ": "byo",
    "ピャ": "pya", "ピュ": "pyu", "ピョ": "pyo",
    "ッ": "",
    "ー": "-",
}

COMBINED_MAP = {**HIRAGANA_MAP, **KATAKANA_MAP}


def _basic_kana_romanize(text: str) -> str:
    """Convert hiragana/katakana to romaji using character map."""
    result = []
    i = 0
    chars = list(text)
    while i < len(chars):
        # Check for small tsu (double consonant)
        if chars[i] in ("っ", "ッ") and i + 1 < len(chars):
            # Get next consonant
            next_char = chars[i + 1]
            next_romaji = COMBINED_MAP.get(next_char, "")
            if next_romaji:
                result.append(next_romaji[0])  # Double the first consonant
            i += 1
            continue

        # Try two-char combination first
        two_char = chars[i] + (chars[i + 1] if i + 1 < len(chars) else "")
        if two_char in COMBINED_MAP:
            result.append(COMBINED_MAP[two_char])
            i += 2
        elif chars[i] in COMBINED_MAP:
            result.append(COMBINED_MAP[chars[i]])
            i += 1
        else:
            result.append(chars[i])
            i += 1

    return "".join(result)


class JapaneseEngine:
    """Japanese romanization engine."""

    def __init__(self):
        self.cutlet = None
        self.cutlet_available = False
        self._try_load_cutlet()

    def _try_load_cutlet(self):
        """Try to load Cutlet (requires MeCab)."""
        try:
            import cutlet
            self.cutlet = cutlet.Cutlet()
            self.cutlet_available = True
        except (ImportError, Exception):
            self.cutlet_available = False

    def romanize(self, text: str, style: str = "hepburn") -> str:
        """
        Romanize Japanese text to romaji.

        Args:
            text: Input Japanese text (kanji, kana, or mixed)
            style: 'hepburn' (default), 'kunrei', or 'nihon'

        Returns:
            Romanized text
        """
        if not text:
            return ""

        # Try Cutlet first
        if self.cutlet_available:
            try:
                result = self.cutlet.romaji(text)
                if result:
                    return result
            except Exception:
                pass

        # Fallback: basic kana mapping + unidecode for kanji
        return self._fallback_romanize(text)

    def _fallback_romanize(self, text: str) -> str:
        """Fallback romanization using kana map + unidecode."""
        # First try basic kana conversion
        result = _basic_kana_romanize(text)

        # For remaining non-ASCII characters (kanji), use unidecode
        has_non_ascii = any(ord(c) > 127 for c in result)
        if has_non_ascii:
            try:
                from unidecode import unidecode
                # Apply unidecode only to non-ASCII parts
                final = []
                for c in result:
                    if ord(c) > 127:
                        final.append(unidecode(c))
                    else:
                        final.append(c)
                return "".join(final)
            except ImportError:
                pass

        return result


_japanese_engine: Optional[JapaneseEngine] = None


def get_japanese_engine() -> JapaneseEngine:
    """Get or create Japanese engine singleton."""
    global _japanese_engine
    if _japanese_engine is None:
        _japanese_engine = JapaneseEngine()
    return _japanese_engine
