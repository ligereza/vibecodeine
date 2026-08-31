# Phase 209 — final MAK architecture and physical disposition

Date: 2026-08-15 (America/Santiago)
Status: `ARCHITECTURE_FREEZE; NO_BROAD_MOVES`

## Architectural target

The final MAK house is layered by ownership and consumer, not flattened into
one directory:

```text
/home/mak/
├── flujo/                    canonical FLUJO source, CLI, data, jobs, tests
│   └── context/quarantine/   reversible, phase-scoped candidates only
├── research/ codex/          active runtime projections
├── curatoria/ plataforma/    active or legacy department surfaces under gates
├── vigia/ lenguaje/          department projections/tools
├── RD/                       protected creative/source/delivery corpus
├── curatoria_inbox/          protected inbound material
├── portfolio_media/ renders  protected published/generated outputs
├── labs/ indexes/ state/      derived evidence and reconciliation indexes
├── models/ src/ apps/        external models, source and applications
├── backups/ rollback/        recovery surfaces
├── WIN/                      historical Windows archive, read-only
└── host/runtime directories  OS, environments and external infrastructure
```

`/home/mak/flujo` is the semantic owner for active FLUJO code. Root department
directories remain runtime projections only where a real consumer exists. RD
assets are not bulk-copied into `flujo`; they are registered/reconciled by
metadata and consumed through explicit paths. `WIN` remains complete history,
never an active source and never a cleanup target.

## Physical disposition from `/home/mak/*`

| Surface | Observed scale | Role | Disposition |
|---|---:|---|---|
| `/home/mak/flujo` | 862M | canonical source/runtime/data/jobs | `KEEP_OWNER`; all active code and integration records live here |
| `/home/mak/RD` | 57G | creative sources, editables, deliveries, evidence | `KEEP_PROTECTED`; classify internally, no bulk merge |
| `/home/mak/WIN` | 7.9G | Windows genealogy and former FLUJO | `KEEP_HISTORICAL_READ_ONLY`; never delete or activate |
| `/home/mak/curatoria_inbox` | 173G | inbound visual/audio/project material | `KEEP_PROTECTED_INBOUND`; provenance gate per item |
| `/home/mak/research` | 768M | active Research runtime projection and state | `KEEP_RUNTIME`; owner crosswalk is complete |
| `/home/mak/codex` | 2.6M | active Codex runtime projection | `KEEP_RUNTIME`; semantic owner is `flujo/cultura/mak_codex` |
| `/home/mak/curatoria` | 8.4M | active Curatoria projection | `KEEP_RUNTIME`; evidence/index consumers remain explicit |
| `/home/mak/plataforma` | 106M | platform runtime plus legacy candidates | `KEEP_FOR_NOW`; only `/home/mak/plataforma/interfaz.py` is a bounded quarantine candidate; no move yet |
| `/home/mak/vigia` | 344K | active monitoring projection | `KEEP_RUNTIME`; canonical wrapper gate passed |
| `/home/mak/lenguaje` | 1.5M | language department/tool surface | `KEEP_UNTIL_CONSUMER_AUDIT`; do not merge by name |
| `/home/mak/labs` | 439M | derived indexes, SQLite/WAL, summaries | `KEEP_EVIDENCE`; never promote or delete by size |
| `/home/mak/indexes` | 113M | derived indexes/reconciliation outputs | `KEEP_DERIVED`; path-level provenance required |
| `/home/mak/state` | 301M | Windows/runtime probe metadata | `KEEP_EVIDENCE`; not a runtime source |
| `/home/mak/portfolio_media` | 5.5G | portfolio media | `KEEP_OUTPUT`; no hash-only cleanup |
| `/home/mak/renders` | 120K | generated renders | `KEEP_OUTPUT`; preserve delivery provenance |
| `/home/mak/trazos` | 4.9M | creative SVG/source corpus | `KEEP_SOURCE_OR_EVIDENCE`; consumer audit before fusion |
| `/home/mak/models` | 206M | MobileCLIP/model artifacts | `KEEP_EXTERNAL_MODEL`; consumed lazily, do not copy |
| `/home/mak/src` | 11M | external source such as MobileCLIP | `KEEP_EXTERNAL_SOURCE`; linked consumer only |
| `/home/mak/apps` | 1.4G | installed application resources | `KEEP_EXTERNAL`; never merge into Python source |
| `/home/mak/Apps` | 576M | application bundle/resources | `KEEP_EXTERNAL`; no MAK source move |
| `/home/mak/blender` | 1.2G | external Blender installation | `KEEP_EXTERNAL`; runtime dependency surface |
| `/home/mak/blender-4.5.3-viejo` | 1.2G | older Blender installation | `REVIEW_BY_PROVENANCE`; no deletion from age/size alone |
| `/home/mak/venvs` | 6.6G | runtime environments | `KEEP_RUNTIME`; dependency audit by environment |
| `/home/mak/.venvs` | 6.9G | additional environments | `KEEP_HOST_RUNTIME`; outside source fusion |
| `/home/mak/venv-providers` | 57M | provider environment | `KEEP_EXTERNAL_RUNTIME`; no provider calls in this audit |
| `/home/mak/backups` | 166M | backups | `KEEP_RECOVERY`; no cleanup without retention authority |
| `/home/mak/rollback` | 240M | rollback snapshots | `KEEP_RECOVERY`; supports reversible cleanup |
| `/home/mak/quarantine` | 185M | previous quarantine/recovery evidence | `KEEP_RECOVERY`; never treat as ordinary junk |
| `/home/mak/flujo-deploy` | 153M | deployment artifact/surface | `REVIEW_BY_PROVENANCE`; separate from canonical source |
| `/home/mak/actions-runner` | 998M | external runner infrastructure | `KEEP_EXTERNAL`; no merge into MAK source |
| `/home/mak/n8n-local` | 16K | discarded automation surface | `EXCLUDED_FROM_ACTIVE_MAK`; preserve until credential/provenance gate, no runtime start |
| `/home/mak/xio_puente` | 3.0M | user-excluded XIO bridge | `EXCLUDED_BY_USER`; no testing or migration |
| `/home/mak/bucle` | 2.6M | loop/orchestration material | `REVIEW_BY_CONSUMER`; no broad move |
| `/home/mak/vibecodeine` | 440M | creative/cultural source | `KEEP_SOURCE`; provenance and consumer audit |
| `/home/mak/curatoria_test` | 28M | test fixtures | `KEEP_TEST_EVIDENCE`; remove only per fixture ledger |
| `/home/mak/curatoria_encolado` | 4K | staging/queue surface | `REVIEW_BY_PATH`; no consumer decision yet |
| `/home/mak/workspace` | 16K | workspace state | `REVIEW_BY_CONSUMER`; do not merge into jobs blindly |
| `/home/mak/OneDrive` | disconnected mount | external sync surface | `LEAVE_UNTOUCHED`; inventory returned Errno 107, no repair attempted |
| host dot-directories and user folders | variable | OS, credentials, caches, apps, environments | `OUTSIDE_MAK_REORGANIZATION`; no recursive cleanup |
| loose root files/logs/installers | small/unknown | mixed diagnostics, launchers, history | `UNRESOLVED`; path-level provenance required before any move |

