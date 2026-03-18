"""
Google Translate API wrapper using the internal batchexecute endpoint.

This module provides a function to translate text using Google Translate's
internal API (similar to translate.google.com web interface).

Usage:
    from app.engines.google_translate import translate_text

    result = translate_text("مرحبا بالعالم", source_lang="auto", target_lang="en")
    print(result)  # "Hello world"
"""

import json
import re
import urllib.parse
import requests
from typing import Optional, List


# Google Translate endpoint
TRANSLATE_URL = "https://translate.google.com/_/TranslateWebserverUi/data/batchexecute"

# Headers that mimic a real browser
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    "Accept": "*/*",
    "X-Same-Domain": "1",
    "X-Browser-Channel": "stable",
    "X-Browser-Year": "2026",
    "sec-ch-ua": '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
    "sec-ch-ua-full-version": "146.0.7680.80",
    "sec-ch-ua-full-version-list": '"Chromium";v="146.0.7680.80", "Not-A.Brand";v="24.0.0.0", "Google Chrome";v="146.0.7680.80"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-ch-ua-platform-version": '"19.0.0"',
    "sec-ch-ua-arch": '"x86"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-model": '""',
    "sec-ch-ua-form-factors": '"Desktop"',
    "sec-ch-ua-wow64": "?0",
}

# Session for cookie persistence
_session: Optional[requests.Session] = None


def _get_session() -> requests.Session:
    """Get or create a requests session with cookies."""
    global _session
    if _session is None:
        _session = requests.Session()
    return _session


