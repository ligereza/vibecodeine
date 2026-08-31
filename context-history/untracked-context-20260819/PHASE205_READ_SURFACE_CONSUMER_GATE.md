# Phase 205 — read-surface consumer gate (LUNA-1)

Date: 2026-08-15 (America/Santiago)

## Result

The remaining read-only FLUJO surfaces are wired and usable. They read the
canonical MAK workspace without starting the hub or writing a product:

| Surface | Command/result | Consumer and authority | Mutation class |
|---|---|---|---|
| Knowledge productoras/venues/logos | `knowledge list ...` exit 0; productoras 3, venues 3, logos 10 | `/home/mak/flujo/src/flujo/knowledge/store.py`, backed by `knowledge/` | read-only |
| Knowledge classifier | `knowledge classify 'EVENTO Festival Ejemplo 2026 en Espacio Riesco'` exit 0; preset `mainstream`, confidence `0.75`, venue `espacio_riesco` | local producer/venue vocabulary; no provider call | read-only |
| Job inventory | `job list` exit 0; 8 jobs | `/home/mak/flujo/jobs` via `jobs.job.list_jobs` | read-only |
| Job next-actions | `job next` exit 0; suggestions rendered for all 8 jobs | job briefs and lifecycle rules | read-only |
| RD producer profile | `rd-db productora thegrid` exit 0 | `data/rd.db` through `src/flujo/rd` | read-only |
| RD operator lookup | `rd-db lookup MDMA` exit 0; reactives and pack inclusion rendered | `rd.db` join/read layer | read-only |
| Datadrop inventory | `datadrop list` exit 0; 5 existing drops/collections | workspace datadrops directory | read-only |

The knowledge `events` entity list returned an empty result with exit 0; this
is not a failure of the RD event catalog. RD events are exposed separately by
`rd-db eventos`, which already passed in Phase 204. The two stores have
different authorities and should not be silently merged.

## Explicitly deferred

`job status` reads one selected brief and is safe when a concrete job path is
provided. `job report` calls `prepare_job` and writes `reporte_job.md`, so it is
deferred until a fixture and rollback path are selected. `datadrop scan`,
`datadrop ingest` and `knowledge ingest-example` write or process evidence and
remain deferred. No write command was called in this phase.

## Validation and safety

- Every command in the result table returned exit 0.
- Outputs were bounded with `head` only after the command had produced its
  result; no command was left running.
- No database, job, datadrop, knowledge, service, package, provider or Git
  mutation occurred.
- The separation between `knowledge` entities, RD catalog entities and
  datadrop ground truth is now explicit for later folder/tool fusion.

## Next concrete action

Reconcile the 13-objective matrix with Phases 203–205, then select one bounded
write-capable functional slice for fixture validation. The safest candidate is
`job report` on a disposable copy only if copying a minimal fixture is
authorized; otherwise continue static validation of the remaining CLI commands
and leave mutation deferred. Do not merge databases or delete preserved
evidence.

