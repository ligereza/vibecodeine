#!/usr/bin/env python3
"""Report Azure usage/cost evidence without treating missing cost as zero.

This command is read-only.  It correlates the live ARM inventory with the
Consumption usage feed, reports whether monetary values are actually present,
and names review decisions for the persistent resources in MAK's student
subscription.  It never creates budgets or changes resources.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import date, timedelta
from typing import Any


SUBSCRIPTION_ID = "6519fcfc-3807-407e-bae5-5f1f7f64e337"
TARGET_TYPES = {
    "microsoft.apimanagement/service": "review_no_backend",
    "microsoft.containerregistry/registries": "review_workspace_binding",
    "microsoft.storage/storageaccounts": "retain_only_with_named_consumer",
    "microsoft.keyvault/vaults": "retain_workspace_dependency",
}


class InventoryError(RuntimeError):
    pass


def _az_json(arguments: list[str], timeout: int = 60) -> Any:
    az = shutil.which("az")
    if not az:
        raise InventoryError("azure_cli_unavailable")
    completed = subprocess.run(
        [az, *arguments, "-o", "json"], check=False, capture_output=True,
        text=True, timeout=timeout,
    )
    if completed.returncode != 0:
        raise InventoryError("azure_cli_command_failed")
    try:
        return json.loads(completed.stdout or "null")
    except json.JSONDecodeError:
        raise InventoryError("azure_cli_invalid_json") from None


def _money(value: Any) -> float | None:
    if value is None or str(value).strip().lower() in {"", "none", "null"}:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def build_snapshot(resources: list[dict[str, Any]], budgets: list[dict[str, Any]],
                   usage: list[dict[str, Any]], *, start: str, end: str,
                   subscription: dict[str, Any] | None = None) -> dict[str, Any]:
    live_ids = {str(row.get("id", "")).lower() for row in resources if row.get("id")}
    measured_costs = [_money(row.get("pretaxCost")) for row in usage]
    numeric_costs = [value for value in measured_costs if value is not None]
    live_usage = 0
    historic_usage = 0
    for row in usage:
        resource_id = str(row.get("instanceId") or row.get("instanceName") or "").lower()
        if resource_id and resource_id in live_ids:
            live_usage += 1
        else:
            historic_usage += 1

    decisions = []
    for row in resources:
        resource_type = str(row.get("type", "")).lower()
        if resource_type not in TARGET_TYPES:
            continue
        name = str(row.get("name", ""))
        decision = TARGET_TYPES[resource_type]
        if resource_type == "microsoft.storage/storageaccounts":
            if name == "makmakmlstorage":
                decision = "retain_workspace_dependency"
            elif name == "makinspace":
                decision = "review_no_measured_share_or_consumer"
        decisions.append({
            "name": name,
            "type": row.get("type"),
            "sku": (row.get("sku") or {}).get("name")
            if isinstance(row.get("sku"), dict) else row.get("sku"),
            "decision": decision,
            "action_taken": "none_read_only_measurement",
        })
    return {
        "schema": "mak-azure-cost-inventory-v1",
        "subscription_id": SUBSCRIPTION_ID,
        "subscription": {
            "display_name": (subscription or {}).get("displayName"),
            "state": (subscription or {}).get("state"),
            "quota_id": ((subscription or {}).get("subscriptionPolicies") or {}).get("quotaId"),
            "spending_limit": ((subscription or {}).get("subscriptionPolicies") or {}).get("spendingLimit"),
        },
        "period": {"start": start, "end": end},
        "live_resource_count": len(resources),
        "budget_count": len(budgets),
        "usage_rows": len(usage),
        "usage_rows_for_live_resources": live_usage,
        "usage_rows_for_absent_or_unresolved_resources": historic_usage,
        "monetary_cost": {
            "status": "measured" if len(numeric_costs) == len(usage) and usage else "unavailable",
            "numeric_rows": len(numeric_costs),
            "total": round(sum(numeric_costs), 6) if numeric_costs else None,
            "rule": "null or absent cost is unknown, never zero",
        },
        "decisions": sorted(decisions, key=lambda row: (str(row["type"]), row["name"])),
        "mutations": [],
    }


def collect(start: str, end: str) -> dict[str, Any]:
    resources = _az_json(["resource", "list", "--subscription", SUBSCRIPTION_ID]) or []
    budgets = _az_json(["consumption", "budget", "list"]) or []
    usage = _az_json([
        "consumption", "usage", "list", "--start-date", start,
        "--end-date", end, "--include-meter-details", "true",
    ], timeout=120) or []
    subscription = _az_json([
        "rest", "--method", "get", "--url",
        "https://management.azure.com/subscriptions/" + SUBSCRIPTION_ID
        + "?api-version=2022-12-01",
    ]) or {}
    return build_snapshot(resources, budgets, usage, start=start, end=end,
                          subscription=subscription)


def main(argv: list[str] | None = None) -> int:
    today = date.today()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default=(today - timedelta(days=30)).isoformat())
    parser.add_argument("--end", default=today.isoformat())
    args = parser.parse_args(argv)
    try:
        result = collect(args.start, args.end)
    except InventoryError as exc:
        print(json.dumps({"schema": "mak-azure-cost-inventory-v1",
                          "available": False, "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
