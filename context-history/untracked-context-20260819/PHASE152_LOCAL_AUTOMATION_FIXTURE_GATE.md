# Phase 152 — local FLUJO automation fixture gate

Date: 2026-08-15

## Consumer chain

The active local automation is `src/flujo/automation.py`, consumed by the hub
endpoint `/api/auto-pending-flyers` and the explicit app processing path. It
uses the existing job lifecycle (`prepare_job` and `activate_job`); it is not a
second job framework. The external chain remains Gmail -> GitHub issue ->
bridge/URL and is outside this local writer gate.

## Foreground validation

An isolated temporary workspace was created with one
`pedido_original.txt` fixture. The command imported
`flujo.automation.run_pending_flyers` and ran it against that temporary root.
Observed result:

- `ok=True`;
- `processed=1`, action `prepared`;
- `brief.yaml` created;
- `reporte_job.md` created;
- resulting brief state `pendiente_datos`;
- assertion `AUTOMATION_FIXTURE=PASS`.

The fixture workspace was temporary; no live MAK job, database, issue, email,
provider, external URL, or permanent process was touched. The state staying
`pendiente_datos` confirms that the automation does not invent missing event or
delivery data.

## Decision

The local automation contract is `FIXTURE_VERIFIED_LOCAL_PARTIAL`. The
provider-backed Gmail/issue writer remains an explicit external gate, not a
missing local implementation. No code change was needed in this slice.

## Next action

Refresh the objective matrix with the stronger non-serve CLI and local
automation evidence, then continue to the next unresolved MAK consumer or
dependency slice. Do not run the external issue/email writer automatically.