def get_cookies() -> dict:
    """
    Get cookies from Google Translate by visiting the main page.

    Returns:
        dict: Cookie dictionary with NID and other cookies.
    """
    session = _get_session()

    # Visit translate.google.com to get cookies
    response = session.get(
        "https://translate.google.com",
        headers={
            "User-Agent": DEFAULT_HEADERS["User-Agent"],
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
        timeout=30,
    )

    return session.cookies.get_dict()


def _build_request_payload(
    text: str, source_lang: str = "auto", target_lang: str = "en"
) -> str:
    """
    Build the request payload for the batchexecute endpoint.

    Args:
        text: Text to translate.
        source_lang: Source language code (e.g., 'auto', 'ar', 'ur').
        target_lang: Target language code (e.g., 'en', 'es').

    Returns:
        str: URL-encoded request payload.
    """
    # Build the request structure based on the working curl format
    # Format: [[func_name, [[text, source_lang, target_lang, 1, null, 2], []]], null, type]
    # We must json.dumps the text to properly escape newlines and quotes
    escaped_text = json.dumps(text)
    inner_request = f'[[{escaped_text},"{source_lang}","{target_lang}",1,null,2],[]]'

    request_data = [
        [
            [
                "MkEWBc",  # Function identifier
                inner_request,
                None,
                "generic",
            ]
        ]
    ]

    payload = json.dumps(request_data)
    encoded_payload = urllib.parse.quote(payload, safe="")

    return f"f.req={encoded_payload}"


def translate_text(
    text: str,
    source_lang: str = "auto",
    target_lang: str = "en",
    use_fresh_cookies: bool = False,
) -> dict:
    """
    Translate text using Google Translate API.

    Args:
        text: Text to translate.
        source_lang: Source language code (e.g., 'auto', 'ar', 'ur', 'fa').
        target_lang: Target language code (e.g., 'en', 'es', 'fr').
        use_fresh_cookies: If True, get fresh cookies before translating.

    Returns:
        dict: A dictionary containing 'translation' and 'romanized' (if available).

    Raises:
        requests.RequestException: If the request fails.
        ValueError: If the response cannot be parsed.
    """
    global _session

    # Get or refresh cookies if needed
    if use_fresh_cookies or _session is None:
        get_cookies()

    session = _get_session()

    # Build the request payload
    payload = _build_request_payload(text, source_lang, target_lang)

    # Make the request
    response = session.post(
        TRANSLATE_URL,
        data=payload,
        headers={
            **DEFAULT_HEADERS,
            "Content-Length": str(len(payload)),
        },
        timeout=60,
    )

    if response.status_code != 200:
        raise requests.RequestException(
            f"Translation request failed with status {response.status_code}: {response.text[:200]}"
        )

    # Parse the response (use content.decode to avoid encoding issues)
    return _parse_response(response.content.decode("utf-8"))


def _parse_response(response_text: str) -> dict:
    """
    Parse the Google Translate response.

    The response format is:
    )]}'\n[["wrb.fr","MkEWBc","[null,null,\"ar\",[[[0,...]]]],...]"

    Args:
        response_text: Raw response text from the API.

    Returns:
        dict: A dictionary containing 'translation' and 'romanized'.
    """
    result = {"translation": "", "romanized": ""}

    try:
        # Remove the wrapper prefix )]}'
        if response_text.startswith(")]}'"):
            response_text = response_text[4:].strip()

        # Parse the outer JSON array
        data = json.loads(response_text)

        if not isinstance(data, list) or len(data) == 0:
            result["translation"] = response_text
            return result

        # The structure is: [["wrb.fr", "MkEWBc", inner_json, null, null, null, "generic"]]
        # The translation is in data[0][2] as a JSON string
        if len(data) > 0 and isinstance(data[0], list) and len(data[0]) >= 3:
            inner_json_str = data[0][2]

            if isinstance(inner_json_str, str):
                # Parse the inner JSON
                inner_data = json.loads(inner_json_str)

                # 1. Try to extract romanized text (often at inner_data[0][0] for transliteration)
                try:
                    if (
                        len(inner_data) > 0
                        and isinstance(inner_data[0], list)
                        and len(inner_data[0]) > 0
                        and isinstance(inner_data[0][0], str)
                        and len(inner_data[0][0]) > 0
                    ):
                        result["romanized"] = inner_data[0][0]
                except (IndexError, TypeError):
                    pass

                # 2. Try to extract translated text
                # The structure usually has the translation segments at:
                # inner_data[1][0][0][5] or inner_data[4][0][0][5]
                # We can iterate through indices 1 to 5 to find the pattern.
                for i in range(10):
                    try:
                        if (
                            len(inner_data) > i
                            and inner_data[i] is not None
                            and isinstance(inner_data[i], list)
                            and len(inner_data[i]) > 0
                            and isinstance(inner_data[i][0], list)
                            and len(inner_data[i][0]) > 0
                            and isinstance(inner_data[i][0][0], list)
                            and len(inner_data[i][0][0]) > 5
                            and isinstance(inner_data[i][0][0][5], list)
                        ):
                            candidate = inner_data[i][0][0][5]
                            if (
                                len(candidate) > 0
                                and isinstance(candidate[0], list)
                                and len(candidate[0]) > 0
                                and isinstance(candidate[0][0], str)
                            ):
                                # Found the translation segments array
                                translated_text = ""
                                for segment in candidate:
                                    if (
                                        isinstance(segment, list)
                                        and len(segment) > 0
                                        and isinstance(segment[0], str)
                                    ):
                                        translated_text += segment[0]
                                result["translation"] = translated_text
                                return result
                    except (IndexError, TypeError):
                        continue

        # Fallback: try to find any English text in the response
        # Use regex to find patterns that look like translations
        english_matches = re.findall(r'"([A-Za-z][A-Za-z\s]{5,})"', response_text)
        if english_matches:
            # Return the longest English text found (likely the translation)
            result["translation"] = max(english_matches, key=len).strip()
            return result

        # If all else fails, return a portion of the raw response for debugging
        result["translation"] = "[Could not parse translation from response]"
        return result

    except (json.JSONDecodeError, IndexError, KeyError, TypeError) as e:
        # Return raw text if parsing fails
        result["translation"] = f"[Parse error: {str(e)}]"
        return result


def translate_batch(
    texts: List[str], source_lang: str = "auto", target_lang: str = "en"
) -> List[dict]:
    """
    Translate multiple texts.

    Args:
        texts: List of texts to translate.
        source_lang: Source language code.
        target_lang: Target language code.

    Returns:
        list[str]: List of translated texts.
    """
    results = []
    for text in texts:
        result = translate_text(text, source_lang, target_lang)
        results.append(result)
    return results


# Test function
if __name__ == "__main__":
    # Test the translation
    print("Getting cookies...")
    cookies = get_cookies()
    print("Cookies: OK")

    print("\nTesting translation...")
    test_texts = [
        "مرحبا بالعالم",
        "كيف حالك",
        "شكرا لك",
    ]

    # Write results to file to avoid encoding issues
    with open("R:/Code/OmniRom/translate_test_output.txt", "w", encoding="utf-8") as f:
        for text in test_texts:
            try:
                result = translate_text(text, source_lang="auto", target_lang="en")
                f.write(f"OK: {json.dumps(result, ensure_ascii=False)}\n")
            except Exception as e:
                f.write(f"ERROR: {str(e)}\n")

    print("\nResults written to translate_test_output.txt")
