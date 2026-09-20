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
import re
import shutil
import subprocess
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "mak-azure-services-v1"
SUBSCRIPTION_ID = os.environ.get(
    "MAK_AZURE_SUBSCRIPTION_ID",
    "6519fcfc-3807-407e-bae5-5f1f7f64e337",
)
RESOURCE_GROUP = os.environ.get("MAK_AZURE_RESOURCE_GROUP", "makmak")
APPINSIGHTS_NAME = os.environ.get("MAK_APPINSIGHTS_NAME", "makmak-ml-insights")
ML_STAGING_ROOT_ENV = "MAK_AZURE_ML_STAGING_ROOT"
DEFAULT_ML_STAGING_ROOT = "/home/mak/research/azure-ml/staging"
ML_LINEAGE_SCHEMA = "mak-azure-ml-learning-lineage-v1"
ML_RECEIPT_SCHEMA = "mak-azure-ml-learning-dataset-v1"
_SAFE_COUNTER_KEY = re.compile(r"[A-Za-z0-9_.:-]{1,80}\Z")
_SAFE_VALUE = re.compile(r"[A-Za-z0-9_.:-]{1,160}\Z")
_SHA256 = re.compile(r"[0-9a-fA-F]{64}\Z")
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
         "/api/azure/status", "operational", "Metadata-only technical telemetry"),
        ("api_management", "Microsoft.ApiManagement/service", "/api/azure/status",
         "not_operational", "Inventory only until a concrete backend exists"),
    ]
    result = []
    for service_id, type_name, consumer, integration_state, decision in definitions:
        service_rows = rows_for(type_name)
        result.append({
            "id": service_id,
            "resource_type": type_name,
            "resource_state": "live" if service_rows else "absent",
            "integration_state": integration_state if service_rows else "absent",
            "consumer": consumer if service_rows else None,
            "decision": decision,
            "resources": service_rows,
        })
    return result


def _ml_staging_root() -> Path:
    return Path(os.environ.get(ML_STAGING_ROOT_ENV, DEFAULT_ML_STAGING_ROOT)).expanduser()


def _safe_counter(value: Any) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    result: dict[str, int] = {}
    for key, count in value.items():
        if (not isinstance(key, str) or not _SAFE_COUNTER_KEY.fullmatch(key)
                or isinstance(count, bool) or not isinstance(count, int) or count < 0):
            continue
        result[key] = count
    return result


def _safe_value(value: Any) -> str | None:
    if not isinstance(value, str) or not _SAFE_VALUE.fullmatch(value):
        return None
    return value


def _project_learning_receipt(receipt: Any) -> dict[str, Any] | None:
    if not isinstance(receipt, dict) or receipt.get("schema") != ML_RECEIPT_SCHEMA:
        return None
    projected: dict[str, Any] = {
        "schema": ML_LINEAGE_SCHEMA,
        "available": True,
        "status": "present",
    }
    rows = receipt.get("rows")
    if isinstance(rows, int) and not isinstance(rows, bool) and rows >= 0:
        projected["rows"] = rows
    fingerprints = receipt.get("dataset_fingerprints")
    if isinstance(fingerprints, list):
        projected["fingerprint_count"] = sum(
            1 for item in fingerprints if isinstance(item, str) and item
        )
    projected["statuses"] = _safe_counter(receipt.get("statuses"))
    projected["target_kinds"] = _safe_counter(receipt.get("target_kinds"))
    digest = receipt.get("dataset_sha256")
    if isinstance(digest, str) and _SHA256.fullmatch(digest):
        projected["dataset_sha256"] = digest.lower()
    for field in ("mlflow_run_id", "artifact_upload", "artifact_builder"):
        safe = _safe_value(receipt.get(field))
        if safe is not None:
            projected[field] = safe
    return projected


def _learning_receipt_candidates(root: Path) -> list[Path]:
    try:
        entries = list(root.iterdir())
    except OSError:
        return []
    candidates: list[tuple[int, str, Path]] = []
    for entry in entries:
        if not entry.is_dir() or entry.is_symlink():
            continue
        receipt = entry / "receipt.json"
        if receipt.is_symlink() or not receipt.is_file():
            continue
        try:
            stamp = receipt.stat().st_mtime_ns
        except OSError:
            continue
        candidates.append((stamp, entry.name, receipt))
    candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [item[2] for item in candidates]


def machine_learning_lineage() -> dict[str, Any]:
    """Project the newest local learning receipt without exposing its path."""
    candidates = _learning_receipt_candidates(_ml_staging_root())
    if not candidates:
        return {
            "schema": ML_LINEAGE_SCHEMA,
            "available": False,
            "status": "absent",
        }
    receipt_path = candidates[0]
    try:
        if receipt_path.stat().st_size > 2_000_000:
            raise ValueError("receipt_too_large")
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return {
            "schema": ML_LINEAGE_SCHEMA,
            "available": False,
            "status": "invalid",
        }
    projected = _project_learning_receipt(receipt)
    if projected is None:
        return {
            "schema": ML_LINEAGE_SCHEMA,
            "available": False,
            "status": "invalid",
        }
    return projected


def snapshot() -> dict[str, Any]:
    """Return the live resource map without revealing credentials."""
    lineage = machine_learning_lineage()
    try:
        resources = _resource_inventory()
    except RuntimeError as exc:
        return {
            "schema": SCHEMA,
            "available": False,
            "error": str(exc),
            "machine_learning_lineage": lineage,
        }
    return {
        "schema": SCHEMA,
        "available": True,
        "subscription_id": SUBSCRIPTION_ID,
        "resource_group": RESOURCE_GROUP,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "services": _service_rows(resources),
        "resource_count": len(resources),
        "machine_learning_lineage": lineage,
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
