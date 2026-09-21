from __future__ import annotations

import json
from pathlib import Path
import urllib.error

import pytest

from tools import azure_search_sync as syncer


def _contract(tmp_path: Path) -> dict:
    source = tmp_path / "safe.md"
    source.write_text("# Evidencia\n\nSólo metadata técnica.\n", encoding="utf-8")
    return {
        "schema": "mak-azure-search-sync-v1",
        "service": "makmak-search",
        "endpoint": "https://example.search.windows.net",
        "api_version": "2024-07-01",
        "allowed_indexes": ["mak-inbox-v1", "mak-rd-v1", "mak-tools-v1"],
        "write_mode": "mergeOrUpload",
        "delete_remote_documents": False,
        "max_source_bytes": 1024,
        "documents": [{
            "index": "mak-tools-v1", "repository": "fixture",
            "relative_path": "safe.md", "domain": "test",
            "evidence_state": "reviewed", "fields": {
                "ruta": "safe.md", "area": "test", "proposito": "fixture",
                "departamento": "test",
            },
        }],
    }


def test_documents_have_stable_id_and_content_hash(tmp_path, monkeypatch):
    contract = _contract(tmp_path)
    monkeypatch.setitem(syncer.REPOSITORIES, "fixture", tmp_path)
    first = syncer.build_documents(contract)
    second = syncer.build_documents(contract)
    assert first[0]["fields"]["id"] == second[0]["fields"]["id"]
    assert first[0]["fields"]["content_sha256"] == second[0]["fields"]["content_sha256"]
    assert first[0]["fields"]["contenido"].startswith("# Evidencia")


def test_source_cannot_escape_or_target_a_fourth_index(tmp_path, monkeypatch):
    contract = _contract(tmp_path)
    monkeypatch.setitem(syncer.REPOSITORIES, "fixture", tmp_path)
    contract["documents"][0]["relative_path"] = "../secret.env"
    with pytest.raises(syncer.SyncError, match="unsafe_source_path"):
        syncer.build_documents(contract)
    contract = _contract(tmp_path)
    contract["documents"][0]["index"] = "fourth-index"
    with pytest.raises(syncer.SyncError, match="not_allowlisted"):
        syncer.build_documents(contract)


def test_sync_is_incremental_and_never_deletes(tmp_path, monkeypatch):
    contract = _contract(tmp_path)
    monkeypatch.setitem(syncer.REPOSITORIES, "fixture", tmp_path)
    documents = syncer.build_documents(contract)
    digest = documents[0]["fields"]["content_sha256"]
    monkeypatch.setattr(syncer, "_remote_hashes", lambda _c, index: (
        {documents[0]["fields"]["id"]: digest} if index == "mak-tools-v1" else {}))
    calls = []
    monkeypatch.setattr(syncer, "_request", lambda *args, **kwargs: calls.append((args, kwargs)) or {})
    receipt = syncer.sync(contract, documents, apply=True)
    assert receipt["delete_count"] == 0
    assert receipt["indexes"]["mak-tools-v1"]["unchanged"] == 1
    assert receipt["indexes"]["mak-tools-v1"]["uploaded"] == 0
    assert calls == []


def test_contract_requires_exact_existing_index_set(tmp_path):
    contract = _contract(tmp_path)
    contract["allowed_indexes"].append("fourth-index")
    path = tmp_path / "contract.json"
    path.write_text(json.dumps(contract), encoding="utf-8")
    with pytest.raises(syncer.SyncError, match="three_existing"):
        syncer._load_contract(path)


def test_disabled_service_error_is_named_without_leaking_body(monkeypatch):
    error = urllib.error.HTTPError(
        "https://example", 400, "Bad Request", {},
        __import__("io").BytesIO(b'{"message":"The search service X is disabled. secret"}'))
    monkeypatch.setattr(syncer, "_token", lambda: "token")
    monkeypatch.setattr(syncer.urllib.request, "urlopen", lambda *_a, **_kw: (_ for _ in ()).throw(error))
    with pytest.raises(syncer.SyncError) as caught:
        syncer._request("https://example", "2024-07-01", "GET", "/indexes")
    assert str(caught.value) == "azure_search_service_disabled"
    assert "secret" not in str(caught.value)
