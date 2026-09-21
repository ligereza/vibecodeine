#!/usr/bin/env python3
"""Incrementally synchronize an explicit, sanitized corpus to Azure AI Search.

The contract allowlists exactly the three existing indexes.  Documents use a
stable key derived from ``index + source_ref`` and a remote ``content_sha256``
field, so unchanged content is never resent.  The tool never creates indexes,
never deletes remote documents and never scans directories implicitly.

Dry-run is the default.  ``--apply-schema`` only adds the common provenance
fields to existing indexes; ``--apply`` performs ``mergeOrUpload`` for changed
documents after every safety check passes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = ROOT / "contracts" / "azure_search_sync.v1.json"
REPOSITORIES = {
    "mak": ROOT,
    "pastillas": ROOT / "pastillas",
    "flujo": ROOT / "flujo",
    "xio": ROOT / "XIO",
    "iris": ROOT / "IRIS",
}
COMMON_FIELDS = (
    {"name": "source_ref", "type": "Edm.String", "searchable": False,
     "filterable": True, "retrievable": True, "sortable": False,
     "facetable": False, "key": False},
    {"name": "content_sha256", "type": "Edm.String", "searchable": False,
     "filterable": True, "retrievable": True, "sortable": False,
     "facetable": False, "key": False},
    {"name": "source_modified_at", "type": "Edm.String", "searchable": False,
     "filterable": True, "retrievable": True, "sortable": False,
     "facetable": False, "key": False},
    {"name": "indexed_at", "type": "Edm.String", "searchable": False,
     "filterable": True, "retrievable": True, "sortable": False,
     "facetable": False, "key": False},
    {"name": "domain", "type": "Edm.String", "searchable": False,
     "filterable": True, "retrievable": True, "sortable": False,
     "facetable": False, "key": False},
    {"name": "evidence_state", "type": "Edm.String", "searchable": False,
     "filterable": True, "retrievable": True, "sortable": False,
     "facetable": False, "key": False},
    {"name": "contenido", "type": "Edm.String", "searchable": True,
     "filterable": False, "retrievable": True, "sortable": False,
     "facetable": False, "key": False, "analyzer": "es.microsoft"},
)
SAFE_SUFFIXES = {".md", ".py", ".json"}
FORBIDDEN_PARTS = {".env", "data", "secrets", "credentials"}


class SyncError(RuntimeError):
    """Named, content-free failure suitable for Hub/CLI reporting."""


def _token() -> str:
    import sys
    module_root = ROOT / "cultura" / "mak_plataforma"
    if str(module_root) not in sys.path:
        sys.path.insert(0, str(module_root))
    from azure_auth import token_for
    return token_for("https://search.azure.com")


def _request(endpoint: str, api_version: str, method: str, path: str,
             payload: dict[str, Any] | None = None) -> dict[str, Any]:
    url = endpoint.rstrip("/") + path
    separator = "&" if "?" in url else "?"
    url += separator + "api-version=" + urllib.parse.quote(api_version)
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url, data=data, method=method,
        headers={"Authorization": "Bearer " + _token(), "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read(2_000_001)
    except urllib.error.HTTPError as exc:
        provider_body = exc.read(4096).decode("utf-8", "replace").lower()
        if exc.code == 400 and "search service" in provider_body and "disabled" in provider_body:
            raise SyncError("azure_search_service_disabled") from None
        raise SyncError(f"azure_search_http_{exc.code}") from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise SyncError("azure_search_unreachable") from None
    if len(raw) > 2_000_000:
        raise SyncError("azure_search_response_too_large")
    if not raw:
        return {}
    try:
        result = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise SyncError("azure_search_invalid_json") from None
    return result if isinstance(result, dict) else {}


def _load_contract(path: Path) -> dict[str, Any]:
    contract = json.loads(path.read_text(encoding="utf-8"))
    if contract.get("schema") != "mak-azure-search-sync-v1":
        raise SyncError("invalid_contract_schema")
    allowed = contract.get("allowed_indexes")
    if allowed != ["mak-inbox-v1", "mak-rd-v1", "mak-tools-v1"]:
        raise SyncError("allowed_indexes_must_be_the_three_existing_indexes")
    if contract.get("delete_remote_documents") is not False:
        raise SyncError("remote_deletion_must_be_disabled")
    if contract.get("write_mode") != "mergeOrUpload":
        raise SyncError("unsafe_write_mode")
    return contract


def _source_path(item: dict[str, Any]) -> tuple[Path, str]:
    repository = str(item.get("repository", ""))
    if repository not in REPOSITORIES:
        raise SyncError("repository_not_allowlisted")
    relative = Path(str(item.get("relative_path", "")))
    if relative.is_absolute() or ".." in relative.parts:
        raise SyncError("unsafe_source_path")
    root = REPOSITORIES[repository].resolve()
    path = (root / relative).resolve()
    if path != root and root not in path.parents:
        raise SyncError("source_escapes_repository")
    lowered = {part.lower() for part in relative.parts}
    if lowered & FORBIDDEN_PARTS or path.suffix.lower() not in SAFE_SUFFIXES:
        raise SyncError("source_type_not_allowed")
    return path, f"{repository}:{relative.as_posix()}"


def _document_id(index: str, source_ref: str) -> str:
    digest = hashlib.sha256((index + "\0" + source_ref).encode("utf-8")).hexdigest()
    return "sync-v1-" + digest[:40]


def build_documents(contract: dict[str, Any]) -> list[dict[str, Any]]:
    allowed = set(contract["allowed_indexes"])
    maximum = int(contract["max_source_bytes"])
    documents = []
    seen: set[tuple[str, str]] = set()
    for item in contract.get("documents", []):
        index = str(item.get("index", ""))
        if index not in allowed:
            raise SyncError("target_index_not_allowlisted")
        path, source_ref = _source_path(item)
        if not path.is_file():
            raise SyncError(f"source_missing:{source_ref}")
        raw = path.read_bytes()
        if len(raw) > maximum:
            raise SyncError(f"source_too_large:{source_ref}")
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError:
            raise SyncError(f"source_not_utf8:{source_ref}") from None
        key = (index, source_ref)
        if key in seen:
            raise SyncError(f"duplicate_source:{source_ref}")
        seen.add(key)
        stat = path.stat()
        fields = dict(item.get("fields") or {})
        fields.update({
            "id": _document_id(index, source_ref),
            "source_ref": source_ref,
            "content_sha256": hashlib.sha256(raw).hexdigest(),
            "source_modified_at": datetime.fromtimestamp(
                stat.st_mtime, timezone.utc).isoformat(),
            "domain": str(item.get("domain", "technical"))[:120],
            "evidence_state": str(item.get("evidence_state", "observed"))[:120],
            "contenido": content,
        })
        documents.append({"index": index, "source_ref": source_ref, "fields": fields})
    return documents


def _index_definition(contract: dict[str, Any], index: str) -> dict[str, Any]:
    return _request(contract["endpoint"], contract["api_version"], "GET",
                    "/indexes/" + urllib.parse.quote(index, safe=""))


def ensure_schema(contract: dict[str, Any], *, apply: bool) -> dict[str, Any]:
    result: dict[str, Any] = {"changed": [], "unchanged": [], "dry_run": not apply}
    for index in contract["allowed_indexes"]:
        definition = _index_definition(contract, index)
        if definition.get("name") != index or not isinstance(definition.get("fields"), list):
            raise SyncError(f"existing_index_not_found:{index}")
        names = {field.get("name") for field in definition["fields"]}
        missing = [dict(field) for field in COMMON_FIELDS if field["name"] not in names]
        if not missing:
            result["unchanged"].append(index)
            continue
        if not apply:
            result["changed"].append({"index": index, "would_add": [f["name"] for f in missing]})
            continue
        clean = {key: value for key, value in definition.items() if not key.startswith("@odata.")}
        clean["fields"] = list(clean["fields"]) + missing
        _request(contract["endpoint"], contract["api_version"], "PUT",
                 "/indexes/" + urllib.parse.quote(index, safe=""), clean)
        result["changed"].append({"index": index, "added": [f["name"] for f in missing]})
    return result


def _remote_hashes(contract: dict[str, Any], index: str) -> dict[str, str]:
    payload = {"search": "*", "top": 1000, "select": "id,content_sha256"}
    response = _request(
        contract["endpoint"], contract["api_version"], "POST",
        "/indexes/" + urllib.parse.quote(index, safe="") + "/docs/search", payload)
    rows = response.get("value", [])
    if not isinstance(rows, list):
        raise SyncError(f"invalid_remote_documents:{index}")
    return {
        str(row.get("id")): str(row.get("content_sha256") or "")
        for row in rows if isinstance(row, dict) and row.get("id")
    }


def sync(contract: dict[str, Any], documents: list[dict[str, Any]], *, apply: bool) -> dict[str, Any]:
    grouped = {name: [] for name in contract["allowed_indexes"]}
    for document in documents:
        grouped[document["index"]].append(document)
    receipt: dict[str, Any] = {
        "schema": "mak-azure-search-sync-receipt-v1",
        "service": contract["service"],
        "dry_run": not apply,
        "delete_count": 0,
        "indexes": {},
    }
    for index, rows in grouped.items():
        remote = _remote_hashes(contract, index)
        changed = [row for row in rows
                   if remote.get(row["fields"]["id"]) != row["fields"]["content_sha256"]]
        unchanged = [row for row in rows if row not in changed]
        if apply and changed:
            now = datetime.now(timezone.utc).isoformat()
            values = []
            for row in changed:
                value = dict(row["fields"])
                value["indexed_at"] = now
                value["@search.action"] = contract["write_mode"]
                values.append(value)
            response = _request(
                contract["endpoint"], contract["api_version"], "POST",
                "/indexes/" + urllib.parse.quote(index, safe="") + "/docs/index",
                {"value": values})
            statuses = response.get("value", [])
            if len(statuses) != len(values) or not all(row.get("status") for row in statuses):
                raise SyncError(f"index_write_not_confirmed:{index}")
        receipt["indexes"][index] = {
            "declared": len(rows), "changed": len(changed),
            "unchanged": len(unchanged), "uploaded": len(changed) if apply else 0,
            "source_refs": sorted(row["source_ref"] for row in rows),
        }
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--apply-schema", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        contract = _load_contract(args.contract)
        documents = build_documents(contract)
        schema = ensure_schema(contract, apply=args.apply_schema)
        if schema["changed"] and not args.apply_schema:
            raise SyncError("remote_schema_missing_fields_run_with_apply_schema")
        receipt = sync(contract, documents, apply=args.apply)
        receipt["schema_update"] = schema
        receipt["document_count"] = len(documents)
        receipt["contains_raw_rd_images"] = False
        receipt["contains_rd_database"] = False
        print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, json.JSONDecodeError, SyncError) as exc:
        print(json.dumps({"schema": "mak-azure-search-sync-receipt-v1",
                          "ok": False, "error": str(exc)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
