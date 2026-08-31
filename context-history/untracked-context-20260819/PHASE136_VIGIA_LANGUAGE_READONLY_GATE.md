# Phase 136 - vigia and language department read-only gate

## Scope

The live root departments `/home/mak/vigia` and `/home/mak/lenguaje` were
checked from the MAK surface. Writer/cron/model paths were excluded:
`vigia_guardia.sh`, `lenguaje/hook_barrido.py`, `lenguaje/corregir.py` and
`lenguaje/cron_lexicon.sh` were not executed.

## Foreground validation

- AST parse: `vigia` 1/1 Python files and `lenguaje` 4/4 Python files passed,
  exit 0.
- `/home/mak/vigia/vigia.py --help`: exit 0; CLI exposes source/state,
  notification and bounded compaction controls.
- `/home/mak/lenguaje/medir.py
  /home/mak/flujo/tests/fixtures/idioma_baseline.txt --json`: exit 0; read-only
  measurement returned 2354 words, score 96 and bilingual/ASCII diagnostics.

No source state, lock, ledger, network, notification, model, cron or output
file was changed.

## Decision

Both departments are live MAK surfaces with usable read-only entrypoints. Their
mutating/cron/model paths remain separate consumers and are not merged into
FLUJO or executed during this gate.

## Next action

Add these department statuses to the objective matrix and continue the final
root-surface inventory. Preserve state/locks and do not enable cron or watcher
execution as part of migration.
