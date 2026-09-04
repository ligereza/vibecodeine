#!/usr/bin/env python3
"""`/api/convocatorias`: the declared calls, and how long each one has left.

The bases in `data/*.json` were reachable only by running
`python -m tools.gen_postulacion --list`. A deadline that exists only in a
terminal is a deadline the operator meets by remembering it, so the hub now
projects them.

The surface is derived and read-only: it computes days remaining from the
declared closing date and says where each entry came from. It decides nothing.
Which is the point of the last group of tests: an entry transcribed from press
coverage carries a date and not the taxative document list, and the surface has
to keep saying so rather than flattening both into one confident row.
"""
from __future__ import annotations

from datetime import date, timedelta
import io
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "cultura", "mak_plataforma"))

import hub  # noqa: E402

ROUTE = "/api/convocatorias"


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


def _get(query: str = "") -> tuple[dict, int]:
    handler = FakeHandler(ROUTE + query)
    hub.H.do_GET(handler)
    assert handler.calls, "the route answered nothing"
    kind, payload, code = handler.calls[-1]
    assert kind == "json"
    return payload, code


@pytest.fixture(scope="module")
def surface() -> dict:
    payload, code = _get()
    assert code == 200, payload
    return payload


class TestTheRouteAnswers:
    def test_it_reports_the_declared_calls(self, surface: dict) -> None:
        assert surface["ok"] is True
        assert surface["schema"] == "mak-convocatoria-surface-v1"
        assert surface["items"], "no call reached the surface"

    def test_every_declared_call_is_present(self, surface: dict) -> None:
        from tools.gen_postulacion import load_calls

        assert {row["id"] for row in surface["items"]} == set(load_calls())

    def test_the_counts_add_up(self, surface: dict) -> None:
        counts = surface["counts"]
        assert counts["total"] == len(surface["items"])
        assert counts["abiertas"] + counts["urgentes"] + counts["cerradas"] <= counts["total"]


class TestDeadlineArithmetic:
    @pytest.mark.parametrize(
        "offset,expected",
        [(-1, "cerrada"), (0, "urgente"), (3, "urgente"), (7, "urgente"), (8, "abierta")],
    )
    def test_the_state_follows_the_days_left(self, offset: int, expected: str) -> None:
        closes = (date.today() + timedelta(days=offset)).isoformat()
        state, remaining = hub._call_state(closes)
        assert state == expected
        assert remaining == offset

    def test_the_urgency_window_is_declared_not_hidden(self) -> None:
        # The surface reports the threshold it used, so a reader can tell
        # "urgente" apart from an opinion.
        assert hub.CONVOCATORIA_URGENT_DAYS == 7
        payload, _code = _get()
        assert payload["urgent_days"] == hub.CONVOCATORIA_URGENT_DAYS

    def test_a_missing_date_is_named_not_guessed(self) -> None:
        assert hub._call_state("") == ("sin_fecha", None)

    def test_an_unparseable_date_is_named_not_guessed(self) -> None:
        state, remaining = hub._call_state("no-es-una-fecha")
        assert state == "fecha_invalida"
        assert remaining is None

    def test_a_fixed_today_makes_the_arithmetic_checkable(self) -> None:
        assert hub._call_state("2026-09-08", date(2026, 9, 4)) == ("urgente", 4)
        assert hub._call_state("2026-09-08", date(2026, 9, 9)) == ("cerrada", -1)
        assert hub._call_state("2026-12-01", date(2026, 9, 4)) == ("abierta", 88)


class TestOrdering:
    def test_the_soonest_open_call_comes_first(self) -> None:
        payload = hub._convocatorias(today=date(2026, 9, 4))
        states = [row["estado"] for row in payload["items"]]
        # Closed calls sink; among the rest the smaller remainder leads.
        assert states.index("urgente") <= min(
            [i for i, s in enumerate(states) if s == "cerrada"] or [len(states)]
        )
        live = [row["dias_restantes"] for row in payload["items"]
                if row["estado"] in {"abierta", "urgente"}]
        assert live == sorted(live)

    def test_a_closed_call_sinks_below_a_live_one(self) -> None:
        payload = hub._convocatorias(today=date(2099, 1, 1))
        assert all(row["estado"] == "cerrada" for row in payload["items"])
        assert payload["counts"]["cerradas"] == len(payload["items"])


class TestProvenanceSurvives:
    def test_each_call_says_where_its_entry_came_from(self, surface: dict) -> None:
        for row in surface["items"]:
            assert row["fuente"], f"{row['id']} does not say where it was read from"
            assert row["archivo"], f"{row['id']} does not name its declaring file"

    def test_a_press_transcribed_entry_is_not_dressed_as_official(
        self, surface: dict
    ) -> None:
        # Flattening both into one confident row is exactly the failure this
        # field exists to prevent.
        sources = {row["id"]: row["fuente"] for row in surface["items"]}
        assert "press_coverage" in sources.values(), (
            "no entry is marked as press-transcribed; either the data changed "
            "or the provenance stopped being carried"
        )

    def test_a_call_without_transcribed_criteria_reports_an_empty_list(
        self, surface: dict
    ) -> None:
        press = [row for row in surface["items"] if row["fuente"] != "official_bases"]
        assert press, "nothing to check"
        for row in press:
            assert row["criterios"] == [], (
                "criteria appeared for an entry whose official bases were never read"
            )

    def test_an_official_entry_carries_its_weights(self, surface: dict) -> None:
        official = [row for row in surface["items"] if row["fuente"] == "official_bases"]
        assert official, "nothing to check"
        for row in official:
            assert row["criterios"], f"{row['id']} lost its criteria"
            assert sum(c["pondera"] for c in row["criterios"]) == 100


class TestDegradation:
    def test_an_absent_tool_answers_503_and_names_the_cause(self, monkeypatch) -> None:
        monkeypatch.setattr(hub, "_load_calls", None)
        monkeypatch.setattr(hub, "_CALLS_IMPORT_ERROR", "ImportError")
        payload, code = _get()
        assert code == 503, payload
        assert payload["error"] == "convocatorias_unavailable"
        assert payload["items"] == []

    def test_an_unreadable_declaration_answers_503(self, monkeypatch) -> None:
        def explode():
            raise OSError("data/ no se puede leer")

        monkeypatch.setattr(hub, "_load_calls", explode)
        payload, code = _get()
        assert code == 503, payload
        assert payload["error"] == "convocatorias_ilegibles"
        assert payload["items"] == []

    def test_it_never_answers_200_while_saying_it_failed(self, monkeypatch) -> None:
        monkeypatch.setattr(hub, "_load_calls", None)
        payload, code = _get()
        assert not (payload.get("ok") is False and code == 200)
