#!/usr/bin/env python3
"""Shared, read-only adapter for MAK's Azure AI Search corpus.

The MAK Hub is the canonical consumer of this adapter.  Command-line tools
may call the same functions for diagnostics, but they must not duplicate the
authentication, filter, or response-shaping logic.

Authentication deliberately reuses the existing MAK ``az login`` session when
no explicit ``SEARCH_KEY`` is configured.  The REST fallback keeps the Hub
usable in its service virtualenv, where the Azure SDK is not installed, and
does not install dependencies or create a second login flow.

This adapter only reads ``mak-tools-v1``.  It never writes Search indexes and
never changes MAK's local databases or ledgers.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

try:
    from .azure_auth import token_for
except ImportError:  # direct import from the Hub's module directory
    from azure_auth import token_for


SCHEMA = "mak-azure-search-tools-v1"
DEFAULT_ENDPOINT = "https://makmak-search.search.windows.net"
DEFAULT_INDEX = "mak-tools-v1"
API_VERSION = "2024-07-01"
MAX_QUERY_LENGTH = 512
MAX_FILTER_LENGTH = 160
MAX_TOP = 50
MAX_RESPONSE_BYTES = 1_000_000


def _endpoint() -> str:
    return os.environ.get("SEARCH_ENDPOINT", DEFAULT_ENDPOINT).rstrip("/")


def _credential_mode() -> str:
    return "search-key" if os.environ.get("SEARCH_KEY") else "azure-cli"


def _bounded_text(value: Any, limit: int) -> str:
    return str(value or "").strip()[:limit]


def _odata_literal(value: Any) -> str:
    """Return one bounded OData string literal without accepting syntax."""
    return "'" + _bounded_text(value, MAX_FILTER_LENGTH).replace("'", "''") + "'"


def build_filter(area: str | None = None,
                 departamento: str | None = None) -> str | None:
    clauses = []
    if area:
        clauses.append("area eq " + _odata_literal(area))
    if departamento:
        clauses.append("departamento eq " + _odata_literal(departamento))
    return " and ".join(clauses) if clauses else None


def _search_request(query: str, filter_value: str | None, top: int) -> list[dict[str, Any]]:
    endpoint = _endpoint()
    index = os.environ.get("SEARCH_INDEX", DEFAULT_INDEX)
    url = "%s/indexes/%s/docs/search?api-version=%s" % (
        endpoint,
        urllib.parse.quote(index, safe=""),
        API_VERSION,
    )
    body: dict[str, Any] = {
        "search": query,
        "top": top,
        "select": "id,ruta,area,proposito,departamento",
    }
    if filter_value:
        body["filter"] = filter_value
    headers = {"Content-Type": "application/json"}
    key = os.environ.get("SEARCH_KEY")
    if key:
        headers["api-key"] = key
    else:
        headers["Authorization"] = "Bearer " + token_for("https://search.azure.com")
    request = urllib.request.Request(
        url,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except urllib.error.HTTPError as exc:
        # Do not return the service body: Azure can echo request details and
        # the Hub must not expose raw provider errors to every LAN client.
        raise RuntimeError("azure_search_http_%s" % exc.code) from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise RuntimeError("azure_search_unreachable") from None
    if len(raw) > MAX_RESPONSE_BYTES:
        raise RuntimeError("azure_search_response_too_large")
    try:
        payload = json.loads(raw.decode("utf-8", "replace"))
    except (TypeError, ValueError, json.JSONDecodeError):
        raise RuntimeError("azure_search_invalid_response") from None
    rows = payload.get("value", []) if isinstance(payload, dict) else []
    if not isinstance(rows, list):
        raise RuntimeError("azure_search_invalid_results")
    return [row for row in rows if isinstance(row, dict)]


def search_tools(query: str, *, area: str | None = None,
                 departamento: str | None = None, top: int = 10) -> dict[str, Any]:
    """Search the shared MAK tools corpus and return a stable Hub payload."""
    clean_query = _bounded_text(query, MAX_QUERY_LENGTH)
    if not clean_query:
        return {
            "schema": SCHEMA,
            "available": False,
            "read_only": True,
            "error": "consulta_requerida",
        }
    try:
        clean_top = max(1, min(int(top), MAX_TOP))
    except (TypeError, ValueError):
        clean_top = 10
    clean_area = _bounded_text(area, MAX_FILTER_LENGTH) or None
    clean_departamento = _bounded_text(departamento, MAX_FILTER_LENGTH) or None
    filter_value = build_filter(clean_area, clean_departamento)
    try:
        rows = _search_request(clean_query, filter_value, clean_top)
    except RuntimeError as exc:
        return {
            "schema": SCHEMA,
            "available": False,
            "read_only": True,
            "provider": "azure-ai-search",
            "index": os.environ.get("SEARCH_INDEX", DEFAULT_INDEX),
            "credential": _credential_mode(),
            "error": str(exc),
            "query": clean_query,
        }
    results = []
    for row in rows:
        results.append({
            key: row.get(key)
            for key in ("id", "ruta", "area", "proposito", "departamento")
            if row.get(key) is not None
        } | {
            "score": round(float(row.get("@search.score", 0) or 0), 4),
        })
    return {
        "schema": SCHEMA,
        "available": True,
        "read_only": True,
        "provider": "azure-ai-search",
        "endpoint": _endpoint(),
        "index": os.environ.get("SEARCH_INDEX", DEFAULT_INDEX),
        "credential": _credential_mode(),
        "query": clean_query,
        "filters": {"area": clean_area, "departamento": clean_departamento},
        "count": len(results),
        "results": results,
    }
