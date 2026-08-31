# Phase 56 — RD create-job-draft mutator gate

## Scope

Selected `/api/create-job-draft` / `HubRequestHandler._create_job_draft` as
the first RD-adjacent mutating consumer. The real hub writer creates a job
folder and traceability files, so the validation used a temporary job root and
monkeypatched `create_job`; no `/home/mak/flujo/jobs` path was touched.

## Foreground validation

```text
temporary _create_job_draft fixture with parsed RD payload
exit=0; created folder, pedido_original.txt, intake.json and resultado.md

temporary fixture rollback
exit=0; only the temporary directory was removed and no MAK evidence changed

AST parse /home/mak/flujo/src/flujo/web/hub.py
exit=0
```

## Decision

The create-job-draft contract is `PASS_WITH_ROLLBACK_FIXTURE`. The broader
mutator phase remains open for `/api/datadrop-upload`,
`/api/auto-pending-flyers`, symbol persistence and real render output. These
must each use isolated fixtures or explicit output rollback; no production
job, upload, render or external automation was executed.
