# Phase 363 — Research projection parity gate

Date: 2026-08-15 (America/Santiago)

## Scope

Reconciled the Phase 361 credential-owner change between the canonical
projection and the live Research root. The five paired files were checked
locally; the remote/SSH mirror checker was deliberately not run.

## Results

```text
RESEARCH_PROJECTION_PARITY=PASS files=5
RESEARCH_ACTIVE_N8N_REFS=ABSENT
PYCOMPILE_RC=0
BASH_RC=0
STATIC_RC=0
UNIT_VERIFY_RC=0
```

Paired files:

- `research_lib.py`
- `interfaz.py`
- `watchdog.sh`
- `interfaz.service`
- `cola.service`

Both `/home/mak/flujo/cultura/mak_research` and `/home/mak/research` now use
`research/research.env` and have identical SHA-256 content for these files.

## Disposition

`RESEARCH_OWNER_PARITY_VERIFIED; N8N_FALLBACK_REMOVED`

The source/projection relationship is coherent for the changed credential
boundary. No service was started and no provider was called.

## Rollback and boundary

Rollback is the inverse substitution in the five paired files. Credential
files, Research data, generated reports, WIN, Git, Docker and external state
were not changed.
