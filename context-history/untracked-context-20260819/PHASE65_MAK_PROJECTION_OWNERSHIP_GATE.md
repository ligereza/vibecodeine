# Phase 65 — MAK source/projection ownership gate

## Evidence

The active FLUJO imports resolve to `cultura.mak_plataforma`,
`cultura.mak_research`, `cultura.mak_curatoria` and `cultura.mak_codex`.
Exact-hash pairs exist in the corresponding root directories, but those root
directories also contain state, logs, locks, reports, virtual environments,
backups and human-facing launchers. They cannot be collapsed as ordinary
duplicates.

Foreground static validation, excluding virtual environments and caches:

| Surface | AST pass | AST fail | Failure meaning |
|---|---:|---:|---|
| `cultura/mak_plataforma` | 48 | 0 | active source parses |
| `/home/mak/plataforma` | 156 | 1 | one known `panel_directivo.py` syntax failure |
| `cultura/mak_curatoria` | 9 | 0 | active source parses |
| `/home/mak/curatoria` | 9 | 0 | projection parses |
| `cultura/mak_research` | 28 | 0 | active source parses |
| `/home/mak/research` | 35 | 0 | projection/runtime files parse |
| `cultura/mak_codex` | 18 | 0 | active source parses |
| `/home/mak/codex` | 125 | 7 | seven generated `piezas/*.py` are malformed artifacts |

The known failures are:

- `/home/mak/plataforma/panel_directivo.py`, line 145: incomplete `try` block;
- seven dated files under `/home/mak/codex/piezas/`: prompt/prototype artifacts
  with invalid or unterminated Python, not imported by the active conductor.

## Ownership decision

For the FLUJO runtime, `cultura/mak_*` is the canonical source. Root
department directories remain protected projections and operational/evidence
surfaces until each launcher and human workflow is audited. The paused
`MAK-REPO-SYNC` declaration that copies whole trees is evidence of historical
projection, not an action for this phase. No sync job was started or edited.

## Merge gate

The next safe merge slice is one pure, exact source/projection module with a
real consumer and no local state dependency. Before changing it, compare:

1. source and projection hashes and normalized text;
2. import path and launcher references in both languages;
3. adjacent state/log/lock files and write locations;
4. foreground AST/import/help behavior;
5. rollback by restoring only the bounded target.

The malformed Codex pieces and the incomplete panel are cleanup/audit
candidates, not merge candidates. They remain untouched until their evidence
and human value are classified.

No source, projection, state, evidence or generated artifact was changed.
