# LAST_HANDOFF - MAK

Updated: 2026-08-13
Status: current local checkpoint. Windows and MAK local surfaces determine
what exists and what is current. Git is stale transport evidence until the
final reviewed push.

## Authority

- MAK local runtime and data surfaces are authoritative for MAK state.
- Win and MAK have different physical structures. Do not force symmetry.
- Contradictory reports are preserved and classified; work is not undone.
- Machine-readable code and operational metadata use English ASCII where
  practical. Existing Spanish identifiers remain for compatibility. Human RD
  and Portfolio products keep proper Spanish.
- Git is transport and review projection only after local validation.

## NUDO frozen worktree

- Checkout: /home/mak/flujo.
- Branch: codex/nudo-rd-evidence.
- HEAD: 4b8453cbf17b25431e091a4a6fe3f09a819a0ffb.
- Worktree is intentionally dirty and all local changes are preserved.
- Do not reset, clean, checkout, pull, merge, stash, commit, or push NUDO
  until the final scope audit explicitly authorizes transport.
- NUDO fix: tools/recovered/import_claude_sessions.py now contains
  sanitize_text, public_bytes, and Windows-root handling. Focused test passes.
- NUDO focused battery and the extended department suite pass.

## MAK local surface

- Operational roots remain independent:
/home/mak/RD
/home/mak/research
/home/mak/plataforma
/home/mak/post
/home/mak/curatoria
/home/mak/codex
/home/mak/xio_puente
/home/mak/state
/home/mak/indexes
- Derived consolidation pair:
  /home/mak/indexes/mak-consolidation-20260813/
- Original manifest remains unchanged. Debug report classifies 8 atomic
  evaluations: 3 resolved, 4 unresolved, 1 review_required.
- PostgreSQL mak_knowledge is a prepared target, not current authority.
- Raw files and department stores remain in place.

## Test phase

- DuckDB 1.5.5 is installed in /home/mak/vibecodeine/.venv, matching Win.
- Full focused MAK department suite passed, including recovered import and
  inferential archaeology.
- No code, source media, service, provider, or database bug remains in the
  tested scopes.
- Unresolved/review_required manifest findings are data review items, not
  test failures.

## Next action

Perform a final local diff/scope audit on Win and NUDO. Separate code eligible
for a reviewed Git checkpoint from operational outputs and unrelated dirty
files. Push only the reviewed scope after that audit.

## Safety

- MAK-REPO-SYNC remains commented.
- Do not touch README/SVG, raw media, unrelated services, or local department
  stores during transport.
