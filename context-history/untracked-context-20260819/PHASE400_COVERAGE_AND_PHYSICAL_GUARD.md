# Phase 400 — coverage refresh and physical guard

Date: 2026-08-15 (America/Santiago)

## New local test evidence

| Group | Files | Cases | Result | Boundary |
|---|---:|---:|---|---|
| Conservative safe suite | 68 | 485 | pass | marker-filtered local tests |
| EVENTOS/bridge fixtures | 2 | 6 | pass | mocks and `tmp_path` |
| Reception fixtures | 1 | 2 | pass | mocked IMAP |
| Hub EVENTOS fixtures | 1 | 15 | pass | temporary JSONL and mocked HTTP |
| Nocturnal cleanup fixtures | 1 | 13 | pass | temporary files only |

The promoted groups are kept separate from the conservative suite count to
avoid double-counting. The historical 177-file risk surface remains a
per-file promotion queue, not a blanket failure and not completed coverage.

## Physical guard

```text
pip check: exit 0
active AST: 550/550
rd_datos.db: integrity ok; atenciones=0; encuestas=0; registros_testeo=0; sqlite_sequence=0
active cron entries: 0
matching MAK/FLUJO/sync/provider/service processes: 0
active bytecode: 0
```

No external, live, durable, WIN, Git, provider, worker or service state
changed in this phase.

Disposition: `LOCAL_COVERAGE_REFRESHED; PHYSICAL_GUARD_GREEN`.

## Remaining proof gaps

RD candidate privacy/field authority, one live RD mutation, external EVENTO
replay/render/provider behavior, remaining risk-test promotion, physical
semantic document fusion and Git branch application remain open.
