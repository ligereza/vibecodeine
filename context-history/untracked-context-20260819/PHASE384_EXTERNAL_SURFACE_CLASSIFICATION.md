# Phase 384 — external surface classification

Date: 2026-08-15 (America/Santiago)

## Scope

Read-only metadata and bounded reference scan from `/home/mak/*` for
`model-config`, `searxng`, the old Blender runtime and Python environments.
No provider, search engine, Blender, XIO/ADB, n8n, service or network action
was started.

## Results

| Surface | Evidence | Disposition |
|---|---|---|
| `/home/mak/model-config/Modelfile` | 136-byte model configuration; no active consumer found | Preserve; model activation is outside this migration slice |
| `/home/mak/searxng/settings.yml` | 190-byte settings file; textual references occur in research/docs/tests, but no running search service was observed | Preserve; external/search boundary remains gated |
| `/home/mak/blender-4.5.3-viejo` | Distinct 1.2G Blender 4.5.3 runtime with executable and asset-support tree; 110 RD blend assets make provenance plausible | Preserve pending named creative consumer; do not delete or replace |
| `/home/mak/venv-providers` | 57M Python environment with valid `pyvenv.cfg`; no active path proof | Preserve; do not install or activate providers |
| `/home/mak/venvs/flujo`, `/home/mak/venvs/oi`, `/home/mak/venvs/visual-index-pilot` | Distinct environments totaling 6.6G; runtime ownership remains slice-specific | Preserve; reconcile only when a named consumer is selected |

## Foreground validation

```text
root metadata and top-level structure: collected successfully
old Blender top-level executable inventory: collected successfully
active source reference scan: completed without opening credentials
no matching Blender/searx/provider process observed
cron active entries: 0
```

No file was changed. No candidate met the confirmed-junk threshold.

Disposition: `EXTERNAL_SURFACES_CLASSIFIED; PRESERVE_AND_GATE`.
