#!/usr/bin/env python3
"""Execute the bounded discovery/capture slice of one research job.

This runner does not call language models. It searches in Spanish and English
ASCII, keeps candidates separate from captured sources, captures only an
allowlist of official domains, and records hashes, statuses, license state and
credit estimates before allowing the job to advance to extraction.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cultura" / "mak_research"))

from research_lib import load_env, web_search  # noqa: E402
from source_pipeline import (  # noqa: E402
    SourceCorpusStore,
    canonical_url,
    capture_url,
    discover_urls,
)

try:
    from tools.interpretive_garden_workflow import create_schema
except ImportError:  # direct invocation from tools/
    from interpretive_garden_workflow import create_schema


DEFAULT_DB = Path("/home/mak/research/jardines_interpretativos/jardines_interpretativos.sqlite")
DEFAULT_OUTPUT = Path("/home/mak/research/jobs")
QUERY_TERMS = (
    "procedural plant growth modeling 3D L-system open source official documentation",
    "modelado procedural crecimiento plantas 3D L-system documentacion oficial",
)
OFFICIAL_HOSTS = {
    "algorithmicbotany.org",
    "openalea.readthedocs.io",
    "gama-platform.org",
    "p5js.org",
    "github.com",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def host_allowed(url: str) -> bool:
    host = (urlsplit(url).hostname or "").lower().rstrip(".")
    return any(host == allowed or host.endswith("." + allowed)
               for allowed in OFFICIAL_HOSTS)


def license_state(text: str) -> tuple[str, str]:
    """Return a conservative license label; absence is never treated as free."""
    folded = text.casefold()
    markers = {
        "mit": "MIT",
        "gnu general public license": "GPL",
        "apache license": "Apache",
        "creative commons": "Creative Commons",
        "open source": "open source (unspecified)",
    }
    for marker, label in markers.items():
        if marker in folded:
            return "mentioned_pending_verification", f"text marker: {label}"
    return "unknown_pending_source_review", "no license marker in bounded capture"


def _slug(value: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return text[:64] or "research-job"


def execute_job(db_path: Path, output_root: Path, job_id: int, max_sources: int = 6) -> dict:
    db_path = db_path.expanduser().resolve()
    output_root = output_root.expanduser().resolve()
    output_dir = output_root / str(job_id)
    output_dir.mkdir(parents=True, exist_ok=True)
    capture_store = SourceCorpusStore(output_dir)

    with sqlite3.connect(db_path) as conn:
        create_schema(conn)
        job = conn.execute(
            "SELECT question, domain, status, next_process FROM research_jobs WHERE id=?",
            (job_id,),
        ).fetchone()
        if not job:
            raise ValueError(f"research job not found: {job_id}")
        question, domain, status, next_process = job
        if next_process != "discover":
            raise ValueError(f"job {job_id} is at {next_process}, expected discover")

    load_env()
    discoveries: list[dict] = []
    search_errors: list[str] = []
    for query in QUERY_TERMS:
        try:
            discoveries.extend(discover_urls(
                query, lambda q, max_results=8: web_search(
                    q, max_results=max_results, errors=search_errors), max_results=8,
            ))
        except Exception as exc:  # retain a bounded audit trail and continue
            search_errors.append(f"{type(exc).__name__}:{str(exc)[:160]}")

    unique: list[dict] = []
    seen: set[str] = set()
    for row in discoveries:
        url = canonical_url(row.get("url", ""))
        if not url or url in seen:
            continue
        seen.add(url)
        row["url"] = url
        unique.append(row)
    official = [row for row in unique if host_allowed(row["url"])]
    selected = official[:max(1, int(max_sources))]

    with sqlite3.connect(db_path) as conn:
        create_schema(conn)
        for row in unique:
            conn.execute(
                """INSERT OR IGNORE INTO job_sources
                (job_id,stage,query,discovery_provider,rank,url,title,snippet,
                 capture_provider,capture_status,http_status,content_type,
                 raw_sha256,text_sha256,text_path,captured_at,license_state,
                 license_evidence,credits_estimate,notes)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (job_id, "discover", row.get("query", ""),
                 row.get("search_backend", "unknown"), int(row.get("rank", 0)),
                 row["url"], str(row.get("title", "")), str(row.get("snippet", "")),
                 "", "discovered", None, "", "", "", "", now_iso(), "", "",
                 0.0, "candidate only; not yet captured"),
            )
        conn.execute(
            "UPDATE job_steps SET status='done' WHERE job_id=? AND process_key='discover'",
            (job_id,),
        )
        conn.execute(
            "INSERT INTO audit_events(event_type,object_type,object_id,detail,created_at) VALUES (?,?,?,?,?)",
            ("discover", "research_job", job_id,
             f"{len(unique)} candidates; {len(official)} official allowlist candidates; search_errors={len(search_errors)}", now_iso()),
        )
        conn.commit()

    captured: list[dict] = []
    for row in selected:
        result = capture_url(row["url"], backend="auto")
        receipt = capture_store.record_capture(result, requested_backend="auto")
        text = str(result.get("text") or "")
        license_kind, license_evidence = license_state(text)
        capture_backend = str(result.get("backend") or "none")
        # Firecrawl and Tavily publish credit units, but this runner records an
        # estimate rather than claiming an account billing truth.
        credits = 1.0 if capture_backend == "firecrawl" else 0.0
        captured.append({
            "url": row["url"], "title": row.get("title", ""),
            "discovery_provider": row.get("search_backend", "unknown"),
            "capture_provider": capture_backend,
            "status": result.get("status", "failed"),
            "http_status": result.get("http_status"),
            "content_type": result.get("content_type", ""),
            "raw_sha256": result.get("raw_sha256", ""),
            "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "text_path": receipt.get("text_path", ""),
            "license_state": license_kind, "license_evidence": license_evidence,
            "credits_estimate": credits, "attempts": result.get("attempts", []),
            "error": result.get("error", ""),
        })
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                """UPDATE job_sources SET stage='capture', capture_provider=?,
                capture_status=?, http_status=?, content_type=?, raw_sha256=?,
                text_sha256=?, text_path=?, captured_at=?, license_state=?,
                license_evidence=?, credits_estimate=?, notes=?
                WHERE job_id=? AND url=?""",
                (capture_backend, result.get("status", "failed"), result.get("http_status"),
                 str(result.get("content_type", "")), str(result.get("raw_sha256", "")),
                 hashlib.sha256(text.encode("utf-8")).hexdigest(), receipt.get("text_path", ""),
                 now_iso(), license_kind, license_evidence, credits,
                 json.dumps({"attempts": result.get("attempts", []), "error": result.get("error", "")}, ensure_ascii=False),
                 job_id, row["url"]),
            )
            conn.commit()

    successful = [item for item in captured if item["status"] == "captured"]
    next_status = "captured" if successful else "capture_failed"
    next_process = "extract" if successful else "capture"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "UPDATE research_jobs SET status=?, next_process=? WHERE id=?",
            (next_status, next_process, job_id),
        )
        conn.execute(
            "UPDATE job_steps SET status=? WHERE job_id=? AND process_key='capture'",
            ("done" if successful else "failed", job_id),
        )
        conn.execute(
            "INSERT INTO audit_events(event_type,object_type,object_id,detail,created_at) VALUES (?,?,?,?,?)",
            ("capture", "research_job", job_id,
             f"captured={len(successful)}/{len(captured)}; estimated_credits={sum(item['credits_estimate'] for item in captured):.1f}; no_model_calls", now_iso()),
        )
        conn.commit()

    report = {
        "job_id": job_id, "question": question, "domain": domain,
        "status": next_status, "next_process": next_process,
        "queries": list(QUERY_TERMS), "candidates": len(unique),
        "official_candidates": len(official), "selected": len(selected),
        "captured": len(successful), "search_errors": search_errors,
        "sources": captured, "model_calls": 0,
        "estimated_credits": sum(item["credits_estimate"] for item in captured),
        "license_policy": "unknown is not free; human/source review remains required",
    }
    json_path = output_dir / f"{job_id:04d}-{_slug(question)}-capture.json"
    md_path = output_dir / f"{job_id:04d}-{_slug(question)}-capture.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        f"# Research job {job_id}: discovery and capture", "",
        f"- question: {question}", f"- domain: `{domain}`", f"- status: `{next_status}`",
        f"- candidates: {len(unique)} ({len(official)} official allowlist)",
        f"- captured: {len(successful)}/{len(selected)}", "- model_calls: `0`",
        f"- estimated_credits: `{report['estimated_credits']:.1f}`", "",
        "| URL | Discovery | Capture | HTTP | License state |", "|---|---|---|---:|---|",
    ]
    for item in captured:
        lines.append("| %s | %s | %s | %s | %s |" % (
            item["url"], item["discovery_provider"], item["capture_provider"],
            item["http_status"] or "", item["license_state"],
        ))
    lines += ["", "Unknown license state is intentional; it blocks publication until source review.", ""]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return {**report, "json": str(json_path), "report": str(md_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job-id", type=int, required=True)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--max-sources", type=int, default=6)
    args = parser.parse_args()
    report = execute_job(args.db, args.output_root, args.job_id, args.max_sources)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["captured"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
