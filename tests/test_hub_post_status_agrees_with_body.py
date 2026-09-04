#!/usr/bin/env python3
"""A POST route that refuses must not answer 200.

Every handler in `do_POST` used to return `self._json(result)` with no status,
so a body reading `{"ok": false, "error": "tablero_no_encontrado"}` went out as
200. The malformed-input guards in the same dispatcher already answer 400
(`json invalido`, `content_length_invalido`), which left the caller able to
tell a broken request from a good one and unable to tell a good request from a
refused one. A panel can read the body; a probe, a retry policy or a proxy
reads the code.

Each case here drives a real handler with a body that makes it refuse, and
asserts the status the file already assigns to that error class elsewhere:
404 for a named thing that does not exist, 400 for input the route cannot act
on, 503 for a dependency that is not answering.

The handlers are called with bodies that fail before any write. The write path
is covered by tests/test_hub_durable_writers.py and is not re-entered here.
"""
from __future__ import annotations

import io
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "cultura", "mak_plataforma"))

import hub  # noqa: E402


def _status_agrees_with_the_body(payload: dict, code: int) -> None:
    """The status must match whatever error came back, not only the hoped-for one.

    The two 404 cases below used to `pytest.skip` when the route refused with a
    different error than the one they were written for. That switched the
    contract off exactly when the route took a path the test did not predict,
    which is when it is worth checking -- and one of them did take another
    path, so its rule went unverified from the day it was written.

    Which error arrives is data. The agreement between that error and the HTTP
    status is the contract, and it holds for every error the table names.
    """
    error = payload.get("error")
    assert error, f"expected a refusal, got {payload!r} with status {code}"
    if error in hub._ERROR_STATUS_LEFT_AT_200:
        assert code == 200, (
            f"{error!r} is a documented exclusion and must stay 200, got {code}"
        )
        return
    expected = hub._ERROR_STATUS.get(error)
    assert expected is not None, (
        f"the route answered {error!r} and no rule says what status that is. "
        "Add it to `_ERROR_STATUS`, or to `_ERROR_STATUS_LEFT_AT_200` with the "
        "reason it is not an error."
    )
    assert code == expected, (
        f"{error!r} is declared as {expected} and the route answered {code}"
    )


class FakeHandler:
    """Capture what the dispatcher answers without opening a socket."""

    def __init__(self, path: str, body: dict | None = None) -> None:
        raw = json.dumps(body if body is not None else {}).encode("utf-8")
        self.path = path
        self.rfile = io.BytesIO(raw)
        self.headers = {"Content-Length": str(len(raw))}
        self.command = "POST"
        self.calls: list[tuple] = []
        self.redirect: dict | None = None

    def _json(self, obj, code=200):
        self.calls.append(("json", obj, code))

    def _send(self, body_text, ctype="text/html; charset=utf-8", code=200):
        self.calls.append(("send", body_text, code))

    def _send_bytes(self, data, ctype="application/octet-stream", code=200):
        self.calls.append(("bytes", data, code))

    def send_response(self, code):
        self.redirect = {"code": code}

    def send_header(self, key, value):
        assert self.redirect is not None
        self.redirect.setdefault("headers", {})[key] = value

    def end_headers(self):
        pass


def _post(path: str, body: dict | None = None) -> tuple[dict, int]:
    handler = FakeHandler(path, body)
    hub.H.do_POST(handler)
    assert handler.calls, f"POST {path} answered nothing"
    kind, payload, code = handler.calls[-1]
    assert kind == "json", f"POST {path} answered {kind}, not json"
    return payload, code


