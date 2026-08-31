# Phase 354 — JSON intake schema gate

Date: 2026-08-15 (America/Santiago)

## Scope

Validated the pure schema boundary in
`/home/mak/flujo/src/flujo/intake/json_parser.py`: schema loading, valid
pedido, missing/invalid fields, additional-property rejection and temporary
JSON reading. Job creation and project writes were not called.

## Results

```text
INTAKE_SCHEMA_VALID=PASS
INTAKE_SCHEMA_INVALID=PASS errors=3
INTAKE_SCHEMA_ADDITIONAL_PROPERTIES=PASS
INTAKE_JSON_READONLY=PASS
PYCOMPILE_RC=0
```

The canonical schema accepts a complete event pedido, reports the expected
human-readable errors for invalid type/content and rejects undeclared fields.
The file loader read only a temporary JSON fixture.

## Disposition

`VERIFIED_SCHEMA_GATE; JOB_CREATION_SEPARATED`

This establishes the validation boundary before `create_job`, brief writing
and status/result files. It does not authorize applying a JSON intake to real
jobs or projects.

## Rollback and boundary

No source, real job, project, database, service, provider, Git state or WIN
evidence changed. No rollback is required. The next action should inspect the
job lifecycle in a temporary repo or a mocked path before any real activation.
