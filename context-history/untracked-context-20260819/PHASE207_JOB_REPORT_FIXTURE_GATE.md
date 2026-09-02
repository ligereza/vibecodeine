# Phase 207 — bounded `job report` fixture gate (LUNA-1)

Date: 2026-08-15 (America/Santiago)

## Scope

Tested the previously deferred write-capable command against a hand-authored
minimal fixture at
`/home/mak/flujo/context/fixtures/phase207_job_report/`. No existing job tree
was copied and no real job was passed to the command.

## Validation

Command:

```text
PYTHONPATH=/home/mak/flujo/src /home/mak/venvs/flujo/bin/python -m flujo job report /home/mak/flujo/context/fixtures/phase207_job_report
```

Exit: `0`.

Expected writes were exactly:

- `estado.md` — 292 bytes, fixture state projection.
- `reporte_job.md` — 552 bytes, generated report.

The hand-authored `brief.yaml` remained present at 524 bytes. SHA-256 values
after the run:

- `brief.yaml`: `19ceafc5c849e19cc7744f8449779caa8948b08cab92c7b842d417ee34884c32`
- `estado.md`: `8830532595c487007426f875b6181246ce8fc05d90052a688d1cc4a55324f389`
- `reporte_job.md`: `b6b6fef1d4c790b6c637306f0530f9c0487e7e3df8dbee4de2d117c441a0b42f`

No `pedido_original.txt`, privacy report, database, real job report or
generated delivery was touched. The fixture is retained as a small reproducible
evidence artifact; rollback is to remove only this fixture directory if the
user later explicitly requests cleanup.

## Decision

`job report` is functionally valid for a concrete job path and its write set is
now known. It remains a controlled writer, not a safe read-only command. The
real job command must be run only when the user wants its report refreshed.

## Next concrete action

Run the final local validation of the changed CLI surface and fixture outputs,
then update the cleanup/architecture status. Do not process real datadrops,
ingest field data, render live outputs, start services or mutate Git.

