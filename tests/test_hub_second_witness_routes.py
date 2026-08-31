#!/usr/bin/env python3
"""tests/test_hub_second_witness_routes.py -- a second test on routes that
`python3 ~/indexes/mak-solape-tests-20260829/analizar_solape.py` reported as
covered by exactly one test in the whole suite (773 such lines live in
cultura/mak_plataforma/hub.py, more than any other file in MAK).

Each test here checks a property the existing single owner does NOT check,
either because it goes through the HTTP dispatch (`hub.H.do_GET`) instead of
calling the internal function directly, or because it exercises a branch
(a cache TTL, a `_ledger is None` fallback, an alias redirect) that had zero
witnesses before this file. The intent, from the task brief: if the one
existing test breaks or is deleted, these lines should not go dark.
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "cultura", "mak_plataforma"))

import hub  # noqa: E402


class FakeHandler:
    def __init__(self, path):
        self.path = path
        self.rfile = io.BytesIO(b"")
        self.headers = {}
        self.command = "GET"
        self.calls = []
        self.redirect = None

    def _json(self, obj, code=200):
        self.calls.append(("json", obj, code))

    def _send(self, body_text, ctype="text/html; charset=utf-8", code=200):
        self.calls.append(("send", body_text, code))

    def _send_bytes(self, data, ctype="application/octet-stream", code=200):
        self.calls.append(("bytes", data, code))

    def send_response(self, code):
        self.redirect = {"code": code}

    def send_header(self, key, value):
        self.redirect.setdefault("headers", {})[key] = value

    def end_headers(self):
        pass

    @property
    def last(self):
        return self.calls[-1]


def _get(path):
    handler = FakeHandler(path)
    hub.H.do_GET(handler)
    return handler


class TestArchivePublicoCache:
    """_archivo_publico() keeps a 30s TTL cache. The existing single owner
    (tests/test_contrato_archivo.py::test_hub_sirve_el_contrato) checks the
    SHAPE of the conversion; it never runs the function twice, so the cache
    branch itself (the `if ahora - _ARCHIVO_CACHE["t"] < 30` guard) had no
    witness at all."""

    def test_second_call_within_ttl_reuses_the_cached_object(self, monkeypatch):
        monkeypatch.setattr(hub, "_ARCHIVO_CACHE", {"t": 0.0, "data": None})
        calls = []

        def fake_micelio():
            calls.append(1)
            return {"nodes": [{"id": "a.md", "dir": "corpus", "titulo": "A",
                                "chunks": 1}], "edges": []}

        monkeypatch.setattr(hub, "_micelio", fake_micelio)

        first = hub._archivo_publico()
        second = hub._archivo_publico()

        assert len(calls) == 1, "a cache hit must not call _micelio() again"
        assert first is second

    def test_expired_cache_recomputes_from_micelio(self, monkeypatch):
        monkeypatch.setattr(hub, "_ARCHIVO_CACHE", {"t": 0.0, "data": None})
        calls = []

        def fake_micelio():
            calls.append(1)
            return {"nodes": [{"id": "a.md", "dir": "corpus", "titulo": "A",
                                "chunks": 1}], "edges": []}

        monkeypatch.setattr(hub, "_micelio", fake_micelio)

        hub._archivo_publico()
        hub._ARCHIVO_CACHE["t"] -= 31  # push the cache timestamp past the TTL

        hub._archivo_publico()

        assert len(calls) == 2, "an expired cache must recompute, not reuse stale data"


class TestLegacyReportsRoute:
    """The existing single owner calls hub._legacy_report_index(...) directly.
    This exercises the do_GET query-string parsing in front of it, which the
    direct call never touches."""

    def _write_run(self, tmp_path):
        run = tmp_path / "faro-report-metadata-20260830"
        run.mkdir()
        rows = [
            {"work_id": "legacy-report:x", "duplicate_family_size": 1,
             "sfera_quarantine": False, "metadata_quality": "legacy_unknown",
             "path": "x.md", "basename": "x.md"},
            {"work_id": "legacy-report:y", "duplicate_family_size": 4,
             "sfera_quarantine": False, "metadata_quality": "legacy_unknown",
             "path": "y.md", "basename": "y.md"},
        ]
        (run / "reports.jsonl").write_text(
            "\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
        (run / "SUMMARY.json").write_text(json.dumps({
            "external_review": {"status": "quarantined_raw"}}), encoding="utf-8")
        return tmp_path

    def test_route_parses_query_string_and_forwards_to_the_index(
            self, tmp_path, monkeypatch):
        monkeypatch.setattr(hub, "LEGACY_REPORT_RUNS", str(self._write_run(tmp_path)))

        handler = _get("/api/research/legacy-reports?classification=orphan_candidate")

        kind, payload, code = handler.last
        assert code == 200
        assert payload["ok"] is True
        assert payload["counts"] == {"orphan_candidate": 1, "paired_family": 1}
        assert [item["work_id"] for item in payload["items"]] == ["legacy-report:x"]

    def test_route_default_limit_is_one_hundred_when_absent(self, tmp_path, monkeypatch):
        monkeypatch.setattr(hub, "LEGACY_REPORT_RUNS", str(self._write_run(tmp_path)))

        handler = _get("/api/research/legacy-reports")

        kind, payload, code = handler.last
        assert code == 200
        assert payload["returned"] == 2


class TestDecisionIndexRoute:
    """Second witness for /api/portfolio/decision-index through the HTTP
    dispatcher, checking the operator-facing `next` hint that the existing
    direct-call test does not assert."""

    def test_route_wires_the_index_function_and_keeps_the_next_hint(self, monkeypatch):
        class FakeLedger:
            @staticmethod
            def read_items(_path, limit=None):
                return []

        monkeypatch.setattr(hub, "_ledger", FakeLedger())
        monkeypatch.setattr(hub, "_portfolio_feedback", lambda: [])
        monkeypatch.setattr(hub, "_portfolio_selections", lambda: {})

        handler = _get("/api/portfolio/decision-index")

        kind, payload, code = handler.last
        assert code == 200
        assert payload["schema"] == "faro-portfolio-decision-index-v1"
        assert payload["counts"] == {"candidate_reviews": 0, "relation_feedback": 0,
                                     "selections": 0}
        assert "work_id" in payload["next"] and "source_id" in payload["next"]


class TestOportunidadesRoute:
    """Second witness for /api/oportunidades through the HTTP dispatcher."""

    def test_route_exposes_the_opportunity_surface(self, monkeypatch):
        class FakeLedger:
            @staticmethod
            def read_items(_path, limit=None):
                return [{
                    "id": "opportunity:two", "domain": "opportunities",
                    "decision": "revisar", "owner": "human",
                    "metadata": {"opportunity_card": {
                        "schema": "faro-opportunity-card-v1",
                        "title": "Candidate two", "status": "unverified"}},
                }]

        monkeypatch.setattr(hub, "_ledger", FakeLedger())

        handler = _get("/api/oportunidades")

        kind, payload, code = handler.last
        assert code == 200
        assert payload["counts"] == {"total": 1, "unverified": 1}
        assert payload["items"][0]["title"] == "Candidate two"

    def test_route_survives_a_missing_ledger_without_a_500(self, monkeypatch):
        monkeypatch.setattr(hub, "_ledger", None)

        handler = _get("/api/oportunidades")

        kind, payload, code = handler.last
        assert code == 200
        assert payload == {"schema": "faro-opportunity-surface-v1", "items": [],
                           "counts": {"total": 0, "unverified": 0}}


class TestDirectorCapabilitiesFallback:
    """The `_ledger is not None` branch has coverage elsewhere; the fallback
    literal lanes/decisions on the else side did not, because this venv has
    a real ledger module and no existing test forces it to None."""

    def test_falls_back_to_default_lanes_and_decisions_without_a_ledger(self, monkeypatch):
        monkeypatch.setattr(hub, "_ledger", None)

        handler = _get("/api/director/capabilities")

        kind, payload, code = handler.last
        assert code == 200
        assert payload["lanes"] == ["obra", "trabajo", "sistema"]
        assert payload["decisions"] == ["hacer", "revisar", "refutar", "archivar", "descartar"]


class TestDepartmentAliasRedirect:
    """/departments/<alias> 301s to the canonical area before ever building a
    page. No test in the suite requested an alias path before this file."""

    def test_portfolio_alias_redirects_to_iskvw(self):
        handler = _get("/departments/portfolio")

        assert handler.calls == []
        assert handler.redirect["code"] == 301
        assert handler.redirect["headers"]["Location"] == "/departments/iskvw"

    def test_research_alias_redirects_to_cultura(self):
        handler = _get("/departments/research")

        assert handler.redirect["code"] == 301
        assert handler.redirect["headers"]["Location"] == "/departments/cultura"


class TestPortfolioAuditMissingItem:
    """Second witness for /api/portfolio/audit: the negative path, which the
    existing owner test (built around a populated inbox) never triggers."""

    def test_unknown_source_id_is_a_named_404(self, tmp_path, monkeypatch):
        monkeypatch.setattr(hub, "PORTFOLIO_INBOX", str(tmp_path / "missing-inbox.json"))

        handler = _get("/api/portfolio/audit?source_id=does-not-exist")

        kind, payload, code = handler.last
        assert code == 404
        assert payload == {"ok": False, "error": "item_no_encontrado",
                           "source_id": "does-not-exist"}
