# Phase 190 — bounded Research duplicate ledger

Status: `LEDGER_ONLY; NO_QUARANTINE`

Scope: same-name files directly under `/home/mak/flujo/cultura/mak_research`
and `/home/mak/research`. Outputs, corpus, checkpoints, logs, locks and
subdirectories were excluded. SHA-256 was read only; no file was moved.

## Exact matches

The following 13 documentation/operational files are byte-identical in source
and runtime: `DIGEST.md`, `MAK_RESEARCH.md`, `REPORTE_VSCODE.md`,
`REVISION_CRUZADA.md`, `USO.md`, `buzon_para_antigravity.md`,
`buzon_para_vscode.md`, `cola.service`, `interfaz.service`,
`micelio_guardia.sh`, `research.sh`, `watchdog.sh`, and `webui.sh`.

The following 19 Python files are byte-identical: `corpus_a_micelio.py`,
`correlacionar_archivos.py`, `digest.py`, `estadisticas.py`, `exportar.py`,
`expulsion.py`, `fallback_util.py`, `formato_ensayo.py`, `fructificacion.py`,
`fusion.py`, `ideas_a_micelio.py`, `indice.py`, `interfaz.py`, `pausa.py`,
`puente.py`, `research_lib.py`, `retencion.py`, `run_stub.py`, and
`update_interfaz.py`.

These are exact duplicates but not automatically disposable: several runtime
paths are still referenced by service/crontab declarations, and generated
outputs/mailboxes are part of the department state. The safe future action is
to keep the canonical source and replace only a verified runtime code copy with
a thin projection, one file at a time, with a pre-wrapper quarantine.

## Semantic wrapper matches

`cadena.py`, `cola.py`, `fuentes.py`, `grafo.py`, `memoria.py`, `panel.py`,
`refutar.py`, `research.py`, and `worker.py` differ by design after Phase 183:
runtime files are compatibility projections to canonical implementations. The
runtime wrappers now import successfully in isolated subprocesses. They are
already the correct fusion shape; do not collapse them into one file or remove
the runtime paths.

## Ledger rules and rollback destinations

| Class | Current action | Future reversible destination |
|---|---|---|
| Exact source/runtime docs | Preserve pending consumer check | `context/quarantine/phase190_research_family/<name>.runtime` only if launcher proves redundant |
| Exact source/runtime scripts | Preserve until service/cron consumer is redirected and paused gate passes | Same phase quarantine, with mode/hash/rollback |
| Semantic wrappers | Keep both owners (source + runtime projection) | No quarantine; wrapper is the runtime contract |
| Mailboxes/locks/checkpoints/logs/outputs | Preserve regardless of hash | No cleanup in this ledger |

## Validation

- Direct bounded hash comparison: exit `0`.
- 13 docs/ops exact matches and 19 Python exact matches recorded.
- 9 semantic wrappers remain distinct but import-gated in Phase 183.
- No move, delete, copy, package, service, cron, provider, WIN or Git action.

Next: use this ledger to choose one exact script whose launcher can be proven
inactive or redirected; otherwise leave the duplicate in place and continue
with the next family. No quarantine is authorized by this phase alone.
