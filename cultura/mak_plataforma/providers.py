#!/usr/bin/env python3
"""External provider calls for MAK batch briefs.

The contract lives in ``tandas.py``. This module only transports prompts to
temporary external credits and returns text, so the system can retire a provider
without rewriting the ledger or local review gate.
"""
from __future__ import annotations

import json
import hashlib
import os
import time
import urllib.request
import sys


def _reserve_bounded_external(provider):
    """Reserve paid-provider capacity only when the conductor is enabled."""
    try:
        from cultura.mak_conductor.runtime import (external_budget_limit,
                                                    reserve_external_call)
    except ImportError:
        sys.path.insert(0, os.environ.get("MAK_CONDUCTOR_PATH",
                                         "/home/mak/flujo/cultura"))
        try:
            from mak_conductor.runtime import (external_budget_limit,
                                               reserve_external_call)
        except ImportError:
            return True
    return reserve_external_call(
        provider, limit_count=external_budget_limit(provider))


def _shared_local_gpu(job_id, estimated_vram_mb):
    try:
        from cultura.mak_conductor.runtime import shared_gpu_lease
    except ImportError:
        sys.path.insert(0, os.environ.get("MAK_CONDUCTOR_PATH",
                                         "/home/mak/flujo/cultura"))
        try:
            from mak_conductor.runtime import shared_gpu_lease
        except ImportError:
            from contextlib import nullcontext
            return nullcontext()
    return shared_gpu_lease(job_id=job_id, estimated_vram_mb=estimated_vram_mb)


ENV_ALIASES = {}

PROVIDER_CAPABILITIES = {
    "cerebras": {"text_review", "hypothesis"},
    "groq": {"text_review", "hypothesis"},
    "gemini": {"text_review", "hypothesis"},
    "ollama": {"local_judge", "text_review", "hypothesis"},
}
PROVIDER_TIERS = {
    "cerebras": "free_cloud", "groq": "free_cloud", "gemini": "free_cloud",
    "ollama": "local_floor",
}
PROVIDER_ORDER = ("groq", "gemini", "cerebras", "ollama")
TASK_CAPABILITIES = {
    "visual": "vision", "vision": "vision", "research": "hypothesis",
    "curation": "hypothesis", "review": "text_review", "judge": "local_judge",
}


def _provider_configured(provider, environment):
    if provider == "groq":
        return bool(environment.get("GROQ_API_KEY"))
    if provider == "cerebras":
        return bool(environment.get("CEREBRAS_API_KEY"))
    if provider == "gemini":
        return bool(environment.get("GEMINI_API_KEY"))
    if provider == "ollama":
        return bool(environment.get("OLLAMA_BASE_URL") or
                    environment.get("OLLAMA_HOST"))
    return False


def provider_registry(environment=None):
    """Return capabilities and health without exposing credentials."""
    if environment is None:
        load_env()
    # An explicit empty mapping means "no providers configured".  Using
    # ``environment or os.environ`` leaks the host environment into callers
    # that intentionally pass an isolated configuration.
    environment = os.environ if environment is None else environment
    providers = []
    for provider in PROVIDER_ORDER:
        configured = _provider_configured(provider, environment)
        providers.append({
            "id": provider,
            "tier": PROVIDER_TIERS[provider],
            "capabilities": sorted(PROVIDER_CAPABILITIES[provider]),
            "configured": configured,
            "status": "configured" if configured else "unconfigured",
            "runtime": "unverified",
        })
    return {"schema": "faro-provider-registry-v1", "providers": providers}


def provider_plan(available=None, allow_premium=True, capability=None):
    """Choose a durable order while retaining temporary-credit priority."""
    requested = {str(value).lower() for value in (available or [])}
    if requested:
        configured = set(requested)
    else:
        registry = provider_registry()
        configured = {row["id"] for row in registry["providers"]
                      if row["configured"]}
    if requested:
        configured |= {value for value in requested if value in PROVIDER_CAPABILITIES}
    requested_capability = str(capability or "").lower()
    required = (requested_capability if requested_capability in {
        value for values in PROVIDER_CAPABILITIES.values() for value in values
    } else TASK_CAPABILITIES.get(requested_capability))
    result = []
    for provider in PROVIDER_ORDER:
        if provider not in configured:
            continue
        if required and required not in PROVIDER_CAPABILITIES[provider]:
            continue
        result.append(provider)
    return result