class TestStatusTable:
    def test_the_table_and_the_deliberate_exclusions_do_not_overlap(self) -> None:
        # An error in both lists would mean the file contradicts its own note
        # about what it chose to leave at 200.
        overlap = set(hub._ERROR_STATUS) & set(hub._ERROR_STATUS_LEFT_AT_200)
        assert not overlap, f"listed as both mapped and left at 200: {sorted(overlap)}"

    def test_every_mapped_status_is_a_failure_code(self) -> None:
        for error, code in hub._ERROR_STATUS.items():
            assert 400 <= code < 600, f"{error} maps to {code}, which is not a failure"

    def test_an_unmapped_error_stays_two_hundred(self) -> None:
        # The default is deliberate: guessing a status from an unrecognised
        # string would change routes nobody measured.
        assert hub._status_for({"ok": False, "error": "algo_que_nadie_mapeo"}) == 200

    @pytest.mark.parametrize("error", sorted(hub._ERROR_STATUS_LEFT_AT_200))
    def test_the_outcomes_left_at_two_hundred_stay_there(self, error: str) -> None:
        assert hub._status_for({"ok": False, "error": error}) == 200


class TestNotFoundAnswers404:
    def test_dispatch_of_an_unknown_item(self) -> None:
        # `depto` had to be a real department. `_portfolio_dispatch`
        # checks it before it looks the item up, so the old `"cultura"`
        # was refused as `departamento_invalido` and this test skipped
        # every run since it was written: it never reached its subject.
        payload, code = _post(
            "/api/portfolio/dispatch",
            {"item_id": "no-existe-en-ningun-inbox", "depto": "research",
             "texto": "x"},
        )
        assert payload.get("error") == "item_no_encontrado", (
            f"the route refused before reaching the lookup: {payload!r}"
        )
        _status_agrees_with_the_body(payload, code)
        assert code == 404

    def test_board_action_on_an_unknown_board(self) -> None:
        payload, code = _post(
            "/api/portfolio/board",
            {"accion": "renombrar", "board_id": "tablero-que-no-existe",
             "nombre": "x"},
        )
        assert payload.get("error") == "tablero_no_encontrado", (
            f"the route refused before reaching the lookup: {payload!r}"
        )
        _status_agrees_with_the_body(payload, code)
        assert code == 404


class TestBadRequestAnswers400:
    def test_board_action_with_an_unknown_action(self) -> None:
        # The handler resolves the board before the action, so an unknown
        # action on an unknown board reports the board. Either refusal is a
        # failure and neither may go out as 200.
        payload, code = _post("/api/portfolio/board", {"accion": "no-es-una-accion"})
        assert payload.get("ok") is False
        assert code in (400, 404), payload

    def test_dispatch_to_an_unknown_department(self) -> None:
        payload, code = _post(
            "/api/portfolio/dispatch",
            {"item_id": "x", "depto": "departamento-inexistente", "texto": "y"},
        )
        if payload.get("error") == "departamento_invalido":
            assert code == 400
        else:
            pytest.skip(f"the route refused earlier with {payload.get('error')!r}")

    def test_xio_link_without_a_source_id(self) -> None:
        payload, code = _post("/api/portfolio/copilot/xio-link", {})
        assert payload.get("ok") is False
        assert code in (400, 503), (
            f"a missing source_id or an absent evidence store, not {code}: {payload}"
        )

    def test_classify_batch_with_an_empty_group(self) -> None:
        payload, code = _post("/api/portfolio/classify-batch", {})
        assert payload.get("ok") is False
        assert code == 400, payload

    def test_connect_with_invalid_items(self) -> None:
        payload, code = _post("/api/portfolio/connect", {"items": []})
        if payload.get("error") == "items_invalidos":
            assert code == 400
        else:
            pytest.skip(f"the route refused earlier with {payload.get('error')!r}")


class TestMalformedInputStillAnswers400:
    """The guards that already worked must not have been disturbed."""

    def test_a_body_that_is_not_json(self) -> None:
        handler = FakeHandler("/api/portfolio/board")
        handler.rfile = io.BytesIO(b"{no es json")
        handler.headers = {"Content-Length": "11"}
        hub.H.do_POST(handler)
        _, payload, code = handler.calls[-1]
        assert code == 400
        assert payload == {"ok": False, "error": "json invalido"}


