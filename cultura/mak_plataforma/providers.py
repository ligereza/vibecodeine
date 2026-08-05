#!/usr/bin/env python3
"""External provider calls for MAK batch briefs.

The contract lives in ``tandas.py``. This module only transports prompts to
temporary external credits and returns text, so the system can retire a provider
without rewriting the ledger or local review gate.
"""
from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request


ENV_ALIASES = {
    "WATSONX_API_KEY": ("IBM_CLOUD_APIKEY",),
    "WATSONX_PROJECT_ID": ("IBM_PROJECT_ID",),
    "WATSONX_URL": ("IBM_CLOUD_URL",),
    "AWS_DEFAULT_REGION": ("AWS_REGION",),
}


def load_env(path=None):
    """Load KEY=value pairs and normalize provider aliases without exposing them."""
    candidates = []
    if path:
        candidates.append(path)
    candidates.extend([
        os.environ.get("RESEARCH_ENV", ""),
        os.path.join(os.getcwd(), ".env"),
        os.path.expanduser("~/n8n-local/research.env"),
        os.path.expanduser("~/research.env"),
    ])
    for candidate in candidates:
        if not candidate:
            continue
        expanded = os.path.expanduser(candidate)
        if not os.path.isfile(expanded):
            continue
        with open(expanded, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    for canonical, aliases in ENV_ALIASES.items():
        if os.environ.get(canonical):
            continue
        for alias in aliases:
            if os.environ.get(alias):
                os.environ[canonical] = os.environ[alias]
                break


_WX_TOKEN = {"value": None, "expires": 0.0}


def _watsonx_token():
    if _WX_TOKEN["value"] and time.time() < _WX_TOKEN["expires"] - 60:
        return _WX_TOKEN["value"]
    api_key = os.environ.get("WATSONX_API_KEY", "")
    if not api_key:
        raise RuntimeError("missing WATSONX_API_KEY")
    body = urllib.parse.urlencode({
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": api_key,
    }).encode("utf-8")
    request = urllib.request.Request(
        "https://iam.cloud.ibm.com/identity/token",
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "User-Agent": "flujo-mak-batches/1.0",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8", "replace"))
    _WX_TOKEN["value"] = payload["access_token"]
    _WX_TOKEN["expires"] = time.time() + float(payload.get("expires_in", 3600))
    return _WX_TOKEN["value"]


def watsonx_chat(prompt, model=None, max_tokens=2500, temperature=0.1):
    load_env()
    project_id = os.environ.get("WATSONX_PROJECT_ID", "")
    if not project_id:
        raise RuntimeError("missing WATSONX_PROJECT_ID")
    base = os.environ.get("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
    request = urllib.request.Request(
        base.rstrip("/") + "/ml/v1/text/chat?version=2024-10-08",
        data=json.dumps({
            "model_id": model or os.environ.get(
                "WATSONX_BATCH_MODEL",
                os.environ.get("WATSONX_MODEL", "meta-llama/llama-3-3-70b-instruct"),
            ),
            "project_id": project_id,
            "messages": [
                {"role": "system", "content": "Return only valid JSON. No prose."},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + _watsonx_token(),
            "Content-Type": "application/json",
            "User-Agent": "flujo-mak-batches/1.0",
        },
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        payload = json.loads(response.read().decode("utf-8", "replace"))
    return (payload["choices"][0]["message"]["content"] or "").strip()


def aws_bedrock_chat(prompt, model=None, max_tokens=2500, temperature=0.1):
    load_env()
    try:
        import boto3
    except Exception as exc:  # noqa: BLE001 - optional provider dependency
        raise RuntimeError("boto3_unavailable") from exc
    region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
    client = boto3.client("bedrock-runtime", region_name=region)
    model_id = model or os.environ.get("AWS_BEDROCK_BATCH_MODEL", "amazon.nova-pro-v1:0")
    body = {
        "messages": [{
            "role": "user",
            "content": [{"text": "Return only valid JSON. No prose.\n\n" + prompt}],
        }],
        "inferenceConfig": {
            "maxTokens": max_tokens,
            "temperature": temperature,
        },
    }
    response = client.invoke_model(
        modelId=model_id,
        body=json.dumps(body).encode("utf-8"),
        contentType="application/json",
        accept="application/json",
    )
    payload = json.loads(response["body"].read().decode("utf-8", "replace"))
    output = payload.get("output", {}).get("message", {}).get("content", [])
    return "".join(part.get("text", "") for part in output).strip()


def call(provider, prompt, model=None, max_tokens=2500, temperature=0.1):
    provider = str(provider or "").lower()
    if provider == "watsonx":
        return watsonx_chat(prompt, model=model, max_tokens=max_tokens,
                            temperature=temperature)
    if provider == "aws":
        return aws_bedrock_chat(prompt, model=model, max_tokens=max_tokens,
                                temperature=temperature)
    raise ValueError("unknown_provider:%s" % provider)
