#!/usr/bin/env python3
"""Small AAD-authenticated client for the Azure model deployed for MAK.

This is an opt-in provider.  It uses the existing MAK ``az login`` session
and the live deployment in ``makmak-5202-resource``; it does not fall back to
ISSVKK credentials and it never becomes the automatic provider for existing
Research jobs without an explicit provider selection.
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


SCHEMA = "mak-azure-foundry-chat-v1"
DEFAULT_ENDPOINT = "https://makmak-5202-resource.cognitiveservices.azure.com"
DEFAULT_DEPLOYMENT = "gpt-oss-120b"
API_VERSION = "2024-10-21"
MAX_PROMPT_LENGTH = 24_000
MAX_TOKENS = 4_000
MAX_RESPONSE_BYTES = 2_000_000


def _bounded(value: Any, limit: int) -> str:
    return str(value or "").strip()[:limit]


def _endpoint() -> str:
    return (os.environ.get("MAK_AZURE_AI_ENDPOINT") or
            os.environ.get("AZURE_MAK_ENDPOINT") or
            DEFAULT_ENDPOINT).rstrip("/")


def _deployment(value: str | None = None) -> str:
    return (_bounded(value, 120) or
            os.environ.get("MAK_AZURE_AI_DEPLOYMENT") or
            os.environ.get("AZURE_MAK_DEPLOYMENT") or
            DEFAULT_DEPLOYMENT)


def _credit_calls_allowed() -> bool:
    return os.environ.get("MAK_AZURE_ALLOW_CREDIT", "").strip().lower() in {
        "1", "true", "yes", "on"
    }


def chat(prompt: str, *, system: str | None = None,
         model: str | None = None, max_tokens: int = 512,
         temperature: float | None = None) -> dict[str, Any]:
    """Call the selected MAK Azure deployment and return a safe envelope."""
    user_text = _bounded(prompt, MAX_PROMPT_LENGTH)
    if not user_text:
        return {"schema": SCHEMA, "available": False,
                "error": "prompt_requerido"}
    if not _credit_calls_allowed():
        return {
            "schema": SCHEMA,
            "available": False,
            "error": "azure_credit_guard_blocked",
            "guard": "closed_by_default",
            "enable_with": "MAK_AZURE_ALLOW_CREDIT=1",
        }
    try:
        limit = max(1, min(int(max_tokens), MAX_TOKENS))
    except (TypeError, ValueError):
        limit = 512
    deployment = _deployment(model)
    messages = []
    if system:
        messages.append({"role": "system", "content": _bounded(system, 8_000)})
    messages.append({"role": "user", "content": user_text})
    body: dict[str, Any] = {"messages": messages, "max_tokens": limit}
    if temperature is not None:
        body["temperature"] = max(0.0, min(float(temperature), 2.0))
    endpoint = _endpoint()
    url = "%s/openai/deployments/%s/chat/completions?api-version=%s" % (
        endpoint, urllib.parse.quote(deployment, safe=""), API_VERSION)
    request = urllib.request.Request(
        url,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": "Bearer " + token_for(
            "https://cognitiveservices.azure.com"),
                 "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            request_id = response.headers.get("x-request-id", "")
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except urllib.error.HTTPError as exc:
        raise RuntimeError("azure_foundry_http_%s" % exc.code) from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise RuntimeError("azure_foundry_unreachable") from None
    if len(raw) > MAX_RESPONSE_BYTES:
        raise RuntimeError("azure_foundry_response_too_large")
    try:
        payload = json.loads(raw.decode("utf-8", "replace"))
    except (TypeError, ValueError, json.JSONDecodeError):
        raise RuntimeError("azure_foundry_invalid_response") from None
    choices = payload.get("choices") or []
    message = (choices[0].get("message") if choices else {}) or {}
    content = message.get("content") or ""
    usage = payload.get("usage") if isinstance(payload, dict) else None
    return {
        "schema": SCHEMA,
        "available": True,
        "provider": "azure-foundry",
        "resource": urllib.parse.urlparse(endpoint).hostname or endpoint,
        "deployment": deployment,
        "model": payload.get("model", deployment),
        "content": str(content),
        "usage": usage if isinstance(usage, dict) else {},
        "request_id": request_id,
    }


def call_text(prompt: str, *, system: str | None = None,
              model: str | None = None, max_tokens: int = 512,
              temperature: float | None = None) -> str:
    """Provider-compatible text call; errors remain attributable to Azure."""
    result = chat(prompt, system=system, model=model, max_tokens=max_tokens,
                  temperature=temperature)
    if not result.get("available"):
        raise RuntimeError(str(result.get("error", "azure_foundry_unavailable")))
    return str(result.get("content", ""))
