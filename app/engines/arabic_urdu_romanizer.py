"""
Arabic/Urdu script romanization using rule-based character mapping.

Provides significantly better output than unidecode by:
- Correctly handling aspirated consonant pairs (ڈھ → dh, بھ → bh, چھ → chh, etc.)
- Processing diacritics (harakat/zabar/zer/pesh) when present in the text
- Recognising long vowel combinations (damma+waw → oo, kasra+ya → ee, fatha+alef → aa)
- Mapping mid-word bare alef (ا) as the long-a vowel 'aa'
- Handling all Urdu-specific characters (ٹ, ڈ, ڑ, ں, ھ, ہ, ی, ے, etc.)
- Normalising Arabic presentation forms (FB50–FDFF, FE70–FEFF) via NFKC before processing

Limitations common to all rule-based approaches:
- Short vowels that are *not* written in the source text cannot be recovered.
  e.g. من (man) appears as "mn" unless the fatha diacritic is present.
- The consonant و is ambiguous (vowel 'o' vs consonant 'w'); we default to 'o'.
- The vowel quality of ی is approximated as 'i'; diphthongs (ai/ei) are not modelled.
"""

import re
import unicodedata

# ---------------------------------------------------------------------------
# Constants – special characters
# ---------------------------------------------------------------------------

_DO_CHASHMI_HE = "\u06be"  # ھ  Urdu do-chashmi he: aspiration marker
_FATHA = "\u064e"  # ◌َ  zabar   – short a
_DAMMA = "\u064f"  # ◌ُ  pesh    – short u
_KASRA = "\u0650"  # ◌ِ  zer     – short i
_SHADDA = "\u0651"  # ◌ّ  tashdid – gemination (doubled consonant)
_SUKUN = "\u0652"  # ◌ْ  jazm    – explicit absence of vowel
_WAW = "\u0648"  # و  waw
_ALEF = "\u0627"  # ا  alef
_URDU_YA = "\u06cc"  # ی  Urdu ya  (U+06CC)
_ARABIC_YA = "\u064a"  # ي  Arabic ya (U+064A)
_YA_SMALL = "\u0649"  # ى  alef maqsura (U+0649)

# ---------------------------------------------------------------------------
# Aspirated consonant pairs: <base consonant> + ھ  →  romanised cluster
# ---------------------------------------------------------------------------
_ASPIRATED: dict[str, str] = {
    "\u0628": "bh",  # ب  + ھ
    "\u067e": "ph",  # پ  + ھ
    "\u062a": "th",  # ت  + ھ
    "\u0679": "th",  # ٹ  + ھ  (retroflex aspirated t)
    "\u062c": "jh",  # ج  + ھ
    "\u0686": "chh",  # چ  + ھ
    "\u062f": "dh",  # د  + ھ
    "\u0688": "dh",  # ڈ  + ھ  (retroflex aspirated d)
    "\u0631": "rh",  # ر  + ھ
    "\u0691": "rh",  # ڑ  + ھ  (retroflex aspirated r)
    "\u06a9": "kh",  # ک  + ھ
    "\u06af": "gh",  # گ  + ھ
    "\u0644": "lh",  # ل  + ھ
    "\u0645": "mh",  # م  + ھ
    "\u0646": "nh",  # ن  + ھ
}

