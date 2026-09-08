#!/usr/bin/env python3
"""Compile local official receipts; fetch only with explicit ``--network``."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
MOTOR_SRC = ROOT / "flujo" / "src"
if MOTOR_SRC.is_dir() and str(MOTOR_SRC) not in sys.path:
    sys.path.insert(0, str(MOTOR_SRC))

from tools.research_source_capture import capture_one  # noqa: E402
from cultura.mak_research.source_pipeline import canonical_url  # noqa: E402
from flujo.knowledge.opportunity_validity_capture import (  # noqa: E402
    EXPECTED_URLS,
    build_opportunity_validity_capture,
)


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


VIGIA_RECEIPT_SCHEMA = "mak-vigia-capture-receipts-v1"


def _receipt_rows(path: Path, *, capture_root: Path | None = None) -> list[dict[str, Any]]:
    value = _load_json(path)
    if isinstance(value, dict) and value.get("schema") == VIGIA_RECEIPT_SCHEMA:
        if capture_root is None:
            raise ValueError("vigia_receipt_requires_capture_root")
        raw_rows = value.get("receipts")
        if not isinstance(raw_rows, list):
            raise ValueError("vigia_receipt_rows_missing")
        hydrated: list[dict[str, Any]] = []
        role_by_url = {canonical_url(url): role for role, url in EXPECTED_URLS.items()}
        for index, row in enumerate(raw_rows):
            if not isinstance(row, dict):
                raise ValueError(f"vigia_receipt[{index}]_not_object")
            url = canonical_url(str(row.get("url") or ""))
            role = role_by_url.get(url)
            if not role:
                raise ValueError(f"vigia_receipt[{index}]_url_not_declared_official")
            capture_id = str(row.get("capture_id") or "")
            if row.get("status") == "captured" and not capture_id:
                raise ValueError(f"vigia_receipt[{index}]_capture_id_missing")
            if capture_id:
                enriched = _stored_receipt(capture_root, capture_id, role, url)
                enriched["capture_id"] = capture_id
                hydrated.append(enriched)
            else:
                # Preserve a failed/abstained receipt as an explicit failed
                # validity input instead of silently dropping the gap.
                hydrated.append({
                    "role": role, "requested_url": url, "final_url": url,
                    "status": str(row.get("status") or "unknown"),
                    "http_status": None, "raw_sha256": "", "text_sha256": "",
                    "text": "", "retrieved_at": "", "error": str(row.get("error") or ""),
                })
        return hydrated
    rows = value if isinstance(value, list) else value.get("receipts", []) if isinstance(value, dict) and "receipts" in value else [value]
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError(f"invalid_receipt_file:{path}")
    return rows


def _stored_receipt(root: Path, capture_id: str, role: str, requested_url: str) -> dict[str, Any]:
    db_path = root / "sources.sqlite"
    uri = f"file:{db_path.resolve()}?mode=ro"
    with sqlite3.connect(uri, uri=True) as conn:
        row = conn.execute(
            "SELECT canonical_url,status,http_status,raw_sha256,text_sha256,text_path,retrieved_at,error FROM source_captures WHERE capture_id=?",
            (capture_id,),
        ).fetchone()
    if row is None:
        raise ValueError("capture_receipt_not_found")
    text = Path(row[5]).read_text(encoding="utf-8") if row[5] else ""
    return {
        "role": role,
        "requested_url": requested_url,
        "final_url": row[0],
        "status": row[1],
        "http_status": row[2],
        "raw_sha256": row[3],
        "text_sha256": row[4],
        "text": text,
        "retrieved_at": row[6],
        "error": row[7],
    }


def _latest_stored_receipt(root: Path, role: str, requested_url: str) -> dict[str, Any]:
    db_path = root / "sources.sqlite"
    uri = f"file:{db_path.resolve()}?mode=ro"
    with sqlite3.connect(uri, uri=True) as conn:
        row = conn.execute(
            "SELECT capture_id FROM source_captures WHERE canonical_url=? ORDER BY retrieved_at DESC, capture_id DESC LIMIT 1",
            (requested_url,),
        ).fetchone()
    if row is None:
        raise ValueError(f"stored_capture_missing:{role}")
    return _stored_receipt(root, str(row[0]), role, requested_url)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frontier", type=Path, required=True)
    parser.add_argument("--opportunity-id", required=True)
    parser.add_argument("--receipt", type=Path, action="append", default=[])
    parser.add_argument("--capture-root", type=Path, default=Path("data/source_corpus"))
    parser.add_argument("--network", action="store_true", help="capture exactly the three declared official URLs")
    parser.add_argument("--reuse-capture-root", action="store_true", help="read the latest three declared captures without network")
    parser.add_argument("--backend", choices=("auto", "firecrawl", "crawl4ai", "urllib"), default="auto")
    parser.add_argument("--timeout", type=int, default=45)
    parser.add_argument("--now", default=None, help="timezone-aware ISO-8601 evaluation time")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        frontier = _load_json(args.frontier)
        receipts: list[dict[str, Any]] = []
        for path in args.receipt:
            receipts.extend(_receipt_rows(path, capture_root=args.capture_root))
        network_called = False
        if args.reuse_capture_root:
            if receipts or args.network:
                raise ValueError("reuse_capture_root_is_mutually_exclusive")
            receipts = [
                _latest_stored_receipt(args.capture_root, role, url)
                for role, url in EXPECTED_URLS.items()
            ]
        if args.network:
            if receipts:
                raise ValueError("network_and_local_receipts_are_mutually_exclusive")
            network_called = True
            for role, url in EXPECTED_URLS.items():
                captured = capture_one(
                    url, root=args.capture_root, backend=args.backend,
                    record=True, timeout=args.timeout,
                )
                receipt = captured.get("receipt") if isinstance(captured, dict) else None
                if not isinstance(receipt, dict) or not receipt.get("capture_id"):
                    raise ValueError(f"capture_failed:{role}")
                row = _stored_receipt(args.capture_root, str(receipt["capture_id"]), role, url)
                receipts.append(row)
        if len(receipts) > len(EXPECTED_URLS):
            raise ValueError("receipt_count_exceeds_bound")
        now = args.now or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        result = build_opportunity_validity_capture(
            frontier, receipts, opportunity_id=args.opportunity_id, now=now,
        )
        result["control"]["network_called"] = network_called
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
    except (OSError, ValueError, json.JSONDecodeError, sqlite3.Error) as exc:
        print(json.dumps({"schema": "mak-opportunity-validity-capture-v1", "valid": False, "error": str(exc)}, sort_keys=True))
        return 2
    if args.output:
        print(json.dumps({
            "schema": result["schema"], "valid": result["valid"],
            "validity": result["validity"], "errors": result["errors"],
            "output": str(args.output),
        }, ensure_ascii=False, sort_keys=True))
    else:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
