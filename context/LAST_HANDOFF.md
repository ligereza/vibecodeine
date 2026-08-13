# LAST_HANDOFF - Faro

Updated: 2026-08-13
Status: local reconciliation is complete for the selected code scope. Windows
and MAK local surfaces determine material truth; Git is transport and review
projection only.

## Authority and topology

- Windows is the director and creative production node.
- MAK is the operational and structured-knowledge node.
- MAK, RD, and Portfolio are sovereign organisms with separate ownership and
  publication gates. They share one logical knowledge database target.
- Git `main` is the canonical reviewed history. `codex/*` and `dependabot/*`
  are temporary work. `mak`, `rd`, `iskvw`, `mejoras`, and `mak-svg` are
  transition/history refs; no new work starts there.
- No bidirectional sync is active. Runtime mirrors, databases, indexes, raw
  media, memories, and credentials remain on their owning local surface.

## Reconciliation completed

- NUDO code and tests were copied from MAK branch `codex/nudo-rd-evidence`
  into the active MAK checkout and the Win transport surface.
- Three-plane contract, unified-knowledge reconciliation/migration code,
  branch policy, workflows, and operational gates are present on both nodes.
- The obsolete `cultura/mak_plataforma/RELEVO_MAK.md` was removed from both
  active checkouts and preserved in the local rollback snapshot.
- MAK rollback snapshot:
  `/home/mak/rollback/local-reconciliation-20260813/`.
- Post-NUDO local index:
  `/home/mak/indexes/mak-consolidation-20260813/mak_local_reality_index_post_nudo.json`.
  It validates 10 roots and 24 selected artifacts with no missing artifacts.
- No raw media, README/SVG, databases, indexes, or private recovered exports
  were promoted to Git.

## Evidence

- Win focused suite passed, including three-plane, migration, NUDO, sync,
  README/SVG, and department tests.
- MAK focused suite passed in `/home/mak/vibecodeine/.venv`, including the
  same reconciliation and NUDO scopes.
- DuckDB `1.5.5` is installed in the tested Win and MAK environments.
- Real RD SQLite reconciliation was read-only: 20 tables, 11 identical,
  1 conflict, 8 candidate-only, 0 legacy-only; writes were false and
  promotion remains `human_review_required`.
- Source hashes after reconciliation remain unchanged: Win `rd.db` is
  `c3ddea0c...`, MAK `rd.db` is `30aead4c...`; physical divergence is kept.
- Optional missing tools are represented as deferred capability states;
  ZIP structure uses the standard-library fallback.

## Safety and next action

- Protected SVG and recovered raw material remain local and unpromoted.
- Do not choose a database writer, merge main, or delete transition refs from
  this handoff alone.
- Stage only the reviewed structural and NUDO/Research scope, run the final
  tests and whitespace checks, then push the scoped checkpoint branches.
