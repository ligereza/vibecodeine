# Phase 219 — empty staging directory quarantine

Date: 2026-08-15 (America/Santiago)

## Candidate gate

Candidate: `/home/mak/curatoria_encolado`.

- Target was a directory, mode `0755`, size `4096` bytes.
- It contained zero entries.
- Bounded consumer search across canonical source, culture, units and deploy
  scripts found no reference.
- It was not a database, source, output, credential, recovery surface, WIN
  path or evidence file.
- Destination did not exist before the move.

## Action

Moved the empty directory, without contents, to:

`/home/mak/flujo/context/quarantine/phase219_empty_staging/curatoria_encolado`

Command exit: `0`.

## Foreground validation

- Original path present: `no`.
- Quarantine path present: `yes`.
- Quarantine entries: `0`.
- Directory mode/metadata: `drwxr-xr-x 0755`, size `4096` bytes.

Rollback command, not executed:

```bash
mv /home/mak/flujo/context/quarantine/phase219_empty_staging/curatoria_encolado /home/mak/curatoria_encolado
```

## Decision

`JUNK_CONFIRMED`: yes, limited to this exact empty staging directory. No rule
is inferred for other empty directories. Protected surfaces and all files were
left untouched.

## Next concrete action

Run post-quarantine health/import/route checks and update the objective
snapshot. Keep the legacy platform UI preserved until its evidence status is
resolved; do not broaden cleanup.

