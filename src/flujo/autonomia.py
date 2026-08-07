"""Director-facing autonomy circuit for external MAK batches.

This module is intentionally thin: it does not become another agent. It checks
whether the repo is safe to operate, then routes bounded batch work to the
durable MAK contracts in ``cultura.mak_plataforma.tandas``.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Iterable

from cultura.mak_plataforma import ledger as common_ledger
from cultura.mak_plataforma import providers as external_providers
from cultura.mak_plataforma import tandas


CANONICAL_BRANCHES = ("main", "mak", "rd", "iskvw")
DEFAULT_AREAS = (
    "mak_quality",
    "rd_evidence",
    "iskvw_curation",
    "tool_archaeology",
    "svg_pipeline",
    "adobe_rescue",
    "opportunity_radar",
)
DEFAULT_PREMIUM_PROVIDERS = ("watsonx", "aws")
DEFAULT_FREE_PROVIDERS = ("cerebras", "groq", "ollama")
LOG_ROOT = Path("_logs") / "cauce_director" / "20260805" / "autonomia"
MAK_SSH_TARGET = "mak@192.168.50.2"
MAK_REPO = "~/flujo"


@dataclass(frozen=True)
class RunOptions:
    areas: tuple[str, ...] = DEFAULT_AREAS
    providers: tuple[str, ...] = DEFAULT_PREMIUM_PROVIDERS
    round_id: str = ""
    out_dir: str = ""
    common_ledger_path: str = tandas.COMMON_LEDGER
    batch_ledger_path: str = tandas.LEDGER
    max_tokens: int = 1800
    max_items: int = 5
    use_ollama: bool = True
    require_clean: bool = True
    dry_run: bool = False
    instruction: str = ""
    executor: str = "local"
    ssh_target: str = MAK_SSH_TARGET
    mak_repo: str = MAK_REPO


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _quarantine_path(common_path: str) -> str:
    return str(Path(common_path).with_name("common_ledger_quarantine.jsonl"))


def _quarantine_summary(path: str) -> dict:
    rows = common_ledger.read_items_quarantine(path)
    return {
        "total": len(rows),
        "by_domain": {
            domain: sum(1 for row in rows if row.get("domain") == domain)
            for domain in sorted({row.get("domain", "") for row in rows})
        },
        "last": rows[-5:],
    }


def _run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=_repo_root(),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=20,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _run_gh(args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["gh", *args],
            cwd=_repo_root(),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
    except OSError:
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _csv(values: str | Iterable[str] | None, default: tuple[str, ...]) -> tuple[str, ...]:
    if values is None:
        return default
    if isinstance(values, str):
        items = [item.strip() for item in values.split(",") if item.strip()]
    else:
        items = [str(item).strip() for item in values if str(item).strip()]
    return tuple(items or default)


def _branch_state() -> dict:
    current = _run_git(["branch", "--show-current"])
    dirty = _run_git(["status", "--porcelain"]).splitlines()
    raw_remote = _run_git([
        "for-each-ref",
        "--format=%(refname:short)",
        "refs/remotes/origin",
    ]).splitlines()
    remote_branches = sorted(
        ref.replace("origin/", "", 1)
        for ref in raw_remote
        if ref.startswith("origin/") and ref != "origin/HEAD"
    )
    extra_remote = sorted(
        ref for ref in remote_branches if ref not in CANONICAL_BRANCHES
    )
    canonical_present = {
        branch: branch in remote_branches for branch in CANONICAL_BRANCHES
    }
    return {
        "current": current,
        "dirty": dirty,
        "remote_branches": remote_branches,
        "canonical_present": canonical_present,
        "extra_remote_branches": extra_remote,
    }


def _open_prs() -> list[dict]:
    raw = _run_gh([
        "pr", "list",
        "--repo", "ligereza/vibecodeine",
        "--state", "open",
        "--json", "number,title,headRefName,baseRefName,mergeStateStatus",
        "--limit", "50",
    ])
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except ValueError:
        return []
    return data if isinstance(data, list) else []


def _provider_state() -> dict:
    external_providers.load_env()
    state = {
        "watsonx": bool(os.environ.get("WATSONX_API_KEY")
                        and os.environ.get("WATSONX_PROJECT_ID")),
        "aws": bool(
            (os.environ.get("AWS_ACCESS_KEY_ID")
             and os.environ.get("AWS_SECRET_ACCESS_KEY"))
            or os.environ.get("AWS_PROFILE")
            or os.environ.get("AWS_CONTAINER_CREDENTIALS_RELATIVE_URI")
            or os.environ.get("AWS_WEB_IDENTITY_TOKEN_FILE")
        ),
        "ollama": _ollama_available(),
        "free_cloud": {
            "cerebras": bool(os.environ.get("CEREBRAS_API_KEY")),
            "groq": bool(os.environ.get("GROQ_API_KEY")),
        },
    }
    return state


def _ollama_available() -> bool:
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
    except OSError:
        return False
    return result.returncode == 0


def _readme_svg_state() -> dict:
    """Report whether the README SVG is synchronized without changing it."""
    try:
        result = subprocess.run(
            [sys.executable, "tools/update_readme_svg.py", "--check"],
            cwd=_repo_root(),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {"status": "unavailable"}
    return {"status": "clean" if result.returncode == 0 else "stale"}


def _operational_state(branches, prs, common, batches, quarantine, readme):
    """Derive a compact action surface from existing status contracts."""
    blocked_prs = [
        pr.get("number") for pr in prs
        if str(pr.get("mergeStateStatus") or "").upper() in {"BLOCKED", "DIRTY"}
    ]
    actions = []
    if branches["dirty"]:
        actions.append("clean_repo_before_promotion")
    if branches["extra_remote_branches"]:
        actions.append("remove_noncanonical_remote_branches")
    if prs:
        actions.append("review_open_promotion_prs")
    if blocked_prs:
        actions.append("repair_blocked_promotion_prs")
    if quarantine["total"]:
        actions.append("review_quarantined_evidence")
    if readme.get("status") == "stale":
        actions.append("refresh_readme_svg")
    if not actions:
        actions.append("run_one_directed_domain_cycle")
    return {
        "schema": "flujo-operational-state-v1",
        "branch_policy": {
            "canonical": list(CANONICAL_BRANCHES),
            "remote": branches["remote_branches"],
            "extra_remote": branches["extra_remote_branches"],
        },
        "promotion": {
            "open_prs": len(prs),
            "blocked_prs": blocked_prs,
        },
        "memory": {
            "common_rows": common.get("total", 0),
            "batch_rows": batches.get("total", 0),
            "quarantined_rows": quarantine.get("total", 0),
        },
        "visual_surface": {"readme_svg": readme.get("status", "unknown")},
        "next_actions": actions,
    }


def _ssh_json(target: str, command: str, timeout: int = 900) -> dict:
    result = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", target, command],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    try:
        payload = json.loads(result.stdout)
    except ValueError:
        payload = None
    if isinstance(payload, dict):
        payload.setdefault("remote_exit_code", result.returncode)
        return payload
    if result.returncode != 0:
        return {
            "ok": False,
            "status": "ssh_error",
            "errors": [(result.stderr or result.stdout or "ssh_failed")[:500]],
        }
    return {
        "ok": False,
        "status": "remote_output_not_json",
        "errors": [result.stdout[:500]],
    }


def mak_status(target: str = MAK_SSH_TARGET, repo: str = MAK_REPO) -> dict:
    command = (
        "cd %s && "
        "python3 -m cultura.mak_plataforma.tandas summary && "
        "python3 -m cultura.mak_plataforma.ledger summary"
    ) % repo
    result = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", target, command],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    return {
        "target": target,
        "repo": repo,
        "reachable": result.returncode == 0,
        "stdout_preview": (result.stdout or "")[:1000],
        "stderr_preview": (result.stderr or "")[:500],
    }


def autonomy_status(common_path: str = tandas.COMMON_LEDGER,
                    batch_path: str = tandas.LEDGER,
                    include_local_providers: bool = False) -> dict:
    branches = _branch_state()
    prs = _open_prs()
    provider_state = (
        _provider_state() if include_local_providers
        else {"executor": "mak", "local_providers": "not_used"}
    )
    blockers = []
    if branches["dirty"]:
        blockers.append("repo_dirty")
    missing = [
        name for name, present in branches["canonical_present"].items()
        if not present
    ]
    if missing:
        blockers.append("missing_canonical_branches:" + ",".join(missing))
    if branches["extra_remote_branches"]:
        blockers.append("extra_remote_branches")
    quarantine_path = _quarantine_path(common_path)
    quarantine = _quarantine_summary(quarantine_path)
    next_actions = []
    if quarantine["total"]:
        next_actions.append("review_quarantined_evidence")
    common_summary = common_ledger.summarize(common_path, limit=50)
    batch_summary = tandas.summarize_ledger(batch_path, limit=50)
    return {
        "schema": "flujo-autonomy-status-v1",
        "ts": time.strftime("%F %T"),
        "repo": branches,
        "open_prs": prs,
        "providers": provider_state,
        "ledgers": {
            "common": common_summary,
            "batches": batch_summary,
            "quarantine": quarantine,
        },
        "operational": _operational_state(
            branches, prs, common_summary, batch_summary, quarantine,
            _readme_svg_state(),
        ),
        "next_actions": next_actions,
        "batch_contract": {
            "areas": list(DEFAULT_AREAS),
            "premium_providers": list(DEFAULT_PREMIUM_PROVIDERS),
            "survival_providers": list(DEFAULT_FREE_PROVIDERS),
        },
        "ready": not blockers,
        "blockers": blockers,
    }


def build_run_options(areas=None, providers=None, **kwargs) -> RunOptions:
    selected_areas = _csv(areas, DEFAULT_AREAS)
    selected_providers = _csv(providers, DEFAULT_PREMIUM_PROVIDERS)
    unknown_areas = [area for area in selected_areas if area not in tandas.AREAS]
    if unknown_areas:
        raise ValueError("unknown_area:" + ",".join(unknown_areas))
    supported_providers = DEFAULT_PREMIUM_PROVIDERS + DEFAULT_FREE_PROVIDERS
    unknown_providers = [provider for provider in selected_providers
                         if provider not in supported_providers]
    if unknown_providers:
        raise ValueError("unsupported_run_provider:" + ",".join(unknown_providers))
    return RunOptions(
        areas=selected_areas,
        providers=selected_providers,
        **kwargs,
    )


def run_autonomy(options: RunOptions) -> dict:
    if options.executor == "mak":
        return run_on_mak(options)
    if options.executor != "local":
        return {
            "ok": False,
            "status": "bad_executor",
            "errors": ["executor must be local or mak"],
            "runs": [],
        }
    status = autonomy_status(
        common_path=options.common_ledger_path,
        batch_path=options.batch_ledger_path,
    )
    if options.require_clean and not status["ready"]:
        return {
            "ok": False,
            "status": "blocked",
            "errors": status["blockers"],
            "preflight": status,
            "runs": [],
        }

    round_id = options.round_id or time.strftime("auto-%Y%m%d-%H%M%S")
    out_dir = Path(options.out_dir) if options.out_dir else LOG_ROOT / round_id
    out_dir.mkdir(parents=True, exist_ok=True)
    runs = []
    for area in options.areas:
        for provider in options.providers:
            batch_id = "%s-%s" % (round_id, provider)
            if options.dry_run:
                brief = tandas.build_brief(
                    area,
                    batch_id,
                    providers=[provider, "ollama"],
                    include_evidence=True,
                    instruction=options.instruction,
                )
                brief_path = tandas.write_brief(brief, out_dir=str(out_dir))
                runs.append({
                    "area": area,
                    "provider": provider,
                    "status": "briefed",
                    "brief_path": brief_path,
                })
                continue
            result = tandas.run_external_batch(
                area,
                batch_id,
                provider,
                out_dir=str(out_dir),
                common_path=options.common_ledger_path,
                batch_path=options.batch_ledger_path,
                use_ollama=options.use_ollama,
                max_tokens=options.max_tokens,
                max_items=options.max_items,
                instruction=options.instruction,
            )
            runs.append({
                "area": area,
                "provider": provider,
                "status": result.get("status", ""),
                "ok": bool(result.get("ok")),
                "items": int(result.get("items", 0) or 0),
                "errors": result.get("errors", []),
                "raw_path": result.get("raw_path", ""),
            })
    return {
        "ok": all(run.get("status") == "briefed" or run.get("ok") for run in runs),
        "status": "briefed" if options.dry_run else "completed",
        "round_id": round_id,
        "out_dir": str(out_dir),
        "preflight": status,
        "runs": runs,
        "summary": {
            "common": common_ledger.summarize(options.common_ledger_path, limit=50),
            "batches": tandas.summarize_ledger(options.batch_ledger_path, limit=50),
        },
    }


def run_on_mak(options: RunOptions) -> dict:
    """Delegate the real provider/Ollama work to MAK over SSH."""
    round_id = options.round_id or time.strftime("auto-%Y%m%d-%H%M%S")
    area_csv = ",".join(options.areas)
    provider_csv = ",".join(options.providers)
    flags = [
        "PYTHONPATH=src python3 -m flujo autonomia run",
        "--executor local",
        "--areas %s" % _sh_quote(area_csv),
        "--providers %s" % _sh_quote(provider_csv),
        "--round-id %s" % _sh_quote(round_id),
        "--max-tokens %d" % int(options.max_tokens),
        "--max-items %d" % int(options.max_items),
        "--allow-dirty",
    ]
    if options.dry_run:
        flags.append("--dry-run")
    if not options.use_ollama:
        flags.append("--no-ollama")
    if options.instruction:
        flags.append("--instruction %s" % _sh_quote(options.instruction))
    command = "cd %s && %s" % (_sh_path(options.mak_repo), " ".join(flags))
    remote = _ssh_json(options.ssh_target, command)
    return {
        "ok": bool(remote.get("ok")),
        "status": remote.get("status", "remote"),
        "executor": "mak",
        "target": options.ssh_target,
        "round_id": round_id,
        "remote": remote,
    }


def _sh_quote(value: str) -> str:
    return "'" + str(value).replace("'", "'\"'\"'") + "'"


def _sh_path(value: str) -> str:
    text = str(value)
    if text == "~":
        return "$HOME"
    if text.startswith("~/"):
        return "$HOME/" + _sh_quote(text[2:])
    return _sh_quote(text)
