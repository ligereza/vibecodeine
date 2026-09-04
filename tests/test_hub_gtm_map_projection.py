#!/usr/bin/env python3
"""`/api/portfolio/copilot/map?fields=map` ships positions, not predictions.

Measured 2026-09-04: the default answer is 4,367,883 bytes and `items` is
100.0% of it -- 7044 rows each carrying `triage_prediction` (412 bytes) and
`features` alongside the position. The only consumer, `iskvw/editor.html`,
reads `item_id`, `x` and `y`, computes its own distance and never opens the
rest. The panel calls this route while the operator moves through pieces.

The projection is opt-in. The default shape stays exactly as it was, because
the engine contract is tested against the full item in tests/test_copilot.py
and a caller that wants the predictions must keep getting them.
"""
from __future__ import annotations

import io
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "cultura", "mak_plataforma"))

import hub  # noqa: E402

ROUTE = "/api/portfolio/copilot/map"


class FakeHandler:
    def __init__(self, path: str) -> None:
        self.path = path
        self.rfile = io.BytesIO(b"")
        self.headers = {}
        self.command = "GET"
        self.calls: list[tuple] = []
        self.redirect: dict | None = None

    def _json(self, obj, code=200):
        self.calls.append(("json", obj, code))

    def _send(self, body, ctype="text/html; charset=utf-8", code=200):
        self.calls.append(("send", body, code))

    def _send_bytes(self, data, ctype="application/octet-stream", code=200):
        self.calls.append(("bytes", data, code))

    def send_response(self, code):
        self.redirect = {"code": code}

    def send_header(self, key, value):
        assert self.redirect is not None
        self.redirect.setdefault("headers", {})[key] = value

    def end_headers(self):
        pass


def _get(query: str) -> dict:
    handler = FakeHandler(f"{ROUTE}?{query}")
    hub.H.do_GET(handler)
    assert handler.calls, "the map route answered nothing"
    kind, payload, _ = handler.calls[-1]
    assert kind == "json"
    return payload


@pytest.fixture(scope="module")
def answers() -> tuple[dict, dict]:
    _get("width=4&height=3")  # warm the engine cache; both calls then compare
    return _get("width=4&height=3"), _get("width=4&height=3&fields=map")


class TestProjection:
    def test_the_positions_the_panel_reads_are_unchanged(self, answers) -> None:
        full, lean = answers
        assert len(full["items"]) == len(lean["items"])
        for row_full, row_lean in zip(full["items"], lean["items"]):
            for key in ("item_id", "x", "y"):
                assert row_full[key] == row_lean[key]

    def test_an_item_carries_only_what_a_map_needs(self, answers) -> None:
        _, lean = answers
        if not lean["items"]:
            pytest.skip("the inbox is empty in this checkout")
        assert set(lean["items"][0]) <= set(hub._GTM_MAP_ITEM_FIELDS)

    def test_the_heavy_fields_are_gone(self, answers) -> None:
        full, lean = answers
        if not full["items"]:
            pytest.skip("the inbox is empty in this checkout")
        assert "triage_prediction" in full["items"][0], (
            "the default answer stopped carrying the predictions; this test "
            "compares against them and would pass while measuring nothing"
        )
        assert "triage_prediction" not in lean["items"][0]
        assert "features" not in lean["items"][0]

    def test_the_answer_says_it_was_projected(self, answers) -> None:
        _, lean = answers
        assert lean["fields"] == "map"

    def test_the_top_level_shape_is_preserved(self, answers) -> None:
        full, lean = answers
        assert set(full) <= set(lean), "the projection dropped a top-level key"
        for key in ("schema", "engine", "grid", "count"):
            if key in full:
                assert lean[key] == full[key]

    def test_it_is_materially_smaller(self, answers) -> None:
        full, lean = answers
        if len(full["items"]) < 50:
            pytest.skip("too few items in this checkout for the size to mean anything")
        full_bytes = len(json.dumps(full, ensure_ascii=False))
        lean_bytes = len(json.dumps(lean, ensure_ascii=False))
        assert lean_bytes < full_bytes / 2, (
            f"projection saved only {100 - lean_bytes / full_bytes * 100:.1f}%"
        )


class TestDefaultIsUntouched:
    def test_without_the_parameter_nothing_changes(self, answers) -> None:
        full, _ = answers
        assert "fields" not in full
        if full["items"]:
            assert "triage_prediction" in full["items"][0]

    @pytest.mark.parametrize("value", ["", "todo", "full", "1", "MAP"])
    def test_only_the_exact_value_projects(self, value: str) -> None:
        # A typo must not silently strip data the caller expected.
        payload = _get(f"width=4&height=3&fields={value}")
        assert "fields" not in payload or payload.get("fields") != "map"


class TestTheOnlyConsumerAsksForIt:
    def test_the_editor_requests_the_projection(self) -> None:
        # If the panel stops asking, the projection is dead code and the 4 MB
        # answer is back without anybody noticing.
        editor = os.path.join(os.path.dirname(__file__), "..", "iskvw", "editor.html")
        source = open(editor, encoding="utf-8").read()
        assert "copilot/map?" in source, "the editor no longer calls the map route"
        call = source[source.index("copilot/map?"):][:120]
        assert "fields=map" in call, f"the editor asks for the full payload: {call!r}"

    def test_the_editor_only_reads_projected_fields(self) -> None:
        editor = os.path.join(os.path.dirname(__file__), "..", "iskvw", "editor.html")
        source = open(editor, encoding="utf-8").read()
        start = source.index("copilot/map?")
        block = source[start:start + 1600]
        for dropped in ("triage_prediction", "item.features", "item.bmu"):
            assert dropped not in block, (
                f"the panel reads {dropped}, which fields=map no longer sends"
            )
