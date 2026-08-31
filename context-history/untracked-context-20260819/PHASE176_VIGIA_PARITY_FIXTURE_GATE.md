# Phase 176 — vigia parity and fixture gate

Date: 2026-08-15
Owner: LUNA-PRINCIPAL

## Source, target and consumer

- Canonical: `/home/mak/flujo/cultura/mak_vigia/vigia.py`
- Runtime: `/home/mak/vigia/vigia.py`
- Guard: `/home/mak/vigia/vigia_guardia.sh`
- Consumer: paused/declared `MAK-VIGIA` hourly guard
- State: runtime `/home/mak/vigia/estado`, protected from test writes

## Action

The runtime Python had only one stale documentation reference (`CLAUDE.md`)
relative to the canonical source. It was corrected to the repository data
policy; no behavior or state path changed. Both Python files now hash equally.

## Foreground result

Both Python files compiled and the guard shell passed `bash -n`. With a local
HTTP-response fixture and separate temporary state directories, source and
runtime runs matched exactly: first pass found two new listings; the second
pass found zero new listings and preserved identical `vistos.jsonl` and
`ultimo.json` state. No network, ntfy, ledger mutation, real state, cron,
service or persistent process was used.

## Decision

Vigia is parity-reconciled but intentionally remains a data/state-owning
runtime, not a wrapper. Its guard remains paused and its live network contract
is still a separate operational gate.
