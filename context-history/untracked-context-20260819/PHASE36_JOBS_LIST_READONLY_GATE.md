# Phase 36 — local jobs list read-only gate

Identity: LUNA principal
Status: INTEGRATED_READ_ONLY
Scope: migrate the WIN FLUJO hub consumer for local job listing into the
active MAK runtime without creating, preparing, activating or rendering jobs.

## Consumer and provenance

- Hub route: `GET /api/list-jobs`.
- MAK source: `/home/mak/flujo/src/flujo/web/hub.py` and
  `/home/mak/flujo/src/flujo/jobs/job.py`.
- Brief parser: `/home/mak/flujo/src/flujo/jobs/brief.py`.
- MAK data surface: `/home/mak/flujo/jobs/*/brief.yaml`.
- WIN comparison surface: `/home/mak/WIN/flujo/jobs/*/brief.yaml`.
- The route uses `list_jobs(include_examples=False)`: it reads each
  `brief.yaml`, skips `_template`, and returns job metadata. The nearby
  `create_job` path is mutating and was deliberately excluded.
- Search vocabulary used: `job`, `jobs`, `trabajo`, `trabajos`, `brief`,
  `pedido`, `estado`, `status`, `pending`, `pendientes`, `list`, `listar`.
  Residual false-negative risk is limited to alternate job stores outside the
  active `flujo/jobs` contract; no alternate store was invoked.

## Static and direct validation

Foreground command (exit 0):

```text
PYTHONPATH=/home/mak/flujo/src /home/mak/venvs/flujo/bin/python - <<'PY'
  ast.parse(hub.py); ast.parse(job.py); ast.parse(brief.py)
  import flujo.web.hub, flujo.jobs.job, flujo.jobs.brief
  list_jobs(repo=/home/mak/flujo, include_examples=False)
  HubRequestHandler._list_jobs_api()
PY
```

Observed:

- AST/import gate: `PASS`.
- Direct reader: `PASS`, 8 jobs.
- Response keys per item: `name`, `path`, `estado`, `tipo_pieza`,
  `proyecto`, `pendientes`.
- Envelope: `connected=true`, `source=jobs`, `count=8`.
- `_template` was not exposed.
- Protected MAK job-tree snapshot before/after direct read:
  `writes_detected=false`.

## WIN → MAK bounded crosswalk

- MAK briefs found: 9, including `_template`.
- WIN briefs found: 8, including `_template`.
- Common non-template briefs: 8.
- Common brief contents: equal after CRLF/LF normalization.
- MAK-only brief: `2026-07-05_contraportadas/brief.yaml`.
- WIN-only non-template briefs: none.
- No file was copied, edited or deleted.

## Temporary HTTP gate

A temporary in-process `ThreadingHTTPServer` was bound to
`127.0.0.1:<ephemeral>`. Exactly one `GET /api/list-jobs` was served, then the
server was shut down and joined.

- HTTP status: `200`.
- HTTP payload: 8 jobs, `source=jobs`, `connected=true`.
- Direct and HTTP payloads: equal.
- Protected MAK job-tree snapshot after shutdown: `writes_detected=false`.
- No POST, job creation, preparation, activation, renderer or worker ran.

## Decision and rollback

The local job-listing slice is integrated read-only. The existing MAK reader
is already the correct consumer for the migrated hub; no adapter or source
edit is required. The `create_job`, `prepare`, `activate` and automation
paths remain outside this gate because they can mutate the job store.

Rollback is physical preservation: retain the existing reader and job store;
if a later lifecycle check fails, do not call the mutator and classify that
branch as deferred. This phase changed only this evidence report and its CSV.

