#!/usr/bin/env python3
"""tests/test_hub_dependency_degradation.py -- what hub.py's GET/POST routes
actually return when an optional flujo.* import failed at module load time.

hub.py wraps several `from flujo... import ...` statements in try/except and
stores None on failure, so the 8900 hub keeps serving when its deployment
venv (plataforma/.venv) lacks the flujo package. This file answers the
question the task asked, not assumed: does the guarded route fail LOUD (a
named 503 a caller can branch on) or QUIET (an HTTP 200 whose body merely
sets an "ok"/"available" flag to false, indistinguishable from success to
anything that only checks the status code)?

Finding pinned here: the behavior is NOT uniform. `/api/project/route`,
`/api/project/probe` and the `/api/portfolio/evidence-*` family return a
named 503. `/api/project/learning`, `/api/project/context` and both the GET
and POST forms of `/api/diagnostics` return HTTP 200 with the failure buried
in the body. That inconsistency is recorded, not fixed here -- fixing it is
outside tests/.
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "cultura", "mak_plataforma"))

import hub  # noqa: E402


class FakeHandler:
    """A minimal stand-in for http.server's request handler.

    Only the pieces hub.H.do_GET/do_POST actually touch: `path`, `headers`,
    `rfile`, and the three response helpers it calls instead of writing to a
    real socket.
    """

    def __init__(self, path, body=b"", headers=None):
        self.path = path
        self.rfile = io.BytesIO(body)
        self.headers = headers or {"Content-Length": str(len(body))}
        self.command = "GET"
        self.calls = []

    def _json(self, obj, code=200):
        self.calls.append(("json", obj, code))

    def _send(self, body_text, ctype="text/html; charset=utf-8", code=200):
        self.calls.append(("send", body_text, code))

    def _send_bytes(self, data, ctype="application/octet-stream", code=200):
        self.calls.append(("bytes", data, code))

    @property
    def last(self):
        return self.calls[-1]


def _get(path):
    handler = FakeHandler(path)
    hub.H.do_GET(handler)
    _, payload, code = handler.last
    return payload, code


def _post(path, body):
    raw = json.dumps(body).encode("utf-8")
    handler = FakeHandler(path, body=raw)
    hub.H.do_POST(handler)
    _, payload, code = handler.last
    return payload, code


class TestDepartmentsCatalogNamedFailure:
    """department_catalog is None mirrors flujo.departments failing to import."""

    def test_departments_route_fails_named_and_carries_the_import_error(self, monkeypatch):
        monkeypatch.setattr(hub, "department_catalog", None)
        monkeypatch.setattr(hub, "_DEPARTMENTS_IMPORT_ERROR", "ModuleNotFoundError")

        payload, code = _get("/api/departments")

        assert code == 503
        assert payload == {"ok": False, "error": "departments_unavailable",
                           "detail": "ModuleNotFoundError"}

    def test_every_rd_and_cultura_route_shares_the_same_named_failure(self, monkeypatch):
        for name in ("department_catalog", "rd_summary", "rd_topics", "rd_crosswalk",
                     "rd_cultura_relations", "cultura_sources", "cultura_capabilities",
                     "cultura_opportunity_gate"):
            monkeypatch.setattr(hub, name, None)
        monkeypatch.setattr(hub, "_DEPARTMENTS_IMPORT_ERROR", "ModuleNotFoundError")

        routes_and_errors = [
            ("/api/rd/summary", "rd_summary_unavailable"),
            ("/api/rd/topics", "rd_topics_unavailable"),
            ("/api/rd/crosswalk", "rd_crosswalk_unavailable"),
            ("/api/rd/cultura-relations", "rd_cultura_relations_unavailable"),
            ("/api/cultura/sources", "cultura_sources_unavailable"),
            ("/api/cultura/capabilities", "cultura_capabilities_unavailable"),
            ("/api/cultura/opportunity-gate", "cultura_opportunity_gate_unavailable"),
        ]
        for path, error in routes_and_errors:
            payload, code = _get(path)
            assert (path, code) == (path, 503)
            assert payload["error"] == error
            assert payload["detail"] == "ModuleNotFoundError"


class TestDiagnosticsDomainsNamedFailure:
    def test_domain_catalog_missing_returns_named_503(self, monkeypatch):
        monkeypatch.setattr(hub, "domain_catalog", None)
        monkeypatch.setattr(hub, "_DIAGNOSTICS_IMPORT_ERROR", "ImportError")

        payload, code = _get("/api/diagnostics/domains")

        assert code == 503
        assert payload == {"ok": False, "error": "diagnostics_unavailable",
                           "detail": "ImportError"}


class TestDiagnosticsReportSilentDegradation:
    """Unlike domain_catalog above, the report-building path answers 200 for
    both verbs -- the caller has to read the body to notice degradation."""

    def test_get_diagnostics_degrades_to_200_not_503(self, monkeypatch):
        monkeypatch.setattr(hub, "build_diagnostic_report", None)
        monkeypatch.setattr(hub, "render_markdown", None)
        monkeypatch.setattr(hub, "_DIAGNOSTICS_IMPORT_ERROR", "ImportError")

        payload, code = _get("/api/diagnostics?area=research&idea=x")

        assert code == 200, "silent degradation: body says failure, status says OK"
        assert payload == {"ok": False, "schema": "mak-diagnostic-v1",
                           "error": "diagnostics_unavailable", "detail": "ImportError"}

    def test_post_diagnostics_shares_the_same_silent_200(self, monkeypatch):
        monkeypatch.setattr(hub, "build_diagnostic_report", None)
        monkeypatch.setattr(hub, "render_markdown", None)
        monkeypatch.setattr(hub, "_DIAGNOSTICS_IMPORT_ERROR", "ImportError")

        payload, code = _post("/api/diagnostics", {"area": "cultura", "idea": "x"})

        assert code == 200
        assert payload["ok"] is False
        assert payload["error"] == "diagnostics_unavailable"


class TestProjectRouterSplitBehavior:
    """The POST-side project router routes fail named; the GET-side
    read-only ones (next class) do not. Same import guard, two contracts."""

    def test_route_post_fails_named_with_503(self, monkeypatch):
        monkeypatch.setattr(hub, "_route_payload_api", None)
        monkeypatch.setattr(hub, "_PROJECT_ROUTER_IMPORT_ERROR", "ModuleNotFoundError")

        payload, code = _post("/api/project/route", {"text": "hola"})

        assert code == 503
        assert payload == {"ok": False, "error": "project_router_unavailable",
                           "detail": "ModuleNotFoundError"}

    def test_probe_post_fails_named_with_503(self, monkeypatch):
        monkeypatch.setattr(hub, "_probe_payload_api", None)
        monkeypatch.setattr(hub, "_PROJECT_ROUTER_IMPORT_ERROR", "ModuleNotFoundError")

        payload, code = _post("/api/project/probe", {"text": "hola"})

        assert code == 503
        assert payload["error"] == "project_router_unavailable"


class TestProjectReadOnlyForwardsItsUnavailability:
    """/api/project/learning and /api/project/context, now answering 503.

    These two assertions used to be the other way round, and on purpose: they
    pinned the defect. Both routes named their unavailability in the BODY --
    `{"available": false, "reason": "..."}` -- and still answered 200, so a
    probe, a watchdog or a proxy, all of which read the status code, saw
    success while the dependency was missing. Their siblings
    `/api/project/route` and `/api/project/probe` already answered 503 for the
    same cause, so the defect was the inconsistency, not the message.

    Pinning it was the right call: the fix of 2026-08-31 could not land
    silently, it had to break these two first. The body is unchanged -- what
    changed is that the code now agrees with it.
    """

    def test_learning_forwards_503_and_keeps_the_named_reason(self, monkeypatch):
        monkeypatch.setattr(hub, "_learning_summary_api", None)

        payload, code = _get("/api/project/learning")

        assert code == 503, "una dependencia ausente no se responde con 200"
        assert payload["available"] is False
        assert payload["reason"] == "project_router_unavailable"

    def test_context_forwards_503_and_keeps_the_named_reason(self, monkeypatch):
        monkeypatch.setattr(hub, "_project_context_api", None)

        payload, code = _get("/api/project/context?context_id=c1")

        assert code == 503
        assert payload == {"available": False, "read_only": True,
                           "reason": "project_context_unavailable", "contexts": []}

    def test_a_healthy_payload_still_answers_200(self, monkeypatch):
        """El arreglo no puede convertir en 503 una respuesta sana."""
        monkeypatch.setattr(hub, "_learning_summary_api",
                            lambda db: {"available": True, "entries": 0})
        payload, code = _get("/api/project/learning")
        assert code == 200
        assert payload["available"] is True


class TestPortfolioEvidenceNamedFailure:
    """Unlike the learning/context pair above, this guard's three routes do
    forward a 503 -- same shape of guard (`_x is None`), different contract."""

    def test_evidence_queue_fails_named(self, monkeypatch):
        monkeypatch.setattr(hub, "_portfolio_evidence", None)
        monkeypatch.setattr(hub, "_PORTFOLIO_EVIDENCE_IMPORT_ERROR", "ModuleNotFoundError")

        payload, code = _get("/api/portfolio/evidence-queue?project_id=p1")

        assert code == 503
        assert payload == {"ok": False, "error": "portfolio_evidence_unavailable",
                           "detail": "ModuleNotFoundError"}

    def test_evidence_draft_fails_named(self, monkeypatch):
        monkeypatch.setattr(hub, "_portfolio_evidence", None)
        monkeypatch.setattr(hub, "_PORTFOLIO_EVIDENCE_IMPORT_ERROR", "ModuleNotFoundError")

        payload, code = _get("/api/portfolio/evidence-draft?project_id=p1")

        assert code == 503
        assert payload["error"] == "portfolio_evidence_unavailable"

    def test_evidence_decision_fails_named(self, monkeypatch):
        monkeypatch.setattr(hub, "_portfolio_evidence", None)
        monkeypatch.setattr(hub, "_PORTFOLIO_EVIDENCE_IMPORT_ERROR", "ModuleNotFoundError")

        payload, code = _post("/api/portfolio/evidence-decision", {
            "project_id": "p1", "candidate_id": "c1", "action": "accept"})

        assert code == 503
        assert payload["error"] == "portfolio_evidence_unavailable"

    def test_evidence_queue_still_validates_input_before_touching_the_dependency(self):
        """project_id_requerido is a caller-contract error (400), not the
        dependency-missing path (503) -- the two must stay distinguishable."""
        payload, code = _get("/api/portfolio/evidence-queue")

        assert code == 400
        assert payload["error"] == "project_id_requerido"


class TestSystemStatusInternalGuard:
    """/api/status guards its flujo import INSIDE the function body (a plain
    try/except, not a module-level None), so it needs a different failure
    injection: poisoning sys.modules for the submodule it imports lazily."""

    def test_status_reports_unknown_instead_of_crashing(self, monkeypatch):
        monkeypatch.setitem(sys.modules, "flujo.knowledge.system_status", None)

        payload, code = _get("/api/status")

        assert code == 200, "still a soft-fail: status carries the signal, not the HTTP code"
        assert payload["status"] == "unknown"
        assert payload["error"] == "ModuleNotFoundError"
        assert payload["next_actions"], "must tell the operator what to do, not just fail quiet"
