# Phase 217 — cleanup and objective closeout snapshot

Date: 2026-08-15 (America/Santiago)

## Cleanup gate

Previously confirmed shell residue is gone from active surfaces:

- `/home/mak/curatoria_inbox`: `.DS_Store` active count `0`; 92 preserved in
  `context/quarantine/phase124_ds_store/`.
- `/home/mak`: literal stray file `\\;` active count `0`; seven phase-126
  shell-residue objects preserved in
  `context/quarantine/phase126_stray_shell_artifacts/`.
- `/home/mak/curatoria_encolado`: empty; no consumer reference found, but no
  deletion was executed.

The confirmed junk is therefore removed from active working surfaces while its
evidence remains recoverable. The platform UI legacy file and incomplete panel
are not classified as junk: they are historical source/evidence and remain.

## Objective status

| # | Objective | Current state | Proof or remaining gate |
|---:|---|---|---|
| 1 | RD datos de terreno | `OPEN / DEFERRED` | Empty field DB and report path pass; real field authority absent. |
| 2 | Fusión de bases `rd.db` | `CLOSED AS SEPARATE` | Catalog and field store have different lifecycle/owners; no merge is correct. |
| 3 | Rutas mutantes RD | `DEFERRED` | All POST/write boundaries classified; no authority to call them. |
| 4 | Automatizaciones FLUJO | `CLASSIFIED` | Issue URL workflow user-confirmed; local cron/provider paths paused/not executed. |
| 5 | Comandos no-serve | `GATED PARTIAL` | Read surfaces pass; writers have fixture/boundary classifications. |
| 6 | Assets RD | `INTEGRATED` | 1,742 regular files reconcile to index by path/size/mtime. |
| 7 | Dependencias por slice | `GATED PARTIAL` | Base requirements consistent; optional provider/GPU/render paths remain scoped. |
| 8 | Arquitectura final de carpetas | `FROZEN` | Phase 209 physical disposition and Phase 210 visual map. |
| 9 | Documentos duplicados | `LEDGERED` | Exact/semantic roles and protected evidence recorded. |
| 10 | Herramientas equivalentes | `ROLE-MAPPED` | Research/Codex/platform/language/deploy owners mapped; no unsafe fusion. |
| 11 | Auditoría completa MAK | `IN PROGRESS` | 216/110 projection syntax and foreground gates; remaining historical/external surfaces documented. |
| 12 | Basura confirmada | `GATED PARTIAL` | 99 confirmed shell artifacts quarantined; new candidates not yet cleared. |
| 13 | Sistema de ramas Git | `PROPOSAL NEXT` | No branches created or history changed; proposal follows in Phase 218. |

## Safety state

All four relevant user services are inactive. No persistent process, cron,
provider, deploy sync, database merge, live mutator, installation, or Git
mutation occurred in this phase.

## Next concrete action

Write the new Git branch-system proposal against this frozen architecture,
without creating branches. Define ownership, naming, merge gates and rollback
for each vertical slice. Then return to the remaining open field/mutator and
historical-surface gates.

