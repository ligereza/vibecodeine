# Phase 181 — RD index reader/writer fixture gate

Status: `PASS`

The existing `cultura/mak_curatoria/ingesta_archivo.py` pipeline was run only
against a temporary source and projection. The live `/home/mak/RD` corpus and
the dated lab SQLite/WAL were not opened by this fixture.

## Fixture and checks

- Source fixture: `a.txt`, `b.txt` (same bytes), `unique.svg`, and one symlink
  to `a.txt`.
- Projection: temporary `archivo_index.sqlite` outside the source root.
- `run(..., full_hash_mb=1, perception_limit=0, timeout=1)` returned exit 0.
- Three regular files were indexed; all three received full hashes.
- The symlink was excluded, matching the source-read policy.
- Exactly one measured `exact_duplicate` relation was created for `a.txt` and
  `b.txt`.
- No perception/provider call was requested (`perception_limit=0`).
- The containment guard rejected an output path inside the source root with
  `--out debe estar fuera de la raiz fuente (solo lectura)`.
- Temporary projection cleanup was handled by the temporary-directory scope;
  no live MAK path was changed and no persistent process remained.

## Interpretation

The indexer is a suitable bounded metadata projection for RD asset triage:
it preserves the source root, excludes symlinks, hashes only within the
configured limit, and creates exact-duplicate relations only from complete
hashes. It does not, by itself, decide which duplicate is the source,
editable master, delivery output, cache, or historical evidence. That role
classification remains the next integration task.

## Validation record

The fixture command exited `0`. No package was installed, no database was
merged, and no real media, provider, mutator, WIN or Git path was changed.
