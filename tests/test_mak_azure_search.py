from __future__ import annotations

import io
import os
import sys
import urllib.error

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cultura.mak_plataforma import azure_search


def test_filter_is_bounded_and_odata_escaped():
    value = "RD' OR 1 eq 1"
    assert azure_search.build_filter(area=value) == "area eq 'RD'' OR 1 eq 1'"


def test_search_tools_returns_stable_read_only_payload(monkeypatch):
    monkeypatch.setattr(
        azure_search,
        "_search_request",
        lambda query, filter_value, top: [{
            "id": "one",
            "ruta": "cultura/mak_codex/revisar.py",
            "area": "codex",
            "proposito": "revision",
            "departamento": "codex",
            "source_ref": "mak:cultura/mak_codex/revisar.py",
            "content_sha256": "a" * 64,
            "domain": "code",
            "evidence_state": "reviewed_technical",
            "@search.score": 3.14159,
        }],
    )
    payload = azure_search.search_tools(
        "revision", area="codex", departamento="codex", top="2")
    assert payload["available"] is True
    assert payload["read_only"] is True
    assert payload["count"] == 1
    assert payload["results"][0]["score"] == 3.1416
    assert payload["results"][0]["content_sha256"] == "a" * 64
    assert payload["filters"] == {"area": "codex", "departamento": "codex"}


def test_empty_query_is_a_named_caller_error():
    payload = azure_search.search_tools(" ")
    assert payload == {
        "schema": "mak-azure-search-tools-v1",
        "available": False,
        "read_only": True,
        "error": "consulta_requerida",
    }


def test_disabled_search_service_has_a_named_content_free_error(monkeypatch):
    error = urllib.error.HTTPError(
        "https://example", 400, "Bad Request", {},
        io.BytesIO(b'{"message":"The search service X is disabled. secret"}'))
    monkeypatch.setattr(azure_search, "token_for", lambda _resource: "token")
    monkeypatch.setattr(
        azure_search.urllib.request, "urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(error))
    payload = azure_search.search_tools("test")
    assert payload["error"] == "azure_search_service_disabled"
    assert "secret" not in str(payload)


def test_hub_route_delegates_to_shared_adapter(monkeypatch):
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "cultura", "mak_plataforma"))
    import hub

    class FakeHandler:
        path = "/api/azure/search/tools?q=revision&departamento=codex&top=3"

        def __init__(self):
            self.calls = []

        def _json(self, payload, code=200):
            self.calls.append((payload, code))

    seen = {}

    def fake_search(text, **kwargs):
        seen.update(text=text, **kwargs)
        return {
            "schema": "mak-azure-search-tools-v1",
            "available": True,
            "read_only": True,
            "results": [],
        }

    monkeypatch.setattr(hub, "_azure_search_tools", fake_search)
    handler = FakeHandler()
    hub.H.do_GET(handler)
    assert seen == {"text": "revision", "area": None,
                    "departamento": "codex", "top": "3"}
    assert handler.calls[-1][1] == 200