# ---------------------------------------------------------------------------
# Main character map  →  romanised string
# ---------------------------------------------------------------------------
_CHAR_MAP: dict[str, str] = {
    # ── Alef variants ────────────────────────────────────────────────────────
    # ا  alef bare – positional logic handled in the main loop (see below)
    # "\u0627": handled dynamically
    "\u0623": "a",  # أ  alef + hamza above
    "\u0625": "i",  # إ  alef + hamza below
    "\u0622": "aa",  # آ  alef madda  (always long a)
    "\u0671": "a",  # ٱ  alef wasla
    "\u0670": "a",  # ◌ٰ  dagger/superscript alef
    # ── Hamza ────────────────────────────────────────────────────────────────
    "\u0621": "",  # ء  hamza (often silent)
    "\u0626": "y",  # ئ  ya + hamza
    "\u0624": "o",  # ؤ  waw + hamza (vowel 'o' in Urdu, e.g. ناؤ → naao)
    # ── Ta marbuta ───────────────────────────────────────────────────────────
    "\u0629": "h",  # ة  (Arabic)
    "\u06c3": "h",  # ۃ  (Urdu)
    # ── Standard Arabic consonants ───────────────────────────────────────────
    "\u0628": "b",  # ب
    "\u062a": "t",  # ت
    "\u062b": "s",  # ث  (th → s in Urdu pronunciation)
    "\u062c": "j",  # ج
    "\u062d": "h",  # ح
    "\u062e": "kh",  # خ
    "\u062f": "d",  # د
    "\u0630": "z",  # ذ  (dh → z in Urdu pronunciation)
    "\u0631": "r",  # ر
    "\u0632": "z",  # ز
    "\u0633": "s",  # س
    "\u0634": "sh",  # ش
    "\u0635": "s",  # ص  (heavy s → s in Urdu)
    "\u0636": "z",  # ض  (heavy d → z in Urdu)
    "\u0637": "t",  # ط  (heavy t → t in Urdu)
    "\u0638": "z",  # ظ  (heavy z → z in Urdu)
    "\u0639": "",  # ع  ayn (often silent in Urdu)
    "\u063a": "gh",  # غ
    "\u0641": "f",  # ف
    "\u0642": "q",  # ق
    "\u0643": "k",  # ك  Arabic kaf
    "\u0644": "l",  # ل
    "\u0645": "m",  # م
    "\u0646": "n",  # ن
    "\u0647": "h",  # ه  Arabic ha
    "\u0648": "o",  # و  waw – default to 'o' (long vowel); see also long-vowel combos
    "\u064a": "i",  # ي  Arabic ya
    "\u0649": "a",  # ى  alef maqsura
    # ── Urdu-specific consonants ─────────────────────────────────────────────
    "\u067e": "p",  # پ  pa
    "\u0686": "ch",  # چ  che
    "\u0698": "zh",  # ژ  zhe
    "\u0688": "d",  # ڈ  retroflex da
    "\u0691": "r",  # ڑ  retroflex ra
    "\u0679": "t",  # ٹ  retroflex ta
    "\u06a9": "k",  # ک  Urdu kaf
    "\u06af": "g",  # گ  gaf
    "\u06ba": "n",  # ں  nun ghunna (nasal n)
    "\u06c1": "h",  # ہ  Urdu goal he
    _DO_CHASHMI_HE: "h",  # ھ  do chashmi he – handled as bigram above; lone fallback
    "\u06cc": "i",  # ی  Urdu ya  – long 'i' / consonant 'y'
    "\u06d2": "e",  # ے  ya barri  – word-final 'e'
    "\u06d3": "e",  # ۓ  ya barri + hamza
    # ── Diacritics (harakat) ─────────────────────────────────────────────────
    _FATHA: "a",  # ◌َ  zabar
    _DAMMA: "u",  # ◌ُ  pesh
    _KASRA: "i",  # ◌ِ  zer
    _SHADDA: "",  # ◌ّ  tashdid – gemination handled in loop
    _SUKUN: "",  # ◌ْ  jazm    – explicit no-vowel
    "\u064b": "an",  # ◌ً  tanwin fath
    "\u064c": "un",  # ◌ٌ  tanwin damm
    "\u064d": "in",  # ◌ٍ  tanwin kasr
    # ── Punctuation ──────────────────────────────────────────────────────────
    "\u060c": ",",  # ،  Arabic comma
    "\u061f": "?",  # ؟  Arabic question mark
    "\u061b": ";",  # ؛  Arabic semicolon
    "\u06d4": ".",  # ۔  Urdu full stop
    # ── Misc ─────────────────────────────────────────────────────────────────
    "\u0640": "",  # tatweel / kashida – elongation mark, ignored
}

