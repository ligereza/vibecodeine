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
ALLOWED_EVENT_PROPERTIES = {
    "component", "operation", "health", "provider", "model", "status",
    "error_class", "job_hash", "prompt_hash", "resource_count", "deployment",
    "privacy", "source", "experiment_id", "dataset_fingerprint", "decision",
}
ALLOWED_EVENT_MEASUREMENTS = {
    "latency_ms", "prompt_tokens", "completion_tokens", "total_tokens",
    "resource_count", "candidate_count", "schema_version", "duration_ms",
}


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
        "[].{name:name,type:type,resourceGroup:resourceGroup,location:location,"
        "state:provisioningState,sku:sku.name,kind:kind}",
    ])
    return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []


def _subscription_state() -> dict[str, Any]:
    value = _az_json([
        "rest", "--method", "get", "--url",
        "https://management.azure.com/subscriptions/" + SUBSCRIPTION_ID
        + "?api-version=2022-12-01",
        "--query", "{state:state,quota_id:subscriptionPolicies.quotaId,"
        "spending_limit:subscriptionPolicies.spendingLimit}",
    ])
    return value if isinstance(value, dict) else {}


def _service_rows(resources: list[dict[str, Any]],
                  subscription_state: str = "") -> list[dict[str, Any]]:
    types = [str(row.get("type", "")).lower() for row in resources]

    def has(type_name: str) -> bool:
        return type_name.lower() in types

    def rows_for(type_name: str) -> list[dict[str, Any]]:
        return [
            {"name": row.get("name"), "resource_group": row.get("resourceGroup"),
             "location": row.get("location"), "state": row.get("state"),
             "sku": row.get("sku"), "kind": row.get("kind")}
            for row in resources
            if str(row.get("type", "")).lower() == type_name.lower()
        ]

    definitions = [
        ("search", "Microsoft.Search/searchServices", "/api/azure/search/tools",
         "operational", "Hub route active; read-only corpus retrieval"),
        ("foundry", "Microsoft.CognitiveServices/accounts", "/api/azure/chat",
         "operational_guarded", "Opt-in model provider; deployment must be verified per call"),
        ("machine_learning", "Microsoft.MachineLearningServices/workspaces",
         "tools/azure_ml_learning_dataset.py + /api/azure/status", "operational", "Sanitized evaluation lineage and MLflow calibration"),
        ("storage", "Microsoft.Storage/storageAccounts", "/api/azure/status",
         "metadata_only", "Metadata only until a data-plane role and consumer are approved"),
        ("key_vault", "Microsoft.KeyVault/vaults", "/api/azure/status",
         "dependency_only", "Dependency metadata only; never bulk-read secrets"),
        ("container_registry", "Microsoft.ContainerRegistry/registries",
         "/api/azure/status", "dependency_only", "ML dependency metadata only"),
        ("application_insights", "Microsoft.Insights/components",
         "/api/azure/status", "partial",
         "Verified metadata-only ingestion; workload forwarding remains opt-in"),
        ("api_management", "Microsoft.ApiManagement/service", "/api/azure/status",
         "not_operational", "Inventory only until a concrete backend exists"),
    ]
    result = []
    for service_id, type_name, consumer, integration_state, decision in definitions:
        service_rows = rows_for(type_name)
        effective_integration = integration_state if service_rows else "absent"
        if subscription_state.lower() == "disabled" and service_id in {
                "search", "foundry", "machine_learning"} and service_rows:
            effective_integration = "blocked_subscription"
        result.append({
            "id": service_id,
            "resource_type": type_name,
            "resource_state": "live" if service_rows else "absent",
            "integration_state": effective_integration,
            "consumer": consumer if service_rows else None,
            "decision": decision,
            "resources": service_rows,
        })
    return result


def snapshot() -> dict[str, Any]:
    """Return the live resource map without revealing credentials."""
    try:
        resources = _resource_inventory()
        subscription = _subscription_state()
    except RuntimeError as exc:
        return {"schema": SCHEMA, "available": False, "error": str(exc)}
    return {
        "schema": SCHEMA,
        "available": True,
        "subscription_id": SUBSCRIPTION_ID,
        "subscription": subscription,
        "resource_group": RESOURCE_GROUP,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "services": _service_rows(resources, str(subscription.get("state", ""))),
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
    """Send one allowlisted technical event and verify ingestion acceptance.

    Unknown keys are dropped before serialization.  This prevents a caller
    from accidentally placing prompts, documents or identifiers in telemetry
    merely by naming a new property.
    """
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
            if str(key) in ALLOWED_EVENT_PROPERTIES and value is not None
        }
        safe_measurements = {}
        for key, value in (measurements or {}).items():
            if str(key) not in ALLOWED_EVENT_MEASUREMENTS:
                continue
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
            raw = response.read(4096)
        try:
            receipt = json.loads(raw.decode("utf-8")) if raw else {}
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise RuntimeError("appinsights_invalid_receipt") from None
        if (not isinstance(receipt, dict) or receipt.get("itemsAccepted") != 1
                or receipt.get("errors")):
            raise RuntimeError("appinsights_event_rejected")
        return {"available": True, "sent": True, "resource": APPINSIGHTS_NAME,
                "event": str(name)[:120], "items_accepted": 1,
                "dropped_properties": len(properties or {}) - len(safe_properties),
                "dropped_measurements": len(measurements or {}) - len(safe_measurements)}
    except RuntimeError as exc:
        return {"available": False, "sent": False, "error": str(exc)}
    except (urllib.error.URLError, TimeoutError, OSError):
        return {"available": False, "sent": False, "error": "appinsights_unreachable"}
