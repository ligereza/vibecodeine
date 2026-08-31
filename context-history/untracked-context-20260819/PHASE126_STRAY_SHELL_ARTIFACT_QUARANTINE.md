# Phase 126 - stray shell artifact quarantine

## Candidate gate

The physical `/home/mak/*` audit found one literal file named `/home/mak/\;`.
Its 55-byte content was escaped JSON-like text followed by `cd` and a
`/home/mak/research` path, consistent with shell-output residue. It also found
six directories whose names were literal backslash-escaped paths to MAK
packages. All six directories were empty. A scoped reference scan found no
consumer references.

## Action

Moved exactly these seven objects to:

`/home/mak/flujo/context/quarantine/phase126_stray_shell_artifacts/`

The relative literal names were preserved. No canonical package, source,
database, evidence, output, rollback or WIN path was touched.

## Foreground validation

The exact move command exited 0 and reported:

```text
stray_file_quarantined=1 empty_dirs_quarantined=6
source_file_remaining=no
source_empty_artifacts_remaining=0
```

Rollback is a path-preserving move from the quarantine directory back to
`/home/mak`, using the seven recorded literal names.

## Decision

`JUNK_CONFIRMED`: yes for these seven shell-residue objects. This decision is
path-specific and does not generalize to other empty files, locks, backups or
rollback trees.

## Next action

Continue the duplicate-document/asset ownership audit, beginning with exact
RD reference PDFs and related job assets. Preserve every source/output/evidence
copy until its human consumer is identified.
