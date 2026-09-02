# Phase 168 — Codex semantic engine fixture gate

Date: 2026-08-15
Owner: LUNA-PRINCIPAL

## Source, target and consumer

- Canonical package: `/home/mak/flujo/cultura/mak_codex/motor_semantico`
- Runtime package: `/home/mak/codex/motor_semantico`
- Consumer: Codex icon generation and SVG review workflows
- Interface: `compilador.py spec.json output.svg`

## Result

All source/runtime semantic-engine Python files compiled. The canonical and
runtime CLI were run independently against the same temporary semantic spec;
both returned exit `0`, emitted the same success contract and produced
byte-identical SVG output (`3802` bytes, `viewBox="0 0 120 120"`). No real Codex
piece, provider, worker, service or persistent process was touched.

## Decision

The exact engine package is functionally reconciled. Keep `piezas/` and their
manifests as historical/generated evidence; do not collapse them into source
code or delete them. Next inspect the Codex job/worker boundary, where provider
calls and writes require fixture isolation.
