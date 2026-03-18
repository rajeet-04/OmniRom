"""Tests for API endpoints."""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

import app.api.files as files_module
from app.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Tests for health/root endpoints."""

    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "OmniRom" in response.json()["message"]

    def test_health(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_docs_available(self):
        response = client.get("/docs")
        assert response.status_code == 200


class TestRomanizeEndpoint:
    """Tests for /v1/romanize POST endpoint."""

    def test_romanize_cyrillic(self):
        response = client.post("/v1/romanize", json={"text": "Привет"})
        assert response.status_code == 200
        data = response.json()
        assert "romanized" in data
        assert "metadata" in data
        assert data["romanized"]
        assert data["metadata"]["engine_used"]

    def test_romanize_hindi(self):
        response = client.post("/v1/romanize", json={"text": "नमस्ते"})
        assert response.status_code == 200
        data = response.json()
        assert data["romanized"]

    def test_romanize_chinese(self):
        response = client.post("/v1/romanize", json={"text": "你好"})
        assert response.status_code == 200
        data = response.json()
        assert data["romanized"]

    def test_romanize_japanese(self):
        response = client.post("/v1/romanize", json={"text": "こんにちは"})
        assert response.status_code == 200
        data = response.json()
        assert data["romanized"]

    def test_romanize_korean(self):
        response = client.post("/v1/romanize", json={"text": "안녕하세요"})
        assert response.status_code == 200
        data = response.json()
        assert data["romanized"]

    def test_romanize_empty_text(self):
        response = client.post("/v1/romanize", json={"text": ""})
        assert response.status_code in (400, 422)

    def test_romanize_with_style(self):
        response = client.post(
            "/v1/romanize", json={"text": "Привет", "style": "chat"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["romanized"]

    def test_romanize_latin_passthrough(self):
        response = client.post("/v1/romanize", json={"text": "Hello World"})
        assert response.status_code == 200

    def test_response_has_metadata(self):
        response = client.post("/v1/romanize", json={"text": "Привет"})
        assert response.status_code == 200
        data = response.json()
        assert "detected_lang" in data["metadata"]
        assert "engine_used" in data["metadata"]
        assert "processing_time_ms" in data["metadata"]
        assert "cached" in data["metadata"]


class TestBatchEndpoint:
    """Tests for /v1/romanize/batch POST endpoint."""

    def test_batch_basic(self):
        response = client.post(
            "/v1/romanize/batch",
            json={"texts": ["Привет", "Hello", "你好"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 3
        assert data["total"] == 3

    def test_batch_empty_list(self):
        response = client.post("/v1/romanize/batch", json={"texts": []})
        assert response.status_code == 400

    def test_batch_too_large(self):
        response = client.post(
            "/v1/romanize/batch",
            json={"texts": ["test"] * 101},
        )
        assert response.status_code == 400

    def test_batch_results_have_romanized(self):
        response = client.post(
            "/v1/romanize/batch",
            json={"texts": ["Привет", "नमस्ते"]},
        )
        assert response.status_code == 200
        data = response.json()
        for result in data["results"]:
            assert "original" in result
            assert "romanized" in result


class TestLanguagesEndpoint:
    """Tests for /v1/languages GET endpoint."""

    def test_list_languages(self):
        response = client.get("/v1/languages")
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        assert "styles" in data

    def test_languages_has_expected_entries(self):
        response = client.get("/v1/languages")
        data = response.json()
        codes = [lang["code"] for lang in data["languages"]]
        assert "ru" in codes
        assert "hi" in codes
        assert "zh" in codes
        assert "ko" in codes

    def test_styles_has_expected_entries(self):
        response = client.get("/v1/languages")
        data = response.json()
        style_ids = [s["id"] for s in data["styles"]]
        assert "standard" in style_ids
        assert "academic" in style_ids
        assert "chat" in style_ids


class TestCacheEndpoint:
    """Tests for cache management endpoints."""

    def test_cache_stats(self):
        response = client.get("/v1/cache/stats")
        assert response.status_code == 200
        data = response.json()
        assert "enabled" in data

    def test_cache_clear(self):
        response = client.post("/v1/cache/clear")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data


class TestStatsEndpoint:
    """Tests for stats endpoint."""

    def test_get_stats(self):
        response = client.get("/v1/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_requests" in data
        assert "uptime_seconds" in data
        assert "cache" in data


class TestFileEndpoint:
    """Tests for /v1/romanize/file POST endpoint."""

    def test_valid_file_romanization_succeeds(self):
        """A small .txt file should be processed and returned with status 200."""
        content = b"Hello\nWorld\n"
        response = client.post(
            "/v1/romanize/file",
            files={"file": ("sample.txt", content, "text/plain")},
            data={"style": "standard"},
        )
        assert response.status_code == 200

    def test_file_exceeding_max_lines_returns_400(self):
        """A file with more lines than MAX_FILE_LINES should return 400."""
        max_lines = 3
        # Build a file with max_lines + 1 lines (no trailing newline so line_count = max_lines + 1)
        content = "\n".join(f"line {i}" for i in range(max_lines + 1))
        with patch.object(files_module, "MAX_FILE_LINES", max_lines):
            response = client.post(
                "/v1/romanize/file",
                files={"file": ("big.txt", content.encode("utf-8"), "text/plain")},
                data={"style": "standard"},
            )
        assert response.status_code == 400
        assert f"max {max_lines}" in response.json()["detail"]

    def test_file_at_exactly_max_lines_succeeds(self):
        """A file with exactly MAX_FILE_LINES lines should be accepted (boundary)."""
        max_lines = 3
        # Build a file with exactly max_lines lines (no trailing newline)
        content = "\n".join(f"line {i}" for i in range(max_lines))
        with patch.object(files_module, "MAX_FILE_LINES", max_lines):
            response = client.post(
                "/v1/romanize/file",
                files={"file": ("boundary.txt", content.encode("utf-8"), "text/plain")},
                data={"style": "standard"},
            )
        assert response.status_code == 200
