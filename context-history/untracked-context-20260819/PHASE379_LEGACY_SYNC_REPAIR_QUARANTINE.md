# Phase 379 — legacy sync repair quarantine

Date: 2026-08-15 (America/Santiago)

## Finding

`/home/mak/flujo/tools/mak_ops/repair_mak_sync.py` is a historical repair
script that can use SSH, create a `MAK-REPO-SYNC` cron entry, checkout/reset
Git and copy four projections. It had zero active references and contradicted
the current no-SSH/no-cron/no-destructive-sync architecture.

## Action

Moved it reversibly to:

`/home/mak/flujo/context/quarantine/phase379_legacy_sync_repair/repair_mak_sync.py`

The file retained 5,424 bytes, mode `0644` and SHA-256
`1eb2a1d794f95322984983811602a60d5be9853594ac4c743aa2367c43c45615`.
Thirteen regenerable `*.pyc` files in `tools/mak_ops/__pycache__` were also
removed; the active tool source remained intact.

## Validation

```text
PYCOMPILE_RC=0
ACTIVE_REFERENCE_FILES=0
ORIGINAL_ABSENT=PASS
QUARANTINE_PRESENT=PASS
MAK_OPS_PYC_BEFORE=13 MAK_OPS_PYC_AFTER=0
MAK_OPS_ACTIVE_PY=9 AST_FAIL=0
ACTIVE_REPAIR_REFERENCE_COUNT=0
CRON_ACTIVE=0
```

Disposition: `LEGACY_DESTRUCTIVE_SYNC_QUARANTINED; REVERSIBLE`.

No SSH, Git, cron, service, provider, data, credential, generated product or
WIN action occurred. The read-only `check_mak_mirror.py` remains preserved as
external diagnostic evidence and was not executed.
