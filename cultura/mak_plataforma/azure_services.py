#!/usr/bin/env python3
"""Live inventory and metadata-only telemetry for MAK's Azure resources.

This module is intentionally narrower than an infrastructure provisioner.  It
uses the existing Azure CLI session to report what is really present, and it
can emit Application Insights events containing only technical metadata.  It
does not upload MAK corpus, prompts, photos, audio, PII, or secrets.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any


SCHEMA = "mak-azure-services-v1"
SUBSCRIPTION_ID = os.environ.get(
    "MAK_AZURE_SUBSCRIPTION_ID",
    "6519fcfc-3807-407e-bae5-5f1f7f64e337",
)
RESOURCE_GROUP = os.environ.get("MAK_AZURE_RESOURCE_GROUP", "makmak")
APPINSIGHTS_NAME = os.environ.get("MAK_APPINSIGHTS_NAME", "makmak-ml-insights")
_CONNECTION_LOCK = threading.Lock()
_CONNECTION_CACHE: tuple[str, float] | None = None


def _az_path() -> str | None:
    return os.environ.get("AZ_CLI") or shutil.which("az")


def _az_json(arguments: list[str], *, timeout: int = 20) -> Any:
    az = _az_path()
    if not az:
        raise RuntimeError("azure_cli_unavailable")
    completed = subprocess.run(
        [az, *arguments, "-o", "json"],
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if completed.returncode != 0:
        raise RuntimeError("azure_cli_command_failed")
    try:
        return json.loads(completed.stdout or "null")
    except (TypeError, ValueError, json.JSONDecodeError):
        raise RuntimeError("azure_cli_invalid_json") from None


def _resource_inventory() -> list[dict[str, Any]]:
    rows = _az_json([
        "resource", "list", "--subscription", SUBSCRIPTION_ID,
        "--query",
        "[].{name:name,type:type,resourceGroup:resourceGroup,location:location,state:provisioningState}",
    ])
    return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []


def _service_rows(resources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    types = [str(row.get("type", "")).lower() for row in resources]

    def has(type_name: str) -> bool:
        return type_name.lower() in types

    def rows_for(type_name: str) -> list[dict[str, Any]]:
        return [
            {"name": row.get("name"), "resource_group": row.get("resourceGroup"),
             "location": row.get("location"), "state": row.get("state")}
            for row in resources
            if str(row.get("type", "")).lower() == type_name.lower()
        ]

    definitions = [
        ("search", "Microsoft.Search/searchServices", "/api/azure/search/tools",
         "Hub route active; read-only corpus retrieval"),
        ("foundry", "Microsoft.CognitiveServices/accounts", "/api/azure/chat",
         "Opt-in model provider; deployment must be verified per call"),
        ("machine_learning", "Microsoft.MachineLearningServices/workspaces",
         "/api/azure/status", "Workspace inventory and MLflow calibration"),
        ("storage", "Microsoft.Storage/storageAccounts", "/api/azure/status",
         "Metadata only until a data-plane role and consumer are approved"),
        ("key_vault", "Microsoft.KeyVault/vaults", "/api/azure/status",
         "Dependency metadata only; never bulk-read secrets"),
        ("container_registry", "Microsoft.ContainerRegistry/registries",
         "/api/azure/status", "ML dependency metadata only"),
        ("application_insights", "Microsoft.Insights/components",
         "/api/azure/status", "Metadata-only technical telemetry"),
        ("api_management", "Microsoft.ApiManagement/service", "/api/azure/status",
         "Inventory only until a concrete backend exists"),
    ]
    result = []
    for service_id, type_name, consumer, decision in definitions:
        service_rows = rows_for(type_name)
        result.append({
            "id": service_id,
            "resource_type": type_name,
            "state": "live" if service_rows else "absent",
            "consumer": consumer if service_rows else None,
            "decision": decision,
            "resources": service_rows,
        })
    return result


def snapshot() -> dict[str, Any]:
    """Return the live resource map without revealing credentials."""
    try:
        resources = _resource_inventory()
    except RuntimeError as exc:
        return {"schema": SCHEMA, "available": False, "error": str(exc)}
    return {
        "schema": SCHEMA,
        "available": True,
        "subscription_id": SUBSCRIPTION_ID,
        "resource_group": RESOURCE_GROUP,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "services": _service_rows(resources),
        "resource_count": len(resources),
        "telemetry": {
            "resource": APPINSIGHTS_NAME,
            "payload_policy": "metadata_only",
            "secrets_in_payload": False,
        },
        "credit_policy": {
            "student_model_calls": "blocked_by_default",
            "enable_variable": "MAK_AZURE_ALLOW_CREDIT",
            "search_free_route": "/api/azure/search/tools",
        },
    }


def _connection_string() -> str:
    """Resolve App Insights configuration from Azure CLI without persisting it."""
    global _CONNECTION_CACHE
    now = time.monotonic()
    with _CONNECTION_LOCK:
        if _CONNECTION_CACHE and _CONNECTION_CACHE[1] > now:
            return _CONNECTION_CACHE[0]
        explicit = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
        if explicit:
            _CONNECTION_CACHE = (explicit, now + 600)
            return explicit
        raw = _az_json([
            "monitor", "app-insights", "component", "show",
            "--resource-group", RESOURCE_GROUP, "--app", APPINSIGHTS_NAME,
            "--query", "connectionString",
        ], timeout=15)
        if not isinstance(raw, str) or not raw.strip():
            raise RuntimeError("appinsights_connection_missing")
        _CONNECTION_CACHE = (raw.strip(), now + 600)
        return _CONNECTION_CACHE[0]


def emit_event(name: str, *, properties: dict[str, Any] | None = None,
               measurements: dict[str, float] | None = None) -> dict[str, Any]:
    """Send one technical event; caller values are bounded and content-free."""
    try:
        connection = _connection_string()
        parts = dict(
            item.split("=", 1) for item in connection.split(";")
            if "=" in item
        )
        instrumentation_key = parts.get("InstrumentationKey", "").strip()
        ingestion = (parts.get("IngestionEndpoint") or
                     "https://dc.services.visualstudio.com/").rstrip("/")
        if not instrumentation_key:
            raise RuntimeError("appinsights_instrumentation_key_missing")
        safe_properties = {
            str(key)[:80]: str(value)[:160]
            for key, value in (properties or {}).items()
            if str(key) and value is not None
        }
        safe_measurements = {}
        for key, value in (measurements or {}).items():
            try:
                safe_measurements[str(key)[:80]] = float(value)
            except (TypeError, ValueError):
                continue
        payload = {
            "name": "Microsoft.ApplicationInsights.Event",
            "time": datetime.now(timezone.utc).isoformat(),
            "iKey": instrumentation_key,
            "tags": {"ai.cloud.role": "mak-hub"},
            "data": {"baseType": "EventData", "baseData": {
                "ver": 2, "name": str(name)[:120],
                "properties": safe_properties,
                "measurements": safe_measurements,
            }},
        }
        request = urllib.request.Request(
            ingestion + "/v2/track",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(request, timeout=10) as response:
            response.read(64)
        return {"available": True, "sent": True, "resource": APPINSIGHTS_NAME,
                "event": str(name)[:120]}
    except RuntimeError as exc:
        return {"available": False, "sent": False, "error": str(exc)}
    except (urllib.error.URLError, TimeoutError, OSError):
        return {"available": False, "sent": False, "error": "appinsights_unreachable"}
