# Phase 331 — Blender runtime provenance gate

Date: 2026-08-15 (America/Santiago)
Scope: bounded decision for the two large external Blender installations.

## Evidence

Current runtime:

- `/home/mak/blender/blender`
- version `4.5.4 LTS`, build hash `b3efe983cc58`, build date 2025-10-28
- active consumers include `tools/render_flyer_mak.py`, the conductor registry
  and curatoria diagnostics; the test contract expects this exact path.

Older runtime:

- `/home/mak/blender-4.5.3-viejo/blender`
- version `4.5.3 LTS`, build hash `67807e1800cc`, build date 2025-09-09
- no active path consumer was found in the bounded search.

Both trees have the same launcher/desktop metadata shapes, but the main
binaries differ and the versions are not identical. Each `--background
--factory-startup --version` probe returned rc=0. No project was opened and no
render was executed.

## Disposition

`PROTECT_CURRENT_RUNTIME; OLD_EXTERNAL_RUNTIME_REVIEW`.

The current tree is load-bearing and stays. The old tree is not confirmed
duplicate junk: it is a distinct 4.5.3 runtime, and deleting or moving it
could break an unrecorded legacy project. Keep it preserved until a project/
asset provenance check or explicit owner decision establishes that it can be
quarantined. Version age and size alone are insufficient.

## Changes and risks

- Blender trees, source, assets, databases, services, Git and WIN: unchanged.
- Risk: future cleanup must prove no `.blend`/addon/script requires 4.5.3 and
  must record a reversible quarantine path before moving 1.2 GB.
- Rollback: not applicable; no move occurred.

