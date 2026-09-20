#!/usr/bin/env python3
"""Opt-in Azure embeddings for sanitized MAK evidence packets."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

try:
    from .azure_auth import token_for
except ImportError:
    from azure_auth import token_for


SCHEMA = "mak-azure-embeddings-v1"
DEFAULT_ENDPOINT = "https://makmak-7457-resource.cognitiveservices.azure.com"
DEFAULT_DEPLOYMENT = "text-embedding-3-small"
API_VERSION = "2024-10-21"
MAX_ITEMS = 64
MAX_TEXT_LENGTH = 8_000
MAX_RESPONSE_BYTES = 32_000_000


def _credit_calls_allowed() -> bool:
    return os.environ.get("MAK_AZURE_ALLOW_CREDIT", "").strip().lower() in {
        "1", "true", "yes", "on"
    }


def embed(texts: list[str], *, model: str | None = None) -> dict[str, Any]:
    """Embed a bounded list, preserving order and returning no input text."""
    if not _credit_calls_allowed():
        return {
            "schema": SCHEMA,
            "available": False,
            "error": "azure_credit_guard_blocked",
            "guard": "closed_by_default",
            "enable_with": "MAK_AZURE_ALLOW_CREDIT=1",
        }
    bounded = [str(value or "").strip()[:MAX_TEXT_LENGTH] for value in texts]
    if not bounded or any(not value for value in bounded):
        return {"schema": SCHEMA, "available": False, "error": "input_required"}
    if len(bounded) > MAX_ITEMS:
        return {"schema": SCHEMA, "available": False, "error": "batch_too_large"}

    endpoint = os.environ.get("MAK_AZURE_EMBEDDING_ENDPOINT", DEFAULT_ENDPOINT).rstrip("/")
    deployment = str(
        model or os.environ.get("MAK_AZURE_EMBEDDING_DEPLOYMENT", DEFAULT_DEPLOYMENT)
    ).strip()
    url = "%s/openai/deployments/%s/embeddings?api-version=%s" % (
        endpoint,
        urllib.parse.quote(deployment, safe=""),
        API_VERSION,
    )
    request = urllib.request.Request(
        url,
        data=json.dumps({"input": bounded}, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + token_for("https://cognitiveservices.azure.com"),
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            request_id = response.headers.get("x-request-id", "")
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except urllib.error.HTTPError as exc:
        raise RuntimeError("azure_embedding_http_%s" % exc.code) from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise RuntimeError("azure_embedding_unreachable") from None
    if len(raw) > MAX_RESPONSE_BYTES:
        raise RuntimeError("azure_embedding_response_too_large")
    try:
        payload = json.loads(raw.decode("utf-8", "replace"))
    except (TypeError, ValueError, json.JSONDecodeError):
        raise RuntimeError("azure_embedding_invalid_response") from None

    rows = sorted(payload.get("data") or [], key=lambda row: int(row.get("index", 0)))
    vectors = [row.get("embedding") for row in rows]
    if len(vectors) != len(bounded) or any(not isinstance(row, list) for row in vectors):
        raise RuntimeError("azure_embedding_incomplete_response")
    dimensions = len(vectors[0]) if vectors else 0
    if any(len(row) != dimensions for row in vectors):
        raise RuntimeError("azure_embedding_dimension_mismatch")
    return {
        "schema": SCHEMA,
        "available": True,
        "resource": urllib.parse.urlparse(endpoint).hostname or endpoint,
        "deployment": deployment,
        "model": payload.get("model", deployment),
        "vectors": vectors,
        "dimensions": dimensions,
        "usage": payload.get("usage") if isinstance(payload.get("usage"), dict) else {},
        "request_id": request_id,
    }
