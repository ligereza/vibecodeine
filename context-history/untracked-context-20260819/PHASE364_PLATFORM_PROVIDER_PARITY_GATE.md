# Phase 364 — platform provider parity gate

Date: 2026-08-15 (America/Santiago)

## Scope

Reconciled the platform provider projection after Phase 361. The canonical
`cultura/mak_plataforma/providers.py` and live `/home/mak/plataforma/providers.py`
were checked for exact content and credential fallback ownership.

## Results

```text
PLATFORM_PROVIDER_PARITY=PASS
PLATFORM_N8N_FALLBACK=ABSENT
PYCOMPILE_RC=0
STATIC_RC=0
```

The platform provider now searches the explicit `RESEARCH_ENV`, local `.env`,
`~/research/research.env` and `~/research.env`, with no n8n path. The paired
canonical/live files have identical SHA-256 content. A bounded scan of active
platform/Research files found no remaining `n8n-local` reference.

## Disposition

`PLATFORM_PROVIDER_OWNER_PARITY_VERIFIED; N8N_SURFACE_FULLY_DECOUPLED`

No provider call, service start, credential read, data mutation, Git, Docker
or WIN operation occurred.

## Rollback and boundary

Rollback is the inverse fallback-list substitution in the paired provider
files. Protected credential files remain in place; optional external provider
availability remains unchanged and gated.