## Merge and cleanup rules now frozen

1. Merge tools by consumer contract, not by similar names or language. A
   Spanish/English alias, Windows launcher or ASCII path variant must be
   included in the crosswalk before a candidate is called unused.
2. Merge documents only when provenance, role and output semantics agree.
   Exact RD duplicates remain preserved evidence unless a consumer-safe
   replacement and explicit move authority exist.
3. Keep databases separate: `data/rd.db` is catalog/evidence projection;
   `data/rd_datos.db` is privacy-first field data and is currently empty.
4. `n8n-local` is excluded from active architecture; XIO is excluded by user;
   neither is a reason to delay the remaining FLUJO work.
5. `JUNK_CONFIRMED` requires no active consumer, no evidence/source/output/
   recovery role, a reversible quarantine, foreground validation and a
   recorded rollback. No root-level item currently passes all five gates.

## Current cleanup disposition

- Exact RD pack files: preserve; hash equality is not deletion authority.
- `/home/mak/plataforma/interfaz.py`: one bounded quarantine candidate, pending
  explicit move gate; not moved in this phase.
- `/home/mak/plataforma/panel_directivo.py`: preserve incomplete evidence; no
  repair or deletion.
- All large surfaces: preserve; no size-based cleanup.

## Next concrete action

Produce the visual closeout snapshot from this frozen architecture and the
13-objective matrix. Then run the final consumer audit for the remaining
`REVIEW_BY_CONSUMER` surfaces before deciding whether the single platform UI
candidate can enter phase quarantine. Git branch design follows those gates.

