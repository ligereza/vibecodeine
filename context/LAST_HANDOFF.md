# LAST_HANDOFF - MAK

Updated: 2026-08-13
Status: local reconciliation is complete for the selected MAK and structure
scope. This checkout is a local authority surface; Git is transport only.

## Authority

- MAK is the operational producer, curator, researcher, and coordinator.
- RD and Portfolio retain separate ownership, safety, authorial, and
  publication gates. They share one logical knowledge database target.
- Windows and MAK have different physical structures. Do not force symmetry.
- Raw material, databases, indexes, memories, services, and credentials stay
  on their owning local surface. No bidirectional sync is active.
- Machine-facing code and operational metadata use English ASCII where
  practical; human RD and Portfolio products keep correct Spanish.

## Active checkout and NUDO

- Checkout: /home/mak/flujo, branch `mak`, local work is the MAK projection.
- NUDO source remains preserved at branch `codex/nudo-rd-evidence`.
- NUDO code and tests were projected into this active checkout without reset,
  checkout, merge, or deletion of the source branch.
- Three-plane contract and unified-knowledge migration/reconciliation code
  were projected from the Win transport surface.
- Obsolete `cultura/mak_plataforma/RELEVO_MAK.md` was removed from the active
  checkout and preserved at
  `/home/mak/rollback/local-reconciliation-20260813/`.

## Local catalog and databases

- Post-NUDO index:
  `/home/mak/indexes/mak-consolidation-20260813/mak_local_reality_index_post_nudo.json`.
- The index validates 10 local roots and 24 selected artifacts; none are
  missing. Earlier consolidation reports are superseded evidence, not rules.
- PostgreSQL `mak_knowledge` remains a prepared target, not current authority.
- RD SQLite remains physically divergent from Windows. The read-only plan
  found 20 tables: 11 identical, 1 conflict, 8 candidate-only, 0 legacy-only;
  no writes were performed and no writer was selected.
- DuckDB `1.5.5` is installed in `/home/mak/vibecodeine/.venv`.

## Verification

- The focused MAK suite passed in `/home/mak/vibecodeine/.venv`, including
  three-plane, migration, NUDO, sync, and department tests.
- Win passed the corresponding focused suite. Optional unavailable tools are
  deferred explicitly; ZIP metadata uses the standard-library fallback.
- `MAK-REPO-SYNC` remains paused. No active sync may overwrite local work.

## Safety and next action

- Do not touch README/SVG, raw media, private recovered exports, databases,
  or indexes during Git transport.
- Do not choose a primary database writer or merge main from this handoff.
- Stage only the reviewed structural and NUDO/Research scope, run final
  checks, and push the scoped checkpoint branch.
