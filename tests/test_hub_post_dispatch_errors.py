#!/usr/bin/env python3
"""tests/test_hub_post_dispatch_errors.py -- the caller-contract error
branches shared by several POST routes in cultura/mak_plataforma/hub.py's
do_POST: a non-numeric Content-Length, a body over the route's own cap, and
a malformed JSON payload. Each POST route repeats this pattern inline
rather than sharing a helper, so each route's copy needs its own witness --
grep across tests/*.py for "content_length_invalido" and "request_too_large"
found only the two large-body proxy/body-limit tests, none of these
per-route parsing branches.

POST /api/research/jobs had no witness of any kind before this file.
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "cultura", "mak_plataforma"))

import hub  # noqa: E402


class FakeHandler:
    def __init__(self, path, body=b"", headers=None):
        self.path = path
        self.rfile = io.BytesIO(body)
        self.headers = headers if headers is not None else {"Content-Length": str(len(body))}
        self.calls = []

    def _json(self, obj, code=200):
        self.calls.append(("json", obj, code))

    @property
    def last(self):
        return self.calls[-1]


def _post(path, body=b"", headers=None):
    handler = FakeHandler(path, body=body, headers=headers)
    hub.H.do_POST(handler)
    _, payload, code = handler.last
    return payload, code


class TestProjectRouteErrorBranches:
    def test_non_numeric_content_length_is_rejected(self):
        payload, code = _post("/api/project/route", body=b"{}",
                              headers={"Content-Length": "not-a-number"})
        assert (payload, code) == ({"ok": False, "error": "content_length_invalido"}, 400)

    def test_body_over_the_cap_is_rejected_without_reading_it(self):
        payload, code = _post("/api/project/route", body=b"{}",
                              headers={"Content-Length": "30001"})
        assert (payload, code) == ({"ok": False, "error": "request_too_large"}, 413)

    def test_malformed_json_is_rejected(self):
        payload, code = _post("/api/project/route", body=b"{not-json")
        assert (payload, code) == ({"ok": False, "error": "json invalido"}, 400)


class TestDiagnosticsPostErrorBranches:
    def test_non_numeric_content_length_is_rejected(self):
        payload, code = _post("/api/diagnostics", body=b"{}",
                              headers={"Content-Length": "not-a-number"})
        assert (payload, code) == ({"ok": False, "error": "content_length_invalido"}, 400)

    def test_body_over_the_cap_is_rejected(self):
        payload, code = _post("/api/diagnostics", body=b"{}",
                              headers={"Content-Length": "20001"})
        assert (payload, code) == ({"ok": False, "error": "request_too_large"}, 413)

    def test_malformed_json_is_rejected(self):
        payload, code = _post("/api/diagnostics", body=b"{not-json")
        assert (payload, code) == ({"ok": False, "error": "json invalido"}, 400)

    def test_non_object_json_is_rejected(self):
        payload, code = _post("/api/diagnostics", body=b"[1, 2, 3]")
        assert (payload, code) == ({"ok": False, "error": "json debe ser objeto"}, 400)


class TestEvidenceDecisionErrorBranches:
    def test_non_numeric_content_length_is_rejected(self):
        payload, code = _post("/api/portfolio/evidence-decision", body=b"{}",
                              headers={"Content-Length": "not-a-number"})
        assert (payload, code) == ({"ok": False, "error": "content_length_invalido"}, 400)

    def test_malformed_json_is_rejected(self):
        payload, code = _post("/api/portfolio/evidence-decision", body=b"{not-json")
        assert (payload, code) == ({"ok": False, "error": "json invalido"}, 400)


class TestResearchJobsRoute:
    def test_non_numeric_content_length_is_rejected(self):
        payload, code = _post("/api/research/jobs", body=b"{}",
                              headers={"Content-Length": "not-a-number"})
        assert (payload, code) == ({"ok": False, "error": "content_length_invalido"}, 400)

    def test_malformed_json_is_rejected(self):
        payload, code = _post("/api/research/jobs", body=b"{not-json")
        assert (payload, code) == ({"ok": False, "error": "json invalido"}, 400)

    def test_non_object_json_is_rejected(self):
        payload, code = _post("/api/research/jobs", body=b'"just a string"')
        assert (payload, code) == ({"ok": False, "error": "json debe ser objeto"}, 400)

    def test_empty_question_is_rejected_as_a_bad_request(self):
        body = json.dumps({"question": "   "}).encode("utf-8")
        payload, code = _post("/api/research/jobs", body=body)
        assert (payload, code) == ({"ok": False, "error": "falta question"}, 400)

    def test_overly_long_question_is_rejected(self):
        body = json.dumps({"question": "x" * 2001}).encode("utf-8")
        payload, code = _post("/api/research/jobs", body=body)
        assert (payload, code) == ({"ok": False, "error": "question demasiado largo"}, 400)
