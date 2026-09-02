# Phase 170 — Codex quality loop fixture gate

Date: 2026-08-15
Owner: LUNA-PRINCIPAL

## Source, target and consumer

- Canonical: `/home/mak/flujo/cultura/mak_plataforma/calidad_loop.py`
- Runtime: `/home/mak/plataforma/calidad_loop.py`
- Inputs: Codex `jobs.jsonl`, optional delivery state and backlog text
- Output: sibling `CALIDAD_LOOP.md`
- Consumer: local operator quality/rate report

## Result

Both source/runtime files compiled. A temporary fixture containing ready,
blocked, review and failed jobs plus dated/undated backlog entries was processed
through both CLIs. Both returned exit `0`, wrote identical reports and exposed
the same metrics: four jobs, one guard block, two backlog items and fourteen
days maximum age. No real jobs, delivery state, backlog, generated pieces,
providers or services were touched.

## Decision

The quality loop is reconciled as an exact data-path-compatible projection.
Keep its report output behind the fixture gate; the next Codex step is the
local `testear.py` validation path, not worker execution.
