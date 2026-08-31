# Phase 166 — curatoria triangulation fixture gate

Date: 2026-08-15
Owner: LUNA-PRINCIPAL

## Source, target and consumer

- Canonical: `/home/mak/flujo/cultura/mak_curatoria/triangular.py`
- Runtime: `/home/mak/curatoria/triangular.py`
- Input: curatoria `fichas.jsonl`
- Output: curatoria `triangulacion.jsonl`
- Downstream role: creates research questions; it does not dispatch them

## Result

Both source/runtime files compiled. An isolated bilingual-friendly fixture
containing one known producer, one discovery candidate, malformed input and an
ignored non-RD row produced two identical outputs with exit 0: one
`confirmar`, one `descubrir`, preserving the headliner and the source request.
The real fichas and triangulation queue were not touched; no research/provider
call or persistent process occurred.

## Decision

Keep the exact copies data-bound to their respective curatoria roots. Do not
wrap them until a data-root parameter is explicit; the queue is a local
derived artifact and the downstream dispatch remains a separate authority
gate.
