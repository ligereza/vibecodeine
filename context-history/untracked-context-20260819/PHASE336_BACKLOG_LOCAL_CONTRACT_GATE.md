# Phase 336 — backlog local contract gate

Date: 2026-08-15 (America/Santiago)
Scope: pure and temporary-only behavior in
`/home/mak/flujo/cultura/mak_plataforma/backlog.py`.

## Foreground validation

Direct fixtures passed normalization and accent folding, deterministic hashes,
Spanish backlog-section parsing, provenance classification, corrupt-JSONL
skipping, append, score-based pop and status marking:

```text
BACKLOG_DIRECT_FIXTURE=PASS
TEMP_ONLY_WRITES=True PROVIDER_CALLS=0
```

The temporary backlog was the only write target. No worker, provider, queue,
service or active MAK backlog was touched. The formal pytest module was not
run because the venv lacks pytest; the direct contract calls covered the
selected local surface.

## Disposition

`VERIFIED_DIRECT_FIXTURE; BACKLOG_WRITERS_TEMPORARY_ONLY`.

The backlog utility is locally coherent for its pure parser and isolated file
operations. Live `cosechar`, worker and queue execution remain separately
gated.

