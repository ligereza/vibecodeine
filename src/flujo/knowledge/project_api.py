"""Read-only API helpers shared by the local Hub surfaces.

Both the canonical ``flujo serve`` Hub and the legacy 8900 MAK projection use
this module.  It intentionally never calls ``ensure_schema``: a GET or route
preview must not silently migrate the real knowledge database.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .project_ir import validate_project_ir
from .project_router import route_project
from .episode_runner import probe_declared_consumer, record_probe
from .learning_policy import learning_summary as learning_policy_summary


def _read_only_connection(path: Path) -> sqlite3.Connection:
    return sqlite3.connect("file:" + str(path) + "?mode=ro", uri=True)


def learning_summary(database: str | Path) -> dict[str, Any]:
    path = Path(database).expanduser()
    if not path.is_file():
        return {"available": False, "reason": "database_missing", "database": path.name}
    try:
        con = _read_only_connection(path)
        tables = {row[0] for row in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN "
            "('project_records','project_episodes','semantic_rules','project_contracts')"
        )}
        if "project_records" not in tables:
            con.close()
            return {"available": False, "reason": "learning_schema_not_initialized", "database": path.name}
        result: dict[str, Any] = {"available": True, "database": path.name}
        result["policy"] = learning_policy_summary(path)
        result["projects"] = {row[0]: row[1] for row in con.execute("SELECT state,COUNT(*) FROM project_records GROUP BY state")}
        result["episodes"] = {row[0]: row[1] for row in con.execute("SELECT status,COUNT(*) FROM project_episodes GROUP BY status")}
        result["rules"] = {row[0]: row[1] for row in con.execute("SELECT status,COUNT(*) FROM semantic_rules GROUP BY status")} if "semantic_rules" in tables else {}
        if "project_contracts" in tables:
            result["contracts"] = {
                "available": True,
                "counts": {
                    row[0]: row[1] for row in con.execute(
                        "SELECT kind,COUNT(*) FROM project_contracts WHERE status!='stale' GROUP BY kind"
                    )
                },
                "statuses": {
                    row[0]: row[1] for row in con.execute(
                        "SELECT status,COUNT(*) FROM project_contracts GROUP BY status"
                    )
                },
            }
        else:
            result["contracts"] = {"available": False, "reason": "contract_registry_not_initialized"}
        if "project_contract_audits" in {
            row[0] for row in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='project_contract_audits'"
            )
        }:
            latest_run = con.execute(
                "SELECT run_id FROM project_contract_audits GROUP BY run_id "
                "ORDER BY MAX(observed_at) DESC, run_id DESC LIMIT 1"
            ).fetchone()
            run_id = latest_run[0] if latest_run else None
            attention = []
            if run_id:
                for contract_key, status, evidence_json in con.execute(
                    "SELECT contract_id,status,evidence_json FROM project_contract_audits "
                    "WHERE run_id=? AND status!='verified' ORDER BY contract_id", (run_id,)
                ):
                    try:
                        evidence = json.loads(evidence_json)
                    except json.JSONDecodeError:
                        evidence = {}
                    dependencies = evidence.get("dependencies", []) if isinstance(evidence, dict) else []
                    missing = [item.get("name") for item in dependencies if isinstance(item, dict) and not item.get("available")]
                    attention.append({"contract_id": contract_key, "status": status, "missing": missing})
            result["audits"] = {
                "available": bool(run_id),
                "latest_run": run_id,
                "statuses": {
                    row[0]: row[1] for row in con.execute(
                        "SELECT status,COUNT(*) FROM project_contract_audits WHERE run_id=? GROUP BY status",
                        (run_id,),
                    )
                } if run_id else {},
                "attention": attention,
            }
        else:
            result["audits"] = {"available": False, "reason": "contract_audit_not_initialized"}
        result["latest_abstain"] = None
        if "project_episodes" in tables:
            row = con.execute(
                "SELECT episode_id,project_id,status,phase,objective,started_at,finished_at "
                "FROM project_episodes WHERE status='abstained' "
                "ORDER BY COALESCE(finished_at,started_at,episode_id) DESC LIMIT 1"
            ).fetchone()
            if row:
                result["latest_abstain"] = {
                    "episode_id": row[0],
                    "project_id": row[1],
                    "status": row[2],
                    "phase": row[3],
                    "objective": row[4],
                    "started_at": row[5],
                    "finished_at": row[6],
                }
        con.close()
        return result
    except (OSError, sqlite3.Error) as exc:
        return {"available": False, "reason": type(exc).__name__, "database": path.name}


def operational_status(database: str | Path, *, repo_root: str | Path | None = None) -> dict[str, Any]:
    """Return the bounded machine-readable status of the MAK knowledge loop.

    This is deliberately read-only.  ``learning_summary`` remains the
    compatibility payload for existing consumers; this normalized envelope is
    the single status surface for the CLI and the Hub.  It reports evidence
    gaps and safe abstentions as actionable state rather than pretending that
    either one is a successful prediction.
    """
    path = Path(database).expanduser()
    summary = learning_summary(path)
    attention: list[dict[str, Any]] = []

    def add_item(
        item_id: str,
        kind: str,
        status: str,
        severity: str,
        reason: str,
        next_action: str,
        *,
        ref: str | None = None,
    ) -> None:
        attention.append({
            "id": item_id,
            "kind": kind,
            "status": status,
            "severity": severity,
            "reason": reason,
            "next_action": next_action,
            **({"ref": ref} if ref else {}),
        })

    if not summary.get("available"):
        add_item(
            "learning_ledger",
            "ledger",
            "unavailable",
            "attention",
            str(summary.get("reason", "database_missing")),
            "initialize or configure the local MAK knowledge database before recording results",
            ref=str(path),
        )
    else:
        for state, count in sorted((summary.get("projects") or {}).items()):
            if state == "blocked":
                add_item(
                    f"projects:{state}", "projects", state, "blocked",
                    f"{count} project(s) are blocked",
                    "inspect the project evidence and unblock only after a bounded validation",
                )
            elif state == "review_required":
                add_item(
                    f"projects:{state}", "projects", state, "attention",
                    f"{count} project(s) require review",
                    "review evidence and consumer before allowing a project transition",
                )

        for status, count in sorted((summary.get("episodes") or {}).items()):
            if status in {"failed", "error"}:
                add_item(
                    f"episodes:{status}", "episodes", status, "blocked",
                    f"{count} episode(s) failed",
                    "inspect the recorded failure and rerun only the bounded step",
                )
            elif status == "needs_evidence":
                add_item(
                    f"episodes:{status}", "episodes", status, "attention",
                    f"{count} episode(s) need evidence",
                    "attach verifiable evidence, then run the validator again",
                )
            elif status == "abstained":
                add_item(
                    f"episodes:{status}", "episodes", status, "info",
                    f"{count} episode(s) abstained safely",
                    "keep the abstention until the missing evidence or an independent test exists",
                )
            elif status not in {"verified", "succeeded", "completed"}:
                add_item(
                    f"episodes:{status}", "episodes", status, "attention",
                    f"{count} episode(s) are not terminal",
                    "inspect the episode before starting another attempt",
                )

        policy = summary.get("policy") or {}
        if policy.get("status") == "abstain":
            reason = str(policy.get("reason", "policy_abstain"))
            add_item(
                "learning_policy",
                "policy",
                "abstain",
                "info",
                reason,
                "collect an independent verified project before promoting a general policy",
            )

        for audit in (summary.get("audits") or {}).get("attention", []):
            contract_id = str(audit.get("contract_id", "contract"))
            audit_status = str(audit.get("status", "unknown"))
            severity = "blocked" if audit_status in {"failed", "error"} else "attention"
            missing = audit.get("missing") or []
            reason = f"contract audit is {audit_status}"
            if missing:
                reason += f"; missing: {', '.join(map(str, missing))}"
            add_item(
                f"contract:{contract_id}",
                "contract_audit",
                audit_status,
                severity,
                reason,
                "restore or explicitly quarantine the missing dependency, then rerun the contract audit",
                ref=contract_id,
            )

    severities = {item["severity"] for item in attention}
    if not summary.get("available"):
        overall = "unknown"
    elif "blocked" in severities:
        overall = "blocked"
    elif "attention" in severities:
        overall = "attention"
    elif summary.get("available"):
        overall = "ready"
    else:
        overall = "unknown"

    next_actions: list[str] = []
    for item in attention:
        action = item["next_action"]
        if action not in next_actions:
            next_actions.append(action)

    return {
        "schema": "mak-operational-status-v1",
        "status": overall,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "database": str(path),
        "read_only": True,
        "repo_root": str(Path(repo_root).expanduser()) if repo_root is not None else None,
        "learning": summary,
        "attention": attention,
        "counts": {
            "attention": sum(1 for item in attention if item["severity"] == "attention"),
            "blocked": sum(1 for item in attention if item["severity"] == "blocked"),
            "info": sum(1 for item in attention if item["severity"] == "info"),
        },
        "next_actions": next_actions,
    }


def promoted_rules(database: str | Path) -> list[dict[str, Any]]:
    path = Path(database).expanduser()
    if not path.is_file():
        return []
    try:
        con = _read_only_connection(path)
        exists = con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='semantic_rules'").fetchone()
        if not exists:
            con.close()
            return []
        rows = con.execute("SELECT rule_id,trigger_json,action_json,status FROM semantic_rules WHERE status='promoted'").fetchall()
        con.close()
        return [{"rule_id": row[0], "trigger_json": row[1], "action_json": row[2], "status": row[3]} for row in rows]
    except (OSError, sqlite3.Error):
        return []


def route_payload(body: Mapping[str, Any], database: str | Path) -> tuple[dict[str, Any], int]:
    project = body.get("project") if isinstance(body, Mapping) else None
    if not isinstance(project, Mapping):
        project = body if isinstance(body, Mapping) else None
    if not isinstance(project, Mapping):
        return {"ok": False, "error": "project debe ser un objeto"}, 400
    errors = validate_project_ir(project)
    if errors:
        return {"ok": False, "error": "invalid_project_ir", "details": errors[:20]}, 400
    decision = route_project(project, rules=promoted_rules(database))
    return {"ok": True, "decision": decision, "learning": learning_summary(database)}, 200


def probe_payload(
    body: Mapping[str, Any], database: str | Path, *, repo_root: str | Path,
    record: bool = False, episode_id: str | None = None,
) -> tuple[dict[str, Any], int]:
    """Route plus bounded probe; persistence is explicit and existing-project only."""
    routed, status = route_payload(body, database)
    if status != 200:
        return routed, status
    project = body.get("project") if isinstance(body, Mapping) else None
    if not isinstance(project, Mapping):
        project = body
    decision = routed["decision"]
    probe = probe_declared_consumer(project, decision, repo_root=repo_root)
    result: dict[str, Any] = {**routed, "probe": probe, "recorded": False, "episode_id": None}
    if record:
        import sqlite3
        from .project_ir import LearningStore
        with sqlite3.connect("file:" + str(Path(database).expanduser()) + "?mode=ro", uri=True) as con:
            exists = con.execute("SELECT 1 FROM project_records WHERE project_id=?", (project.get("project_id"),)).fetchone()
        if not exists:
            return {"ok": False, "error": "project_must_be_persisted_before_recording"}, 409
        try:
            result["episode_id"] = record_probe(
                LearningStore(database), project, decision, probe, episode_id=episode_id,
            )
        except (OSError, ValueError, sqlite3.Error) as exc:
            return {"ok": False, "error": str(exc)[:300]}, 409
        result["recorded"] = True
    return result, 200