# Characters that are vowel sounds (used to track whether last output was consonant)
_VOWEL_CHARS = frozenset("aeiouAEIOU")


def romanize_arabic_urdu(text: str) -> str:
    """
    Convert Arabic/Urdu script text to a romanised (Latin) representation.

    Strategy (in order of priority):
      1. NFKC-normalise to collapse Arabic presentation forms.
      2. Detect long-vowel digraphs formed by diacritic + vowel letter:
           damma (ُ) + waw (و)   →  'oo'
           kasra (ِ) + ya  (ی/ي) →  'ee'
           fatha (َ) + alef (ا)  →  'aa'
      3. Detect aspirated consonant pairs: <consonant> + ھ  →  cluster.
      4. Handle shadda (ّ) by doubling the last consonant character.
      5. Map mid-word bare alef (ا) preceded by a consonant as 'aa'.
      6. Apply the character map for everything else.
    """
    if not text:
        return text

    # Step 1: normalise – converts presentation forms (FB50–FDFF, FE70–FEFF)
    # to their canonical base characters.
    text = unicodedata.normalize("NFKC", text)

    # Step 1b: Sanitize - remove non-Arabic/Urdu, non-ASCII printable characters.
    # This strips box drawings (─), emoji, and other miscellaneous symbols that
    # can appear in copied text (e.g., from PDFs or subtitles).
    # Keep: Arabic (0600-06FF, 0750-077F, 08A0-08FF), ASCII printable, spaces.
    def is_keep_char(c: str) -> bool:
        if c.isspace() or c.isascii() and 32 <= ord(c) <= 126:
            return True
        # Arabic Unicode ranges
        cp = ord(c)
        if 0x0600 <= cp <= 0x06FF:  # Arabic
            return True
        if 0x0750 <= cp <= 0x077F:  # Arabic Supplement
            return True
        if 0x08A0 <= cp <= 0x08FF:  # Arabic Extended-A
            return True
        if 0xFB50 <= cp <= 0xFDFF:  # Arabic Presentation Forms-A
            return True
        if 0xFE70 <= cp <= 0xFEFF:  # Arabic Presentation Forms-B
            return True
        return False

    text = "".join(c for c in text if is_keep_char(c))

    _NUN_GHUNNA = "\u06ba"  # ں
    chars = list(text)
    result: list[str] = []
    n = len(chars)
    i = 0
    # Track whether the last *output* ended with a consonant (for alef rule).
    prev_was_consonant = False
    # Track whether we are at the start of a word (for initial-consonant و/ی).
    at_word_start = True

    while i < n:
        ch = chars[i]
        nxt = chars[i + 1] if i + 1 < n else None

        # ── Long vowel: damma + waw → 'oo' ─────────────────────────────────
        if ch == _DAMMA and nxt == _WAW:
            result.append("oo")
            prev_was_consonant = False
            at_word_start = False
            i += 2
            continue

        # ── Long vowel: fatha + alef → 'aa' ─────────────────────────────────
        if ch == _FATHA and nxt == _ALEF:
            result.append("aa")
            prev_was_consonant = False
            at_word_start = False
            i += 2
            continue

        # ── Long vowel: kasra + ya → 'ee' ────────────────────────────────────
        if ch == _KASRA and nxt in (_URDU_YA, _ARABIC_YA, _YA_SMALL):
            result.append("ee")
            prev_was_consonant = False
            at_word_start = False
            i += 2
            continue

        # ── Aspirated consonant pair ─────────────────────────────────────────
        if ch in _ASPIRATED and nxt == _DO_CHASHMI_HE:
            result.append(_ASPIRATED[ch])
            prev_was_consonant = True
            at_word_start = False
            i += 2
            continue

        # ── Shadda: geminate the previous consonant ──────────────────────────
        if ch == _SHADDA:
            if result:
                last = result[-1]
                trailing = last.rstrip("aeiouAEIOU")
                if trailing:
                    result.append(trailing[-1])
                    prev_was_consonant = True
            i += 1
            continue

        # ── Sukun: explicit no-vowel – just skip ────────────────────────────
        if ch == _SUKUN:
            i += 1
            continue

        # ── Bare alef (ا) positional rule ────────────────────────────────────
        # After a consonant:
        #   • word-MEDIAL (followed by another letter) → long 'aa' vowel
        #   • word-FINAL  (followed by space/punct/end) → short 'a' vowel
        # Not after a consonant (word-initial): fall through to char map → 'a'
        if ch == _ALEF and prev_was_consonant:
            # Look ahead past any remaining diacritics to the next real char.
            j = i + 1
            _DIACRITICS = {
                _FATHA,
                _DAMMA,
                _KASRA,
                _SHADDA,
                _SUKUN,
                "\u064b",
                "\u064c",
                "\u064d",
            }
            while j < n and chars[j] in _DIACRITICS:
                j += 1
            next_real = chars[j] if j < n else None
            word_final = (
                next_real is None or next_real.isspace() or next_real in "،,؟?!۔.؛;"
            )
            result.append("a" if word_final else "aa")
            prev_was_consonant = False
            at_word_start = False
            i += 1
            continue

        # ── Word-initial و → 'w' (consonant), elsewhere → 'o' (long vowel) ──
        if ch == _WAW:
            mapped = "w" if at_word_start else "o"
            result.append(mapped)
            prev_was_consonant = mapped == "w"
            at_word_start = False
            i += 1
            continue

        # ── ی / ي before ں → diphthong 'ei' (e.g. میں → mein) ───────────────
        if ch in (_URDU_YA, _ARABIC_YA) and nxt == _NUN_GHUNNA:
            result.append("ei")
            prev_was_consonant = False
            at_word_start = False
            i += 1
            continue

        # ── Word-initial ی → 'y' (consonant), elsewhere → 'i' (long vowel) ──
        if ch in (_URDU_YA, _ARABIC_YA):
            mapped = "y" if at_word_start else "i"
            result.append(mapped)
            prev_was_consonant = mapped == "y"
            at_word_start = False
            i += 1
            continue

        # ── Word-final ہ (Urdu goal he, U+06C1) after a consonant → 'a' ────────
        # In Urdu, e.g. نہ → na, یہ → ya, وہ → wo (but وہ needs special case),
        # کہ → ka.  The ہ is a short-vowel marker, not a /h/ sound, when it
        # appears at the end of a word and follows a consonant.
        if ch == "\u06c1" and prev_was_consonant:
            j = i + 1
            _DIACRITICS = {
                _FATHA,
                _DAMMA,
                _KASRA,
                _SHADDA,
                _SUKUN,
                "\u064b",
                "\u064c",
                "\u064d",
            }
            while j < n and chars[j] in _DIACRITICS:
                j += 1
            next_real = chars[j] if j < n else None
            word_final = (
                next_real is None or next_real.isspace() or next_real in "،,؟?!۔.؛;"
            )
            if word_final:
                result.append("a")
                prev_was_consonant = False
                at_word_start = False
                i += 1
                continue
            # Not word-final: fall through to the standard char map (maps to 'h')

        # ── Standard character map ───────────────────────────────────────────
        if ch in _CHAR_MAP:
            mapped = _CHAR_MAP[ch]
            result.append(mapped)
            if mapped:
                prev_was_consonant = mapped[-1] not in _VOWEL_CHARS
                at_word_start = False
            # else: diacritic mapping to "" – don't change word-start state
        elif ch.isspace():
            result.append(ch)
            prev_was_consonant = False
            at_word_start = True
        elif ch.isascii():
            # Pass through ASCII (digits, existing Latin, punctuation)
            result.append(ch)
            prev_was_consonant = ch.isalpha() and ch not in _VOWEL_CHARS
            at_word_start = not ch.isalpha()
        # Unknown non-ASCII characters are silently dropped.

        i += 1

    romanized = "".join(result)
    # Collapse runs of multiple spaces (can appear when silent chars are removed)
    romanized = re.sub(r"  +", " ", romanized)
    return romanized.strip()
