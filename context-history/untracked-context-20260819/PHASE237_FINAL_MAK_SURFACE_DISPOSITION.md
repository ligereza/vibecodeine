# Phase 237 — Final MAK surface disposition

## House rule

The final house is layered by owner and consumer. `/home/mak/flujo` owns
active FLUJO source/integration; department roots remain runtime projections
only when a consumer exists; RD/media/data/evidence remain protected; WIN is
historical read-only. Similar names, languages or dates never authorize a
merge.

| Surface | Owner/role | Consumer | Language/platform | Disposition | Rollback |
|---|---|---|---|---|---|
| `/home/mak/flujo` | canonical source/integration | CLI, hub, jobs, RD, departments | ES/EN metadata; Linux | keep owner | filesystem/git review only |
| `/home/mak/WIN` | historical source/archive | provenance/crosswalk only | Windows/ES/EN | keep historical read-only | never clean; original path |
| `/home/mak/RD` | protected creative corpus | RD delivery, assets, index | Spanish delivery; cross-platform assets | keep protected; classify internally | preserve original path |
| `/home/mak/curatoria_inbox` | protected inbound | curation/asset intake | mixed | keep protected | preserve original path |
| `/home/mak/research` | runtime projection | Research service/UI | ES/EN; Linux | keep runtime | restore projection via owner map |
| `/home/mak/codex` | runtime projection | Codex jobs/pieces | ES/EN; Linux | keep runtime | restore projection via owner map |
| `/home/mak/curatoria` | runtime projection | curation/index | ES/EN; Linux | keep runtime | restore projection via owner map |
| `/home/mak/plataforma` | mixed platform surface | platform ledgers/UI | ES/EN; Linux | keep mixed; review files individually | path-level only |
| `/home/mak/plataforma/panel_directivo.py` | incomplete evidence | no active consumer | ES/EN; Linux source | preserve, not active | original path |
| `/home/mak/plataforma/interfaz.py` | legacy UI candidate | historical tests only; no launcher | ES/EN; Linux source | preserve pending explicit move | original path |
| `/home/mak/vigia` | runtime projection | monitoring wrappers | ES/EN; Linux | keep runtime | owner crosswalk |
| `/home/mak/lenguaje` | language department | lexicon/hooks/roles | Spanish + ASCII machine keys; Linux | keep department | owner crosswalk |
| `/home/mak/flujo/data/rd.db` | catalog projection | RD catalog/curatoria | Spanish data; SQLite/Linux | keep catalog owner | rebuild from canonical sources |
| `/home/mak/flujo/data/rd_datos.db` | privacy field store | field ingest/report | Spanish data; SQLite/Linux | keep separate privacy owner | restore from protected backup |
| `/home/mak/labs` | derived evidence/indexes | reconciliation/experiments | machine ASCII; Linux | keep evidence | quarantine per artifact |
| `/home/mak/indexes` | derived indexes | catalog/search | machine ASCII; Linux | keep derived | regenerate from source |
| `/home/mak/state` | probe/recovery state | audit continuity | machine ASCII; Linux | keep evidence | preserve snapshot |
| `/home/mak/portfolio_media` | published media | portfolio | mixed; cross-platform | keep output | preserve delivery |
| `/home/mak/renders` | generated output | RD/visual delivery | mixed; cross-platform | keep output | preserve delivery |
| `/home/mak/trazos` | creative source | SVG/design work | Spanish labels; cross-platform | keep source/evidence | original path |
| `/home/mak/models` | model artifacts | optional visual index | machine/API; Linux | keep external model | reinstall/relink only with authority |
| `/home/mak/src` | external source | optional model/tool consumers | machine/API; Linux | keep external source | relink owner |
| `/home/mak/apps` and `/home/mak/Apps` | installed applications | host tools | mixed; Linux/Windows assets | keep external | host package recovery |
| `/home/mak/blender` and old Blender | external runtime | creative assets | cross-platform | keep; old version review only | restore host install |
| `/home/mak/venvs`, `/home/mak/.venvs`, `/home/mak/venv-providers` | environments | slice runtimes | machine/API; Linux | keep per environment | recreate from manifests |
| `/home/mak/flujo-deploy` | deploy artifact | `mak_sync_safe.py` | machine/API; Linux | keep separate external deploy owner | deploy rollback |
| `/home/mak/backups`, `/home/mak/rollback`, `/home/mak/quarantine` | recovery | rollback/audit | machine ASCII; Linux | keep recovery | inverse operation in ledger |
| `/home/mak/n8n-local` | discarded provider surface | none active | mixed | excluded from active MAK; preserve evidence | original path |
| `/home/mak/xio_puente` | user-excluded bridge | none in this plan | mixed | excluded by user | original path |
| `/home/mak/bucle`, `/home/mak/vibecodeine` | cultural/source projects | no bounded runtime consumer | mixed | preserve source; review by consumer | original path |
| `/home/mak/curatoria_test` | test evidence | test fixtures | mixed; Linux | keep test evidence | fixture rollback |
| `/home/mak/tmp` | host temporary contract | ad hoc runtime/tests | machine; Linux | preserve empty path; not junk-confirmed | original path |
| `/home/mak/OneDrive` | disconnected external mount | none verified | host sync | leave untouched; Errno 107 | host mount recovery |
| `/home/mak/flujo/context/quarantine/phase228_empty_workspace` | reversible empty staging | audit only | machine ASCII; Linux | quarantined, zero files | move back to `/home/mak/workspace` |
| `/home/mak/flujo/context/quarantine/phase229_empty_shell_residue` | confirmed empty shell residue | audit only | machine ASCII; Linux | quarantined, zero files | inverse moves recorded in Phase 229 |

## Fusion policy

- Documents merge only when provenance, role and output semantics agree; exact
  duplicates remain evidence until a consumer-safe replacement is verified.
- Tools fuse by consumer contract: canonical source plus thin runtime
  projection is a valid fusion; deleting a projection by filename similarity is
  not.
- Databases are logically reconciled but physically separate until a privacy
  and lifecycle migration is explicitly selected.
- Cleanup means reversible quarantine for confirmed residue, never deletion of
  WIN, databases, media, credentials, generated products or evidence.

## Branch alignment

This disposition maps to the existing proposal in
`context/PHASE218_GIT_BRANCH_SYSTEM_PROPOSAL.md`: architecture, RD catalog,
RD field, RD routes, CLI, automation, dependencies, departments, cleanup and
release each get disjoint write sets. No branch was created or switched.

## Next concrete action

Use this artifact as the architecture baseline. Any next change must name one
surface, one consumer, one write set and one rollback; otherwise the local
integration is at a safe boundary awaiting the explicit external gates.
