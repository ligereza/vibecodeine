# Phase 164 — research statistics fixture gate

Date: 2026-08-15
Owner: LUNA-PRINCIPAL

## Source, target and consumer

- Source: `/home/mak/flujo/cultura/mak_research/estadisticas.py`
- Runtime: `/home/mak/research/estadisticas.py`
- Inputs: JSON metadata under the research `informes` and `paneles` folders
- Output: `USO.md`, consumed as human/operator usage summary

## Result

The source and runtime files are byte-identical and both compiled. A temporary
fixture with provider calls, an error, a query and an advanced Tavily finding
was processed independently by each module. Both returned exit `0` and wrote
identical output: local calls `2`, one error, basic searches `1`, advanced
searches `1`, estimated credits `3` and average duration `1200 ms`.

The real `/home/mak/research/USO.md` and its source counterpart were not
rewritten. No provider, network, service or persistent process was used.

## Decision

Keep the exact data-bound copies separate: their `ROOT` is intentionally the
department that owns their input/output data. Do not convert this family to a
canonical wrapper without first adding an explicit data-root contract.
