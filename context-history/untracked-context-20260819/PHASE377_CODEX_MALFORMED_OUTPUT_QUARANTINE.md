# Phase 377 — malformed generated Codex output quarantine

Date: 2026-08-15 (America/Santiago)

## Finding

Seven files under `/home/mak/codex/piezas` failed AST because they were
truncated, fenced Markdown or assistant refusal text rather than executable
Python. A bounded consumer scan found zero active references to their exact
filenames.

## Action

Moved exactly those seven files, without copying or editing them, to:

`/home/mak/flujo/context/quarantine/phase376_malformed_generated_codex/`

All seven retained mode `0644`, byte size and SHA-256. The inverse operation
is a direct move back to `/home/mak/codex/piezas/` using the recorded basename.

## Validation

```text
CODEX_ACTIVE_GENERATED_PY_AFTER=106
CODEX_ACTIVE_GENERATED_AST_FAIL=0
CODEX_MALFORMED_QUARANTINE=7
POST_MOVE_AST_RC=0
```

The active generated surface now parses; the quarantined products remain
recoverable evidence. No source, database, credential, service, provider, Git
or WIN state changed.

Disposition: `MALFORMED_GENERATED_OUTPUT_QUARANTINED; REVERSIBLE`.
