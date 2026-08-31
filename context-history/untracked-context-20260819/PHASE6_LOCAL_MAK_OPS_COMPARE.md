# Phase 6 Local MAK Ops Comparison

## Objective

Compare the active local `tools/mak_ops` surface with the historical local WIN snapshot and make a conservative no-change decision.

## Scope

- Active: `/home/mak/flujo/tools/mak_ops`
- Historical snapshot: `/home/mak/WIN/flujo/tools/mak_ops`
- Regular files only, relative depth 1–2.
- Excluded `__pycache__`, `*.pyc`, logs, databases, and named secret files.
- Consumers limited to `check_mak_mirror.py` and `run_conductor_worker.py`; only AST parsing and `--help` were allowed.
- No SSH, remote address probes, Git, known_hosts changes, copies, merges, worker starts, or service starts.

## Method

Used Python `pathlib`, native `hashlib.sha256`, and a standard-library inventory. Text diffs were run only for the four small differing files. Statuses are `same`, `different`, `active_only`, or `win_only`. CSV was written with Python's standard `csv` module and then validated.

## File-set summary

- Active files included: 12
- WIN files included: 15
- Union: 15
- Same: 8
- Different: 4
- Active-only: 0
- WIN-only: 3

Excluded bytecode inventory was present under `__pycache__` and was not compared.

## Hash comparison

The complete row-level result, hashes, statuses, consumers, verification, decisions, and notes is in `PHASE6_LOCAL_MAK_OPS_COMPARE.csv`. The four text differentials are:

- `director_snapshot.py`: active prompt no longer references `context/LAST_HANDOFF.md`.
- `mak-conductor-shadow.service`: content equivalent under a small-text diff except line endings.
- `mak-conductor-shadow.timer`: content equivalent under a small-text diff except line endings.
- `repair_mak_sync.py`: materially different historical repair implementation; the WIN variant contains remote/Git repair behavior and was not executed.

WIN-only files are `build_director_context.py`, `migrate_unified_knowledge.py`, and `sync_mak_safe.py`.

## Consumer verification

- `check_mak_mirror.py`: AST parse passed; `/home/mak/venvs/flujo/bin/python ... --help` exited 0 and stopped at argparse before its SSH code.
- `run_conductor_worker.py`: AST parse passed; `/home/mak/venvs/flujo/bin/python ... --help` exited 0 and stopped at argparse before worker construction or execution.
- No services, timers, workers, subprocess probes, or remote checks were started.

## No-change decision

Decision: `no_change` for every CSV route. The WIN tree is historical evidence, not a live Windows host or an integration target. No row has sufficient owner/consumer/dependency authority for promotion, and the requested phase explicitly prohibits copying or merging. The active consumer contracts remain unchanged.

## Risks

- `repair_mak_sync.py` has a material historical divergence and includes prohibited remote/Git behavior in the WIN variant; it requires a separately authorized owner and contract review.
- Systemd unit hashes differ because of line endings; no semantic normalization or activation was attempted.
- Hash equality does not prove runtime equivalence.
- The active mirror checker still contains a remote SSH path, but `--help` validation did not reach it; this phase did not invoke it.

## Verification log

- Read `/home/mak/flujo/agents.md` and `/home/mak/flujo/context/LAST_HANDOFF.md` first.
- Local inventory/hash command: exit 0; 12 active, 15 WIN, 15 union, 8 same, 4 different, 0 active-only, 3 WIN-only.
- AST parse with `PYTHONDONTWRITEBYTECODE=1`: exit 0 for both relevant active Python consumers.
- `check_mak_mirror.py --help`: exit 0.
- `run_conductor_worker.py --help`: exit 0.
- Small-text `diff -u`: exit 1 for four expected content-difference comparisons; output inspected only, no files changed.
- CSV validation: performed with Python standard library; header exact and row counts recorded below.
- No SSH, Git, known_hosts, copy, merge, or service/worker action executed.

## Next action

Keep this comparison as evidence and leave all routes `no_change`. If integration is later requested, assign an explicit owner and dependency contract for each divergent route, beginning with `repair_mak_sync.py`; do not promote the WIN snapshot by default.

## Last checkpoint

2026-08-14 America/Santiago — LUNA-06 completed the bounded local comparison and consumer checks with no source changes.