# Every POST path this dispatcher recognises, one per Content-Length guard.
# A header is caller input: four routes guarded it and seven did not, and on
# those seven `int()` raised straight out of do_POST -- a 500 with a traceback
# for what the guarded routes answer as a named 400.
POST_PATHS = [
    "/api/project/route",
    "/api/project/probe",
    "/api/diagnostics",
    "/api/portfolio/evidence-decision",
    "/api/revision/episodios",
    "/api/revision",
    "/api/portfolio/board",
    "/api/portfolio/select",
    "/api/portfolio/classify",
    "/api/portfolio/classify-batch",
    "/api/portfolio/draft",
    "/api/portfolio/commit",
    "/api/portfolio/undo",
    "/api/portfolio/dispatch",
    "/api/portfolio/connect",
    "/api/portfolio/feedback",
    "/api/portfolio/triangulation/review",
    "/api/portfolio/triangulation/context-link",
    "/api/portfolio/copilot/xio-link",
    "/api/portfolio/copilot/external",
    "/api/portfolio/copilot/vision",
    "/api/portfolio/external-candidates/review",
    "/api/director/work",
    "/api/director/decision",
    "/api/ejecutar",
    "/api/ideas",
    "/api/render",
]


class TestContentLengthIsNeverTrusted:
    @pytest.mark.parametrize("path", POST_PATHS)
    def test_a_non_numeric_content_length_is_a_named_400(self, path: str) -> None:
        handler = FakeHandler(path)
        handler.headers = {"Content-Length": "no-es-un-numero"}

        try:
            hub.H.do_POST(handler)
        except Exception as error:  # noqa: BLE001 - that is the defect
            pytest.fail(
                f"POST {path} raised {type(error).__name__} on a non-numeric "
                f"Content-Length: {error}"
            )

        assert handler.calls, f"POST {path} answered nothing"
        _, payload, code = handler.calls[-1]
        assert code == 400, f"POST {path} answered {code}: {payload}"
        assert payload.get("error") == "content_length_invalido", payload

    @pytest.mark.parametrize("path", POST_PATHS)
    def test_an_absent_content_length_does_not_raise(self, path: str) -> None:
        handler = FakeHandler(path)
        handler.headers = {}

        try:
            hub.H.do_POST(handler)
        except Exception as error:  # noqa: BLE001
            pytest.fail(
                f"POST {path} raised {type(error).__name__} with no "
                f"Content-Length header: {error}"
            )


# Every field the POST dispatcher reads out of a body, so one hostile body
# reaches whichever fields a given route uses.
BODY_FIELDS = [
    "item_id", "board_id", "decision", "accion", "nombre", "items", "grupo",
    "clasificacion", "depto", "texto", "note", "session_id", "pass_size",
    "decision_scope", "reason_code", "target_id", "source_id", "segment_id",
    "work_id", "proveedor", "scope", "video", "episodio", "modo", "densidad",
    "question", "project_id", "format_id", "text", "context_id",
]

# A field the handler reads as text can arrive as any JSON type. None of these
# is a valid request; all of them must be refused rather than raise.
CONFUSED_VALUES = {
    "numero": 7,
    "lista": [1, 2],
    "objeto": {"a": 1},
    "nulo": None,
    "booleano": True,
    "cadena vacia": "",
}


class TestTypeConfusedBodies:
    @pytest.mark.parametrize("label,value", sorted(CONFUSED_VALUES.items(), key=str))
    @pytest.mark.parametrize("path", POST_PATHS)
    def test_a_body_of_the_wrong_types_is_refused_not_raised(
        self, path: str, label: str, value: object
    ) -> None:
        handler = FakeHandler(path, {field: value for field in BODY_FIELDS})

        try:
            hub.H.do_POST(handler)
        except Exception as error:  # noqa: BLE001 - that would be the defect
            pytest.fail(
                f"POST {path} raised {type(error).__name__} on a body whose "
                f"fields are {label}: {error}"
            )

        assert handler.calls, f"POST {path} answered nothing for a {label} body"


class TestSuccessIsStillTwoHundred:
    def test_a_route_that_does_not_refuse_keeps_its_two_hundred(self) -> None:
        # `_status_for` only looks at bodies that declare failure, so an `ok`
        # answer must be untouched by this change.
        assert hub._status_for({"ok": True, "items": []}) == 200
        assert hub._status_for({"schema": "x", "rows": []}) == 200
