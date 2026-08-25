#!/usr/bin/env python3
"""Emit the bounded bootstrap packet required before an agent edits MAK.

This command is intentionally read-only. It does not decide the task, mutate
state, or replace the operational handoff. It makes the coordinator pass a
small, hash-pinned current packet to a worker instead of relying on a worker
to discover a long append-only handoff by itself.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


SCHEMA = "mak-agent-bootstrap-v1"
CURRENT_PACKET_START = "## Agent bootstrap — CURRENT"
REQUIRED_FILES = (
    "agents.md",
    "docs/MAK_CURRENT_STATE.md",
    "context/LAST_HANDOFF.md",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def current_packet(handoff: str) -> str:
    lines = handoff.splitlines()
    try:
        start = next(index for index, line in enumerate(lines) if line.strip().startswith(CURRENT_PACKET_START))
    except StopIteration as exc:
        raise ValueError("handoff_missing_current_agent_bootstrap") from exc
    selected: list[str] = []
    for line in lines[start:]:
        if selected and line.startswith("## "):
            break
        selected.append(line)
    return "\n".join(selected).strip()


def build_packet(root: Path, task: str, write_set: list[str]) -> str:
    paths = {relative: root / relative for relative in REQUIRED_FILES}
    missing = [relative for relative, path in paths.items() if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing_required_context:" + ",".join(missing))
    handoff_text = paths["context/LAST_HANDOFF.md"].read_text(encoding="utf-8")
    packet = current_packet(handoff_text)
    lines = [
        f"schema={SCHEMA}",
        f"root={root}",
        f"task={task or '<unspecified>'}",
        "required_read_order=agents.md -> docs/MAK_CURRENT_STATE.md -> context/LAST_HANDOFF.md",
        "write_set=" + (";".join(write_set) if write_set else "<must be supplied by coordinator>"),
        "context_sha256:",
    ]
    for relative, path in paths.items():
        lines.append(f"  {relative}={sha256(path)}")
    lines.extend([
        "",
        "--- CURRENT PACKET (operative; historical sections are excluded) ---",
        packet,
        "--- END CURRENT PACKET ---",
        "bootstrap_requirements=read_required_files;confirm_write_set;report_commands_exit_codes_and_observed_results",
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--task", default="")
    parser.add_argument("--write-set", action="append", default=[])
    args = parser.parse_args()
    print(build_packet(args.root.resolve(), args.task, args.write_set), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
