"""Tests for the bounded public-source capture gate."""

from __future__ import annotations

import json
from pathlib import Path

from tools import research_source_capture as capture


def test_default_capture_is_a_plan_and_makes_no_network_call(tmp_path: Path) -> None:
    result = capture.capture_one("https://Example.org/path?b=2&a=1", root=tmp_path)
    assert result["decision"] == "plan"
    assert result["url"] == "https://example.org/path?a=1&b=2"
    assert result["network_called"] is False
    assert not (tmp_path / "sources.sqlite").exists()


def test_recorded_capture_keeps_backend_and_receipt(tmp_path: Path) -> None:
    def fake_capture(url: str, **_kwargs: object) -> dict[str, object]:
        return {
            "url": url,
            "status": "captured",
            "backend": "fixture",
            "raw_sha256": "a" * 64,
            "text": "official fixture text",
            "attempts": [{"backend": "fixture", "status": "captured"}],
            "links": [],
            "metadata": {"license": "fixture"},
        }

    result = capture.capture_one(
        "https://example.org/official",
        root=tmp_path,
        record=True,
        capture=fake_capture,
    )
    assert result["decision"] == "record"
    assert result["network_called"] is True
    assert result["capture"]["used_backend"] == "fixture"
    assert result["receipt"]["status"] == "captured"
    assert result["store_summary"] == {"discovered": 0, "captured": 1, "failed": 0}


def test_invalid_url_abstains_without_writing(tmp_path: Path) -> None:
    result = capture.capture_one("not-a-url", root=tmp_path, record=True)
    assert result["decision"] == "abstain"
    assert result["reason"] == "invalid_public_url"
