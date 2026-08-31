# Phase 272 — architecture closeout and merge queue

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none  
Status: `ARCHITECTURE_BASELINE_REFRESHED; NO_BROAD_MOVES`

## Final house model

The physical tree remains layered by owner and consumer. The fact that WIN
contains an older copy of MAK does not make every similarly named file a merge
candidate: WIN is provenance, while `/home/mak/flujo` is the active semantic
owner.

```text
/home/mak/
├── flujo/                         canonical FLUJO source, hub, CLI, tests, data
│   └── context/quarantine/        reversible phase-scoped candidates
├── research/ codex/ curatoria/    active department projections
├── plataforma/ vigia/ lenguaje/   department surfaces, gated individually
├── RD/ curatoria_inbox/            protected creative and inbound corpus
├── portfolio_media/ renders/      generated and published outputs
├── trazos/                         creative source/evidence
├── labs/ indexes/ state/           derived evidence and reconciliation state
├── backups/ rollback/ quarantine/ recovery and audit evidence
├── WIN/                            historical Windows archive, read-only
├── apps/ Apps/ src/ models/       external applications, source, model assets
├── venvs/ .venvs/                  host/runtime environments
├── blender/ searxng/ actions-runner/ external infrastructure
├── flujo-deploy/                   separate deployment surface
├── bucle/ vibecodeine/             preserved cultural/source projects
├── n8n-local/ xio_puente/          excluded from active migration
└── host folders/dotdirs/logs       outside MAK reorganization authority
```

The root-level audit in Phase 271 closes the previously unresolved installer,
diagnostic and provider-tool question: these remain at their original paths
and are not active MAK departments.

## Objective refresh

| # | Objective | Current disposition | Next gate |
|---:|---|---|---|
| 1 | RD field data | Strict temporary dry-run passes; live `rd_datos.db` empty | Human privacy/date review and explicit ingest authority |
| 2 | RD database fusion | `rd.db` is merged 20-table catalog; `rd_datos.db` stays separate privacy store | Separate migration decision only if lifecycle changes |
| 3 | RD mutating routes | 16 POST paths classified; fixture gates pass | Named live input/output/rollback and authority |
| 4 | FLUJO automations | `EVENTO ...` issue/URL bridge user-confirmed; cron inactive; n8n excluded | Explicit re-enable request |
| 5 | Non-serve FLUJO commands | Read/help/compile/allow-list gates pass | Provider and mutator commands remain gated |
| 6 | RD assets/tools | Read-only asset/index/render fixture slices pass | Optional live delivery only if requested |
| 7 | Dependencies | Slice matrix and `pip check` pass | Named consumer before optional promotion |
| 8 | Folder architecture | Layered baseline refreshed and physically checked | Path-specific consumer decision |
| 9 | Duplicate documents | 99 exact-hash groups/334 paths classified by provenance | Named family with consumer-safe merge and rollback |
| 10 | Equivalent tools | Owner/projection ledger established; root optional tools unconsumed | Remove a projection only with manifest/test proof |
| 11 | Full MAK audit | Local health/fixture gates pass; risk/external surfaces remain gated | Per-file risk promotion or authority |
| 12 | Junk cleanup / WIN history | Confirmed residue removed; one legacy UI quarantined; WIN preserved | No broad cleanup; path-specific evidence only |
| 13 | Git branches | Branch proposal aligned with layers and write sets | Explicit request before Git mutation |

Full completion is not claimed: the remaining gates are authority boundaries,
not reasons to flatten the house or treat historical material as garbage.

## Merge queue, in execution order

### Queue A — consumer-backed tool families

1. Keep `/home/mak/flujo/cultura/*` as semantic owners.
2. Keep only runtime projections with a named consumer in `research`, `codex`,
   `curatoria`, `plataforma`, `vigia` and `lenguaje`.
3. For every proposed removal, record source, consumer, language, platform,
   hash/mode, foreground test and inverse move in a phase report.
4. The platform legacy UI move is the current model: one file, reversible,
   validated; no department-wide move.

### Queue B — documents and generated products

1. Do not merge by filename, language or exact hash alone.
2. For each named family, identify master/editable/runtime projection,
   generated delivery, historical capture and active consumer.
3. Merge only when provenance and output semantics agree; quarantine the old
   path before any later deletion decision.
4. Preserve databases, media, credentials, logs, memories, journals,
   generated products and WIN even when bytes match.

### Queue C — remaining review surfaces

Process one surface at a time, starting with the highest local value and
lowest mutation risk: `lenguaje`, `trazos`, `bucle`, `vibecodeine`, then the
separate `flujo-deploy` and old Blender/provider environments. Their first
action is static consumer mapping, not moving files. `n8n-local` and
`xio_puente` remain excluded; root installers/providers/diagnostics remain
execution-gated.

## Safety boundary

No files, databases, services, providers, credentials, WIN content or Git
state changed in this phase. The next implementation phase may move only a
named path after the consumer proof and rollback are written first.

## Next concrete action

Run the static consumer audit for `/home/mak/lenguaje` as the next review
surface, beginning with `/home/mak/*`, then compare only its canonical FLUJO
owner and runtime projection. Produce a bounded report before any move.
