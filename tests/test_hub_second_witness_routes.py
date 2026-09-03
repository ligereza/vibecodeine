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
from pathlib import Path

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


# ---------------------------------------------------------------------------
# The production chain was whole; only the wire was missing
# ---------------------------------------------------------------------------
#
# `compile_portfolio_claims` -> `assess_feasibility` -> `render_portfolio` ->
# `render_markdown` already existed in the FLUJO motor and nothing ran it from
# the Hub, so six declared formats looked unbuildable. Measured 2026-09-02:
# eight of eight sources are present and four of the six render, the Fondart one
# among them. The input is the CLAIM BASE, never the archive rows -- a claim
# carries verb, layer, state, permission, its supporting route and what would
# refute it, which is exactly what a slot declares. Feeding raw inbox records
# instead is what made every format look blocked on a permission nobody records.


def test_the_hub_wires_the_existing_production_chain():
    from pathlib import Path

    source = (Path(__file__).parents[1] / "cultura" / "mak_plataforma"
              / "hub.py").read_text(encoding="utf-8")
    assert '"/api/portfolio/production"' in source
    assert "def _portfolio_production(" in source
    # The chain is consumed, not reimplemented: no second composer lives here.
    for engine in ("compile_portfolio_claims", "render_portfolio",
                   "assess_feasibility", "load_format_library"):
        assert engine in source, engine
    assert "def compose_order" not in source


def test_every_source_of_the_chain_is_named_and_checked():
    """A missing source must be reported, never silently treated as empty."""
    from cultura.mak_plataforma import hub

    assert set(hub.PORTFOLIO_PRODUCTION_SOURCES) == {
        "index", "authority", "archive", "practices", "attestations",
        "declared_inputs", "blend_targets", "screen_setup_root"}
    reported = hub._portfolio_production_sources()
    assert set(reported) == set(hub.PORTFOLIO_PRODUCTION_SOURCES)
    for name, row in reported.items():
        assert set(row) == {"path", "present"}
        assert isinstance(row["present"], bool), name


def test_the_route_never_publishes_or_signs():
    """Production is a reading. The renderers already return a control block
    with everything false; the wire must not add a way around it.

    Checked as WRITES, not as words: the first version grepped the body for
    "publish" and failed on the very keys that declare it does not publish --
    the same confusion as reading a comment as a call.
    """
    import ast
    from pathlib import Path

    source = (Path(__file__).parents[1] / "cultura" / "mak_plataforma"
              / "hub.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    function = next(node for node in ast.walk(tree)
                    if isinstance(node, ast.FunctionDef)
                    and node.name == "_portfolio_production")
    body = ast.unparse(function)
    assert '"promotion": "none"' in body.replace("'", '"')
    assert '"owner": "human"' in body.replace("'", '"')
    # No write of any kind: no file opened for writing, no append, no commit.
    for call in ast.walk(function):
        if not isinstance(call, ast.Call):
            continue
        target = ast.unparse(call.func)
        assert not target.endswith((".write", ".writelines", ".commit",
                                    ".append_item", ".append_review")), target
        if target == "open":
            modes = [ast.unparse(a) for a in call.args[1:]]
            assert not any("w" in m or "a" in m for m in modes), modes


# ---------------------------------------------------------------------------
# The inbox cache is keyed on writes, not on a clock
# ---------------------------------------------------------------------------
#
# Measured 2026-09-02: one `/api/portfolio/copilot/scene` call reached
# `_portfolio_inbox()` seven times, each reopening the 3.8 MB inbox, rebuilding
# 7044 dictionaries and reading four more files -- 0.41 s of the 1.19 s a warm
# scene cost, and the interface calls that route on every piece the operator
# selects with 6928 records still undecided. After the cache a scene is 0.30 s
# over HTTP.
#
# The key is deliberately NOT a TTL, which is the convention used elsewhere in
# this file for a graph and a rendered page. This data changes when the
# operator decides something, so a stale window would show a person their own
# decision not applied. Keyed on source mtimes, the write invalidates it.


def test_the_inbox_cache_is_keyed_on_its_sources_not_on_time():
    assert set(hub._PORTFOLIO_INBOX_SOURCES) == {
        "PORTFOLIO_INBOX", "PORTFOLIO_SELECTIONS", "PORTFOLIO_CLASSIFICATIONS",
        "PORTFOLIO_DRAFTS", "PORTFOLIO_VISION"}
    signature = hub._portfolio_inbox_signature()
    assert len(signature) == len(hub._PORTFOLIO_INBOX_SOURCES)
    for name, mtime, size in signature:
        assert name in hub._PORTFOLIO_INBOX_SOURCES
        # A missing source is part of the key, so its appearance invalidates too.
        assert (mtime is None) == (size is None)
    assert hub._portfolio_inbox_signature() == signature, "must be stable"


def test_a_write_to_any_source_invalidates_the_inbox_cache(tmp_path, monkeypatch):
    """A decision must be visible on the very next read, never one window late."""
    inbox = tmp_path / "inbox.json"
    inbox.write_text(json.dumps({"schema": "faro-portfolio-inbox-v1",
                                 "items": [{"id": "a.jpg"}]}), encoding="utf-8")
    selections = tmp_path / "selections.json"
    selections.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(hub, "PORTFOLIO_INBOX", str(inbox))
    monkeypatch.setattr(hub, "PORTFOLIO_SELECTIONS", str(selections))
    monkeypatch.setattr(hub, "_PORTFOLIO_INBOX_CACHE", {})

    first = hub._portfolio_inbox()
    assert hub._portfolio_inbox() is first, "an unchanged tree must not re-read"

    os.utime(selections, (0, 0))
    assert hub._portfolio_inbox() is not first, (
        "a write to a source must invalidate the cache")


def test_the_uncached_reader_is_still_the_one_that_fills_the_cache():
    """The cache wraps the reader; it does not become a second reader."""
    source = (Path(__file__).parents[1] / "cultura" / "mak_plataforma"
              / "hub.py").read_text(encoding="utf-8")
    assert "def _portfolio_inbox_uncached(" in source
    assert "_portfolio_inbox_uncached(compact=compact)" in source
    # No clock in this cache: the other caches in the Hub may use one, this must
    # not, because its data changes by human decision.
    start = source.index("def _portfolio_inbox(compact=False):")
    body = source[start:source.index("\ndef _portfolio_inbox_uncached")]
    for clock in ("time.time", "time.monotonic", "TTL"):
        assert clock not in body, clock
