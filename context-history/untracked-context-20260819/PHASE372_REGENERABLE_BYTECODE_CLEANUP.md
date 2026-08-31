# Phase 372 — regenerable bytecode cleanup

Date: 2026-08-15 (America/Santiago)

## Scope

Removed only regular `*.pyc` files from these explicit MAK roots:

- `/home/mak/flujo/src`
- `/home/mak/flujo/cultura`
- `/home/mak/plataforma`
- `/home/mak/research`
- `/home/mak/curatoria`
- `/home/mak/codex`
- `/home/mak/vigia`
- `/home/mak/lenguaje`

The preflight found 6,060 regenerable bytecode files. The explicit roots
included package-environment caches under `plataforma` and `research`; those
caches were removed as bytecode only, while package sources, metadata and
virtual environments remained intact. No `.py`, data, database, credential,
generated product, WIN or Git file was targeted.

## Validation

```text
PYC_BEFORE=6060
PYC_AFTER=0
PIP_CHECK_RC=0
HEALTH_RC=0
CRON_ACTIVE=0
```

`__pycache__` directories remain as empty/recreatable directories where the
interpreter had created them; no bytecode remains in the listed roots.

## Disposition

`REGENERABLE_RESIDUE_REMOVED; SOURCES_AND_DATA_PRESERVED`

The cleanup is reversible by normal Python imports/compilation. No package
installation or service start was needed.
