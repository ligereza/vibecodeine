# Phase 361 — n8n credential-owner migration

Date: 2026-08-15 (America/Santiago)

## Finding

`/home/mak/n8n-local` was correctly excluded as an automation department, but
active Research/platform consumers still used its `research.env` as a default
credential fallback. The directory contains mode-600 credential material and
cannot be treated as deletable junk.

## Change

The active consumers now use the existing Research credential path:

- `/home/mak/plataforma/providers.py`
- `/home/mak/research/research_lib.py`
- `/home/mak/research/interfaz.py`
- `/home/mak/research/watchdog.sh`
- `/home/mak/research/interfaz.service`
- `/home/mak/research/cola.service`

The n8n fallback was removed; no secret values were copied, printed or
modified. `/home/mak/n8n-local` and its three environment files remain in
place as protected historical/credential evidence. The existing
`/home/mak/research/research.env` is now the active owner path.

## Validation

```text
ACTIVE_N8N_CREDENTIAL_FALLBACK=ABSENT
RESEARCH_ENV_OWNER=PASS
PYCOMPILE_RC=0
BASH_RC=0
STATIC_RC=0
UNIT_VERIFY_RC=0
```

`systemd-analyze verify` checked both unit files without starting them.

## Disposition and rollback

`N8N_TOOL_DISCARDED; CREDENTIAL_STORE_PROTECTED; RESEARCH_OWNER_ACTIVE`

Rollback is the inverse path substitution in the six listed active files;
credential files are not deleted or moved. External provider availability is
still governed by the Research environment and was not enabled or called.
