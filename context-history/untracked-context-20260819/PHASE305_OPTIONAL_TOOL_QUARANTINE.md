# Phase 305 — optional tool quarantine

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none  
Status: `BROKEN_OR_UNCONSUMED_OPTIONALS_QUARANTINED`

## Decision

Moved without deletion:

- `/home/mak/plataforma/agente_real.py` ->
  `context/quarantine/phase305_orphan_optional_tools/agente_real.py`
- `/home/mak/plataforma/panel_directivo.py` ->
  `context/quarantine/phase305_orphan_optional_tools/panel_directivo.py`

`panel_directivo.py` failed `py_compile` with
`SyntaxError: line 145, expected 'except' or 'finally' block`. It had no
canonical owner, unit, active cron or code consumer. `agente_real.py` compiled
but its canonical was explicitly removed in the recorded PR reference; the
only remaining scheduler mention was a historical backup crontab, not the
installed crontab. It requires optional `qwen_agent` and can launch other
organs, so it was not promoted as an active MAK tool.

## Validation and rollback

```text
9b566a937670bbd7609694d2e6504b603d511de4599a46c4046c8eb88a471066  agente_real.py
4a85f10015f9e25a7f6bc739e6ae81c38f6c5b2e69d71536544816ded824afc7  panel_directivo.py
```

Both retained mode `644` and original sizes (3,434 and 4,785 bytes). The
reference/entrypoint tests passed (7 tests); no active path reference remains
outside historical test/backup evidence. Rollback is a literal move back to
the original paths. No generated evidence, database, WIN file, service or
cron entry was deleted or changed.
