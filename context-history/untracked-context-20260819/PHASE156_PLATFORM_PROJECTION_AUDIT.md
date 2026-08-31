# Phase 156 — MAK platform projection audit

Date: 2026-08-15
Owner: LUNA-PRINCIPAL

## Scope

Physical comparison started at `/home/mak/*` and narrowed to the active
projection pair `/home/mak/plataforma` and
`/home/mak/flujo/cultura/mak_plataforma`. Runtime state, `.venv`, logs,
rollback archives and generated queues are excluded from code promotion.

## Result

- 46 code/tree files are byte-identical between the two surfaces.
- 15 code files differ; most root files are already compatibility wrappers or
  intentionally divergent runtime projections. They require per-file gates,
  not bulk replacement.
- The root-only remainder is dominated by `.venv`, state, logs, locks and
  rollback evidence; it is not a migration target.
- The active crontab template points `MAK-MATERIAL` at
  `/home/mak/plataforma/material.py`, while the installed crontab keeps that
  line paused. No cron process is enabled by this audit.

## Decision

Select `material.py` as the next bounded consolidation slice because it has a
real queue consumer (`trabajo.py`), a read-only contract (`--contar`) and a
reversible exact source projection. Preserve the root copy in quarantine and
replace only the runtime projection with a wrapper to the canonical source.
Do not touch queue data, cron installation, `trabajo.py`, rollback archives or
the other projection files in this phase.

## Risks and next action

The canonical script uses absolute `~/curatoria` and `~/plataforma` paths and
its normal mode writes the queue. Validation must therefore use `--contar` and
compare queue metadata before/after. If the wrapper does not preserve the
read-only output, restore the quarantined file. Next: apply and validate the
`material.py` wrapper in foreground, then record the result in the operational
handoff.
