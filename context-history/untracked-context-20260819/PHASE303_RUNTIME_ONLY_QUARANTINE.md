# Phase 303 — orphan platform projection quarantine

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none  
Status: `TWO_UNCONSUMED_DUPLICATES_QUARANTINED_REVERSIBLY`

## Decision

Moved, without deletion:

- `/home/mak/plataforma/memoria.py` -> `/home/mak/flujo/context/quarantine/phase303_orphan_platform_projections/memoria.py`
- `/home/mak/plataforma/vigia.py` -> `/home/mak/flujo/context/quarantine/phase303_orphan_platform_projections/vigia.py`

Evidence before move:

- `memoria.py` was a divergent stale copy; active Research uses
  `/home/mak/research/memoria.py`, a shim to
  `/home/mak/flujo/cultura/mak_research/memoria.py`.
- `vigia.py` was a divergent stale copy; active Curatoria/Vigia uses
  `/home/mak/vigia/vigia.py`, byte-identical to
  `/home/mak/flujo/cultura/mak_vigia/vigia.py`.
- No active cron, unit, import or direct path consumer referenced the two
  `/home/mak/plataforma` copies.

## Validation and rollback

```text
372a59e0cf9e670ab686b300183f8dc4b4db51ea997340b9b4d2b428c66d7da6  memoria.py
1ef53bdefefc821e7ea170ab96cebcc9115147f555dba798dd4c74188c8a7f95  vigia.py
```

Modes remained `644`; sizes remained 25,317 and 38,189 bytes. Post-move
consumer tests were run and the active crontab remained empty. Rollback is a
literal move from the quarantine paths to the original paths; no source,
database, generated output, WIN evidence or service state was deleted.

`agente_real.py` and `panel_directivo.py` remain in place because they have no
canonical pair but are plausible optional tools; they require a separate
manual-consumer decision.
