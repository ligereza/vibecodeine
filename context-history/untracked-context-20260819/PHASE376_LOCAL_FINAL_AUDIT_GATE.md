# Phase 376 — local MAK final audit gate

Date: 2026-08-15 (America/Santiago)

## Foreground results

```text
HEALTH_RC=0
DOCTOR_RC=0
PIP_CHECK_RC=0
RD_DATOS_INTEGRITY=ok
RD_DATOS_ROWS=0
CRON_ACTIVE=0
ACTIVE_AST_FILES=371
ACTIVE_AST_PASS=371
ACTIVE_AST_FAIL=0
```

The base FLUJO health and doctor checks pass, the canonical venv has no broken
requirements, `rd_datos.db` remains integrity-ok and empty with its known
hash, and no active cron entry or MAK service was observed.

## Generated-output exception

The first broad AST scan covered 484 Python files and returned exit 1 because
seven malformed files live under the protected generated-output surface
`/home/mak/codex/piezas`. They are not active source consumers; they remain
preserved as generated products and were not repaired or deleted. The refined
active-source scan excluded generated `piezas`, caches, rollback and venv
trees and passed 371/371 files.

This is a classified audit exception, not a claim that every generated
historical artifact is executable.

## Disposition

`LOCAL_CORE_HEALTH_PASS; ACTIVE_SOURCE_AST_PASS; GENERATED_OUTPUT_EXCEPTION`

External providers, live mutators, automation enablement, real field ingest,
renderers, Git and WIN remain outside this foreground audit.

## Rollback and boundary

No source, data, credential, generated product, database, service, Git, Docker
or WIN state changed. No rollback is required.
