# LAST_HANDOFF - Faro

Updated: 2026-08-13
Status: current local checkpoint. Windows and MAK local surfaces determine
what exists and what is current. Git is stale transport evidence until the
final reviewed push.

## Authority

- Local Win and MAK surfaces decide what exists and what is current.
- Win and MAK have different physical structures. Do not force symmetry.
- Contradictory reports are preserved and classified; work is not undone.
- Machine-readable code and operational metadata use English ASCII where
  practical. Existing Spanish identifiers remain for compatibility. Human RD
  and Portfolio products keep proper Spanish.
- Git is transport and review projection only after local validation.

## Three-plane implementation

- Git is a small reproducible transport projection.
- Windows is the director and creative production node.
- MAK is the operational and structured-knowledge node.
- Win implementation:
  src/flujo/knowledge/three_plane.py
  src/flujo/knowledge/__main__.py
  schemas/knowledge/three_plane_manifest.schema.json
  docs/THREE_PLANE_CONTRACT.md
  tests/test_three_plane_manifest.py
- Win focused plane, migration, autonomy, README/SVG, and reconciliation
  tests passed. py_compile passed.
- DuckDB 1.5.5 is installed on Win; local requirements declare duckdb>=1.5.0.
- git diff --check passes. Remaining CRLF messages are existing normalization
  warnings in historical files, not errors.

## MAK state

- NUDO checkout remains dirty and preserved:
  /home/mak/flujo, branch codex/nudo-rd-evidence,
  HEAD 4b8453cbf17b25431e091a4a6fe3f09a819a0ffb.
- Do not reset, clean, checkout, pull, merge, stash, commit, or push NUDO
  until the final scope audit explicitly authorizes transport.
- NUDO local fix adds sanitize_text, public_bytes, and Windows-root handling
  to tools/recovered/import_claude_sessions.py. Its focused test passes.
- MAK consolidation outputs remain outside the checkout under
  /home/mak/indexes/mak-consolidation-20260813/.
- The debug report has 8 atomic evaluations: 3 resolved, 4 unresolved, and
  1 review_required. Original manifests remain unchanged.
- MAK installed DuckDB 1.5.5 in /home/mak/vibecodeine/.venv.

## Test phase

- Full focused MAK department suite passed after DuckDB installation,
  including recovered import and inferential archaeology.
- No code, source media, service, provider, or database bug remains in the
  tested scopes.
- Unresolved/review_required manifest findings are data review items, not
  test failures.

## Next action

Perform a final local diff/scope audit on Win and NUDO. Separate code eligible
for a reviewed Git checkpoint from operational outputs and unrelated dirty
files. Push only the reviewed scope after that audit.

## Safety

- No mass folder move, provider call, raw media scan, or README/SVG edit.
- Preserve local department work and NUDO evidence.