def route_task(task_kind, available=None, allow_premium=True):
    """Route a typed task and expose its fallback chain to the work envelope."""
    capability = TASK_CAPABILITIES.get(str(task_kind or "").lower(), "text_review")
    plan = provider_plan(available, allow_premium=allow_premium,
                         capability=capability)
    requires_external = any(PROVIDER_TIERS.get(provider) != "local_floor"
                            for provider in plan)
    fallback_chain = plan[1:]
    if not fallback_chain:
        fallback_chain = ["local_deterministic"]
    return {"schema": "faro-provider-route-v1", "task_kind": str(task_kind),
            "capability": capability, "provider": plan[0] if plan else "local_deterministic",
            "fallback_chain": fallback_chain,
            "requires_external": requires_external}


def load_env(path=None):
    """Load KEY=value pairs and normalize provider aliases without exposing them."""
    explicit_path = (os.path.abspath(os.path.expanduser(path))
                     if path else "")
    if path:
        # An explicit environment file is an isolated configuration boundary.
        # Do not merge host credentials from fallback locations into a test,
        # batch, or service that named its source deliberately.
        candidates = [path]
    else:
        candidates = [
            os.environ.get("RESEARCH_ENV", ""),
            os.path.join(os.getcwd(), ".env"),
            "/home/mak/flujo/.env",
            os.path.expanduser("~/research/research.env"),
            os.path.expanduser("~/research.env"),
        ]
    for candidate in candidates:
        if not candidate:
            continue
        expanded = os.path.expanduser(candidate)
        if not os.path.isfile(expanded):
            continue
        is_explicit = bool(explicit_path and
                           os.path.abspath(expanded) == explicit_path)
        with open(expanded, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if is_explicit:
                    os.environ[key] = value
                else:
                    os.environ.setdefault(key, value)
    for canonical, aliases in ENV_ALIASES.items():
        if os.environ.get(canonical):
            continue
        for alias in aliases:
            if os.environ.get(alias):
                os.environ[canonical] = os.environ[alias]
                break


def _openai_compatible_chat(provider, prompt, model=None, max_tokens=2500,
                            temperature=0.1):
    load_env()
    config = {
        "cerebras": (
            "CEREBRAS_API_KEY", "CEREBRAS_BASE_URL",
            "https://api.cerebras.ai/v1", "CEREBRAS_MODEL",
            "llama-3.3-70b"),
        "groq": (
            "GROQ_API_KEY", "GROQ_BASE_URL",
            "https://api.groq.com/openai/v1", "GROQ_MODEL",
            "llama-3.3-70b-versatile"),
    }[provider]
    api_key = os.environ.get(config[0], "")
    if not api_key:
        raise RuntimeError("missing_%s" % config[0])
    request = urllib.request.Request(
        os.environ.get(config[1], config[2]).rstrip("/") + "/chat/completions",
        data=json.dumps({
            "model": model or os.environ.get(config[3], config[4]),
            "messages": [{"role": "system", "content": "Return only valid JSON. No prose."},
                         {"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }).encode("utf-8"),
        headers={"Authorization": "Bearer " + api_key,
                 "Content-Type": "application/json",
                 "User-Agent": "flujo-mak-batches/1.0"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        payload = json.loads(response.read().decode("utf-8", "replace"))
    return (payload["choices"][0]["message"]["content"] or "").strip()


def _gemini_chat(prompt, model=None, max_tokens=2500, response_format=None):
    load_env()
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("missing_GEMINI_API_KEY")
    payload = {
        "contents": [{"role": "user", "parts": [{"text": str(prompt)}]}],
        "generationConfig": {"temperature": 0.1,
                              # Structured output needs headroom for the
                              # complete JSON object, even when the caller
                              # asks for a tiny smoke-test budget.
                              "maxOutputTokens": max(
                                  512 if response_format else 128,
                                  int(max_tokens),
                              )},
    }
    if response_format:
        payload["generationConfig"]["responseMimeType"] = "application/json"
    request = urllib.request.Request(
        "https://generativelanguage.googleapis.com/v1beta/models/"
        + (model or os.environ.get("GEMINI_MODEL", "gemini-3.6-flash"))
        + ":generateContent?key=" + api_key,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "User-Agent": "flujo-mak-batches/1.0"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        payload = json.loads(response.read().decode("utf-8", "replace"))
    candidates = payload.get("candidates") or []
    content = (candidates[0].get("content") if candidates else {}) or {}
    parts = content.get("parts") or []
    return ((parts[0].get("text") if parts else "") or "").strip()


def _call_unobserved(provider, prompt, model=None, max_tokens=2500,
                     temperature=0.1, response_format=None, image_paths=None,
                     parent_job_id=None):
    provider = str(provider or "").lower()
    if provider in ("cerebras", "groq", "gemini") and not _reserve_bounded_external(provider):
        raise RuntimeError("external_budget_exceeded:%s" % provider)
    if provider == "ollama":
        load_env()
        try:
            from . import discernment
        except ImportError:
            import discernment
        ollama_kwargs = {
            "base_url": os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
            "model": model or os.environ.get("OLLAMA_MODEL", "gemma3:4b"),
            "max_tokens": max_tokens,
            "temperature": temperature,
            "response_format": response_format,
        }
        if parent_job_id is not None:
            ollama_kwargs["parent_job_id"] = parent_job_id
        with _shared_local_gpu("providers-ollama-%s" % os.getpid(), 2500):
            return discernment.call_ollama(prompt, **ollama_kwargs)
    if provider in ("cerebras", "groq"):
        return _openai_compatible_chat(provider, prompt, model=model,
                                       max_tokens=max_tokens,
                                       temperature=temperature)
    if provider == "gemini":
        return _gemini_chat(prompt, model=model, max_tokens=max_tokens,
                            response_format=response_format)
    raise ValueError("unknown_provider:%s" % provider)


def call(provider, prompt, model=None, max_tokens=2500, temperature=0.1,
         response_format=None, image_paths=None):
    """Call one provider and attach bounded shadow evidence when enabled."""
    try:
        from cultura.mak_conductor.runtime import active_enabled
    except ImportError:
        sys.path.insert(0, os.environ.get("MAK_CONDUCTOR_PATH",
                                         "/home/mak/flujo/cultura"))
        from mak_conductor.runtime import active_enabled
    if active_enabled():
        try:
            from cultura.mak_conductor.runtime import dispatch_sync
        except ImportError:
            sys.path.insert(0, os.environ.get("MAK_CONDUCTOR_PATH",
                                             "/home/mak/flujo/cultura"))
            from mak_conductor.runtime import dispatch_sync
        prompt_hash = hashlib.sha256(str(prompt).encode("utf-8")).hexdigest()

        def handle(job):
            result = _call_unobserved(
                provider, prompt, model=model, max_tokens=max_tokens,
                temperature=temperature, response_format=response_format,
                image_paths=image_paths,
                parent_job_id=job["job_id"])
            return {"validated": bool(str(result or "").strip()),
                    "provider": provider, "text": result}

        queued = dispatch_sync(
            "external_call", {
                "provider": provider, "prompt": str(prompt),
                "prompt_hash": prompt_hash,
                "prompt_length": len(str(prompt)), "model": model or "",
                "max_tokens": max_tokens,
                "temperature": float(temperature),
                "response_format": response_format or "",
                "image_paths": list(image_paths or []),
            }, producer="platform.providers.call",
            handler=handle,
            estimated_vram_mb=2500 if provider == "ollama" else 0,
            model=model or provider, template_version="provider-call-v2")
        if queued and queued.get("queue_status") == "COMPLETED":
            return queued.get("text", "")
        if queued and queued.get("status") == "COMPLETED":
            return queued.get("text", "")
        raise RuntimeError("queued provider call failed: %s" %
                           (queued or {}).get("error", "not executed"))
    try:
        from cultura.mak_conductor.runtime import (enqueue_shadow,
                                                    observe_shadow)
    except ImportError:
        sys.path.insert(0, os.environ.get("MAK_CONDUCTOR_PATH",
                                         "/home/mak/flujo/cultura"))
        try:
            from mak_conductor.runtime import (enqueue_shadow,
                                               observe_shadow)
        except ImportError:
            enqueue_shadow = observe_shadow = None
    started = time.time()
    shadow_job = (enqueue_shadow(
        "external_call", {"provider": provider,
                           "prompt_hash": hashlib.sha256(
                               str(prompt).encode("utf-8")).hexdigest(),
                           "prompt_preview": str(prompt)[:256],
                           "model": model or "", "max_tokens": max_tokens},
        producer="platform.providers.call", estimated_vram_mb=(
            2500 if provider == "ollama" else 0),
        model=model or provider, template_version="provider-call-v1")
        if enqueue_shadow is not None else None)
    try:
        result = _call_unobserved(
            provider, prompt, model=model, max_tokens=max_tokens,
            temperature=temperature, response_format=response_format,
            image_paths=image_paths,
            parent_job_id=(shadow_job or {}).get("job_id"))
    except Exception as exc:
        if observe_shadow is not None:
            observe_shadow(
                shadow_job, producer="platform.providers.call",
                result_status="FAILED", payload={"provider": provider,
                                                  "error": str(exc)[:2000]},
                started_at=started, owner_pid=os.getpid())
        raise
    if observe_shadow is not None:
        observe_shadow(
            shadow_job, producer="platform.providers.call",
            result_status="READY", validated=bool(str(result or "").strip()),
            payload={"provider": provider}, started_at=started,
            owner_pid=os.getpid())
    return result
