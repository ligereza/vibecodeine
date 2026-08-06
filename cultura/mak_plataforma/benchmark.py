#!/usr/bin/env python3
"""Benchmark estructural del corpus de research de MAK.

No decide si una afirmacion es verdadera. Mide si el producto declarado
coincide con su forma, si conserva su pareja JSON/Markdown y si un ensayo deja
las huellas minimas que lo separan de un informe disfrazado.
"""
from __future__ import annotations

import argparse
import json
import re
import time
from collections import Counter
from pathlib import Path

try:
    from .research_router import route_research_task
except ImportError:
    from research_router import route_research_task


FORMATS = {"informe", "ensayo", "revision", "exposicion", "curatoria"}
RESEARCH_DIRS = {"informes", "paneles", "cadenas", "refutaciones",
                 "correlaciones", "grafos", "memoria"}


def _read_json(path):
    try:
        with path.open(encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else None
    except (OSError, ValueError):
        return None


def _essay_gaps(text):
    gaps = []
    if len(re.findall(r"^#{2,3} +\S", text, re.M)) < 3:
        gaps.append("essay_parts")
    if len(re.findall(r"^\s*\|?[-:| ]{3,}$", text, re.M)) < 1:
        gaps.append("essay_table")
    if len(set(re.findall(r"\b(?:1\d{3}|20[0-2]\d)\b", text))) < 2:
        gaps.append("essay_chronology")
    if "http" not in text:
        gaps.append("essay_sources")
    return gaps


def inspect_corpus(root, since=0):
    root = Path(root)
    totals = Counter()
    issues = []
    products = []
    for folder in sorted(root.iterdir()) if root.exists() else []:
        if not folder.is_dir() or folder.name not in RESEARCH_DIRS:
            continue
        for path in sorted(folder.glob("*.json")):
            if path.name.endswith(".conceptos.json") or path.name == "grafo_cache.json":
                continue
            try:
                if path.stat().st_mtime <= since:
                    continue
            except OSError:
                continue
            totals["json"] += 1
            payload = _read_json(path)
            if payload is None:
                issues.append({"kind": "invalid_json", "path": str(path)})
                continue
            formato = payload.get("formato", "")
            totals["format_%s" % (formato or "missing")] += 1
            product = {"path": str(path), "folder": folder.name,
                       "format": formato or None}
            products.append(product)
            if formato not in FORMATS:
                issues.append({"kind": "missing_or_unknown_format",
                               "path": str(path), "format": formato or None})
            elif payload.get("topic"):
                route = route_research_task("multiplicar", payload["topic"])
                if route.formato != formato:
                    issues.append({"kind": "route_format_mismatch",
                                   "path": str(path), "declared": formato,
                                   "expected": route.formato,
                                   "topic": payload.get("topic", ""),
                                   "reason": route.reason})
            markdown = path.with_suffix(".md")
            if not markdown.exists():
                totals["missing_markdown"] += 1
                issues.append({"kind": "missing_markdown", "path": str(path)})
            elif formato == "ensayo":
                gaps = _essay_gaps(markdown.read_text(
                    encoding="utf-8", errors="replace"))
                if gaps:
                    totals["essay_structural_fail"] += 1
                    issues.append({"kind": "essay_structural_gaps",
                                   "path": str(path), "gaps": gaps})
    totals["products"] = len(products)
    totals["issues"] = len(issues)
    totals["structural_pass"] = sum(
        1 for product in products
        if not any(issue.get("path") == product["path"] for issue in issues))
    for issue in issues:
        issue["next_action"] = _next_action(issue)
    return {"schema": "mak-corpus-benchmark-v1", "root": str(root),
            "totals": dict(totals), "products": products, "issues": issues,
            "queue": issues}


def _next_action(issue):
    kind = issue.get("kind")
    if kind == "route_format_mismatch":
        if issue.get("declared") == "ensayo" and issue.get("expected") == "informe":
            return "review_then_relabel_as_informe"
        if issue.get("declared") == "informe" and issue.get("expected") == "ensayo":
            return "review_then_rebuild_or_keep_informe"
        return "review_route"
    if kind == "essay_structural_gaps":
        return "review_then_repair_or_archive"
    if kind == "missing_or_unknown_format":
        return "legacy_review"
    if kind == "missing_markdown":
        return "locate_or_quarantine_pair"
    return "manual_review"


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--out", default="")
    parser.add_argument("--since", type=float, default=0,
                        help="epoch: inspect only products newer than this")
    parser.add_argument("--check", action="store_true",
                        help="fail when the selected corpus has structural issues")
    args = parser.parse_args(argv)
    result = inspect_corpus(args.root, since=args.since)
    text = json.dumps(result, ensure_ascii=True, indent=2)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 2 if args.check and result["totals"].get("issues", 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
