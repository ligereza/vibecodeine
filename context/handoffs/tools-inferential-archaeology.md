# Branch handoff: tools/inferential-archaeology

Branch: `tools/inferential-archaeology`
Contract: `contracts/branches/tools-inferential-archaeology/agents.md`
Owner: `LUNA-502`
Base commit: `536d807`

## Current objective

Protect the read-only archaeology index from output paths that could overwrite
repository source files. Keep all generated artifacts in `/tmp` or ignored
`out/` output space.

## Completed evidence

- Existing unit suite: 27 tests passed.
- Python compilation passed.
- Bounded build with missing external roots wrote SQLite/DuckDB only under
  `/tmp/archaeology-slice.L7bsYD` and indexed 1,014 commits.
- A duplicate bounded run was stopped after it became an unnecessary pending
  temporary process; no repository source was changed.

## Open items

- Promote the durable gate result to the root handoff before branch deletion.

## Next concrete action

The implementation now uses `safe_artifact_path` before loading any history or
session input. It rejects repository source/data/context paths, resolves
symlinks before checking, and allows only external paths or `repo/out`.

Validation results:

- compile and focused unit suite: exit 0, `29 passed`;
- negative CLI output-path probe: exit 2 with the expected guard error;
- foreground build without external roots: exit 0, schema
  `inferential-archaeology-v7`, 1,014 commits indexed;
- foreground report: exit 0, schema `inferential-archaeology-report-v1`;
- `data/rd.db` and README SHA-256 hashes unchanged before/after;
- `git diff --check`: exit 0.

Generated outputs were written only under `/tmp`; no source, database, WIN,
README or service was changed.

## Disposition

`ARCHAEOLOGY_OUTPUT_GUARD_GREEN; READ_ONLY_GATE_GREEN; SOURCE_HASHES_GREEN`

## Next concrete action

Promote the durable gate result to the root handoff, remove this temporary
branch contract/handoff as part of branch closeout, fast-forward `main`, and
delete the short-lived branch.

## Rollback

Only branch-scoped code/tests and this contract/handoff may be reverted.
Source databases, WIN and historical evidence remain untouched.

Last verified: 2026-08-15 America/Santiago.
