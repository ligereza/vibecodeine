# Phase 154 — MAK issue bridge projection merge

Date: 2026-08-15

## Finding

The active-looking paths
`/home/mak/plataforma/puente_issues.py`,
`/home/mak/flujo/cultura/mak_plataforma/puente_issues.py` and
`/home/mak/flujo-deploy/cultura/mak_plataforma/puente_issues.py` were identical
28 KB copies (`sha256=e1bc8880...705659`). The paused user crontab references
`/home/mak/plataforma/puente_issues.py`; therefore this was a real runtime
projection duplication, not unrelated history.

## Change

The root runtime path is now a small ASCII wrapper that delegates to the
canonical FLUJO source. The previous root copy was moved intact to
`context/quarantine/phase154_platform_bridge_projection/puente_issues.py.pre-wrapper`.
The source and rollback copy have matching pre-change hashes. No cron entry was
created or enabled; the current user crontab remains paused/commented.

## Validation

- wrapper and canonical `--help`: exit 0 and byte-equal output;
- wrapper and canonical source: `py_compile` exit 0;
- canonical dry-run with `active_enabled`, shadow queue and issue lookup safely
  stubbed: result `0`, `CANONICAL_DRY_RUN=PASS`, no issues processed;
- process gate: no bridge, hub, serve, generator or Vite process;
- no external issue/email/rclone/Blender writer ran.

## Decision

Objective 10 gains a real consumer-backed merge: the paused future cron target
and FLUJO source now have one implementation. The external Gmail -> issue -> URL
contract remains unchanged and gated. The Windows bridge and WIN copies remain
historical evidence; they were not deleted or rewritten.

## Next action

Run the relevant core verification and refresh the objective matrix. Then audit
the next remaining active MAK department/tool surface; do not enable cron or
invoke the external bridge as part of validation.

