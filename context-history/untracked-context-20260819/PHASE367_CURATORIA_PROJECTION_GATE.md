# Phase 367 — Curatoria projection/consumer gate

Date: 2026-08-15 (America/Santiago)

## Scope

Audited the declared Curatoria mirror set: `percepcion.py`,
`extraccion_db.py` and `curatoria_guardia.sh`.

## Results

```text
CURATORIA_CANONICAL_IMPORTS=PASS
CURATORIA_LIVE_WRAPPER_IMPORTS=PASS
IMPORT_RC=0
WRAPPER_RC=0
PYCOMPILE_RC=0
BASH_RC=0
```

The two Python files at `/home/mak/curatoria` are intentional compatibility
wrappers that load the canonical implementations from
`/home/mak/flujo/cultura/mak_curatoria`. The guard shell file is an exact
paired projection. No perception run, database extraction, worker, provider
or service was started.

## Disposition

`CURATORIA_OWNER_PROJECTION_VERIFIED; WRAPPERS_INTENTIONAL`

No merge or deletion is justified for this family. The root wrappers provide
the deployed import path while the canonical package owns behavior.

## Rollback and boundary

No source, Curatoria database, ledger, generated report, service state, Git,
Docker or WIN evidence changed. No rollback is required. Real perception and
extraction remain bounded mutator/external gates.
