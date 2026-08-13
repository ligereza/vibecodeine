# LAST_HANDOFF - MAK

Updated: 2026-08-13
Status: local MAK state is authoritative. Git is a reviewed transport
projection; it does not replace MAK or Windows material.

## Authority

- MAK local runtime and data surfaces determine MAK state.
- Windows and MAK have different physical structures; do not force symmetry.
- Contradictory reports are classified, not used to undo local work.
- Machine-readable code and operational metadata use English ASCII where
  practical. Existing Spanish identifiers remain for compatibility.
- RD and Portfolio products keep proper human-facing Spanish.

## NUDO checkpoint

- Checkout: /home/mak/flujo.
- Branch: codex/nudo-rd-evidence.
- Commit: 8219341 feat: checkpoint nudo local consolidation.
- Checkpoint is pushed to origin/codex/nudo-rd-evidence and the worktree is
  clean after the checkpoint.
- NUDO files include source bridging, producer catalog, project diagnosis,
  archive ingestion, Fondart corpus support, source pipeline, and focused
  tests. Originals and local department material were preserved.
- Focused and extended MAK suites passed, including recovered import and
  inferential archaeology.

## MAK local surface

- Independent roots remain in place:
  /home/mak/RD, /home/mak/research, /home/mak/plataforma,
  /home/mak/post, /home/mak/curatoria, /home/mak/codex,
  /home/mak/xio_puente, /home/mak/state, /home/mak/indexes.
- Derived consolidation outputs remain at
  /home/mak/indexes/mak-consolidation-20260813/.
- The original material and department stores were not moved or replaced.
- The debug report classifies 8 atomic evaluations: 3 resolved,
  4 unresolved, and 1 review_required. These are data-review items, not
  test failures.
- PostgreSQL mak_knowledge is a prepared target, not current authority.
- DuckDB 1.5.5 is installed in /home/mak/vibecodeine/.venv, matching Win.

## Transport status

- Windows checkpoint is separate: origin/codex/three-plane-consolidation,
  commit 307631a feat: establish local three-plane knowledge transport.
- No checkpoint was merged to main.
- Operational manifests, databases, indexes, raw media, and provider state
  remain local by design.
- MAK-REPO-SYNC remains commented; no local department store was touched by
  transport.

## Next action

Human review of both pushed checkpoints, followed by deliberate PR review or
merge. Do not promote unrelated local material without a new scoped audit.

## Safety

- Do not reset, clean, mass-move, or overwrite local department material.
- Do not touch README/SVG or raw media during transport work.
- Keep one active handoff in this context directory and update it only after
  verifying current state.
