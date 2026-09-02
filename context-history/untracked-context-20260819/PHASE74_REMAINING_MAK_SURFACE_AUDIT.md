# Phase 74 — remaining MAK surface audit

## Physical classification

The search began at `/home/mak/*` and narrowed only to unresolved roots.

| Root | Observed surface | Classification | Decision |
|---|---|---|---|
| `/home/mak/apps` | 2,102 files, 623 dirs, ~1.46 GB | installed external applications (Antigravity/VS Code) | outside FLUJO cleanup; preserve |
| `/home/mak/labs` | 99 files, 84 dirs, ~459 MB | dated experiments, indexes, Blender/GPU evidence and research probes | evidence/lab surface; preserve and classify per lab |
| `/home/mak/src/ml-mobileclip` | 166 files, 69 dirs, ~10.9 MB | external model/library source with its own `.git`, requirements and results | optional dependency; do not merge into FLUJO |
| `/home/mak/workspace` | 0 files, 4 dirs | empty shell containing parser tool dirs | no active consumer; candidate for empty-dir cleanup only |
| `/home/mak/quarantine` | 4,087 files, 688 dirs, ~184 MB | explicit rollback/evidence snapshots and pre-change artifacts | protected evidence; never bulk-delete |
| `/home/mak/flujo/web/node_modules` | installed web build dependencies | runtime/build dependency for web UI | preserve; dependency audit separate |
| `/home/mak/flujo/web/dist*` | generated static build outputs | publish/share projections | preserve until route/build owner audit |
| `/home/mak/flujo/docs/recovered` | recovered Claude sessions and raw artifacts | historical provenance | preserve; never treat as duplicate junk |
| `/home/mak/flujo/out` and `dist_compartir` | generated/share outputs | output evidence and publication projections | preserve until consumer manifest |

## Cleanup decision

No root above is confirmed junk. The empty `/home/mak/workspace` directories
are the only narrow candidate, but they are harmless and deleting them would
not advance integration; they remain `EMPTY_UNOWNED_CANDIDATE` until the parser
tools are explicitly assigned or archived. No deletion occurred in this phase.

`/home/mak/quarantine` and `/home/mak/labs` are intentionally evidence-rich;
their large size is not proof of waste. `WIN` remains historical and protected.

## Remaining audit focus

The unresolved work is now semantic rather than a blind filesystem sweep:
map web build outputs to routes, map lab indexes to consumers, and classify
quarantine snapshots against active replacements. Only after that can a final
cleanup manifest be produced.
