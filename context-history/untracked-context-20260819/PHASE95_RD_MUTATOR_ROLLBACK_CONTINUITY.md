# Phase 95 — RD mutator rollback continuity

## Scope

Rechecked the current source surface and physical MAK roots after the Phase
56–60 fixture gates.

## Validation

- AST found all expected mutator functions in `src/flujo/web/hub.py`:
  `_create_job_draft`, `_handle_datadrop_upload`, `_subir_logo`,
  `_handle_datadrop_analyze` and `_guardar_simbolo_plano`.
- AST found `run_pending_flyers` in `src/flujo/automation.py`.
- No files matching `phase`, `fixture` or `tmp` were found in the bounded real
  roots `/home/mak/flujo/jobs`, `/home/mak/flujo/datadrops`,
  `/home/mak/flujo/data` or `/home/mak/RD`.
- Targeted process check found no FLUJO server, Blender, Ollama, Watson/AWS or
  automation process.

## Decision

The RD mutator surface remains `FIXTURE_VERIFIED_WITH_ROLLBACK`; continuity is
confirmed and production remains untouched. This is stronger than a help-only
check but does not authorize a live job/upload/render/provider operation.

## Next

Continue with the automation/provider boundary and remaining ownership merges;
retain explicit production authority and the pytest/web recovery conditions.
