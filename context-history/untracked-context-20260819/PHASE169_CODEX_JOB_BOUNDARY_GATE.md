# Phase 169 — Codex job boundary gate

Date: 2026-08-15
Owner: LUNA-PRINCIPAL

## Source, target and consumer

- Canonical library: `/home/mak/flujo/cultura/mak_codex/codex_lib.py`
- Runtime library: `/home/mak/codex/codex_lib.py` (compatibility projection)
- Canonical worker: `/home/mak/flujo/cultura/mak_codex/worker_codex.py`
- Runtime worker: `/home/mak/codex/worker_codex.py` (compatibility projection)
- Consumer: Codex API/service job dispatch

## Result

All four files compiled. Source/runtime library imports exposed the same coder
chain parsing contract, including invalid-key fallback to the complete default
chain. Source/runtime workers were imported with dispatch disabled and their
safe boundaries were exercised: unknown mode returns a structured failure and
an out-of-scope path is rejected before subprocess/provider work. No LLM,
Ollama, NIM, Watson, job subprocess, lock, event, service or persistent
process was started.

## Decision

The runtime Codex library/worker projections are already canonicalized. Keep
provider-backed `run_pedido()` execution gated; its normal path writes jobs and
pieces and acquires GPU/locks. Next inspect the local non-provider Codex
validation path (`calidad_loop.py` or `testear.py`) with a fixture.
