Identity: LUNA-09

# Phase 9 — handler audit and semantic classification

Decision: no_change. No real handler was executed. Isolation could not be proven without violating the original prohibition on live logs, locks, persistent queue/state, network, or external delivery.

## Counts

- HANDLERS: 30 entries.
- PRODUCER_CATALOG: 35 entries.
- Candidate chains: 2 (repo_delivery and issue_render).
- Evidence rows: 9.
- Required bilingual matrix: 15 semantic categories, searched in Spanish and English, accented and unaccented forms, casefold, paths/localized dirs, slugs, human labels, and exact keys.
- rg was unavailable (exit 127); fallback find/grep completed. This is residual false-negative risk.

## Semantic classification

| chain/path | classification | owner | current consumer in MAK Debian 12 | dependency available | operational path | destination recommendation |
|---|---|---|---|---|---|---|
| repo_delivery source chain | BLOCKED | platform.entregar.main named in producer catalog | registry and module consumer exist; no safe execution proof | Python parses; live jobs/state/log/lock and git/gh boundaries remain | not safe; dry-run still locks/logs | retain source as evidence; later replace with isolated no-write harness |
| issue_render source chain | BLOCKED | platform.puente_issues.una_pasada named in producer catalog | registry and module consumer exist; route can enqueue/observe | Python parses; gh/network and durable queue boundaries remain | not safe; dry-run queries GitHub and may persist observation | retain evidence; later replace with networkless fixture harness |
| handler_registry.py and producer catalog | EVIDENCE_ONLY | LUNA principal / conductor candidate owner | canonical mapping present; audit does not promote it | lazy imports; runtime store side effects available, not isolated | inventory/contract evidence only | retain logically; do not integrate or duplicate |
| /home/mak/WIN copies | WINDOWS_LEGACY | historical Windows owner unknown | no demonstrated current Debian consumer | local files exist; contract parity not proven | historical route not operationally adoptable | retain evidence or archive logically later; do not move/delete/promote |
| panel_directivo.py | BLOCKED | existing runtime panel | not a handler consumer | compile fails at line 145 | no operational path | retain unchanged as evidence; separate authorization required |

Classification rule: a name/hash match is not adoption. Adoption requires current owner, current MAK Debian 12 consumer, available dependency, and working contract/path. No item is labeled LIVE/ADOPTABLE, SUPERSEDED, OBSOLETE, or UNDEVELOPED because inspected evidence does not prove those stronger states.

## Owner, consumer, contract

repo_delivery: payload_json maps to argv list; registry calls cultura.mak_plataforma.entregar.main; output is validated/result_code plus repo_delivery_manifest. producer_catalog marks human_gate_pending publication.

issue_render: payload_json maps to dry_run and optional issue; registry calls una_pasada(dry_run, solo); output is validated/result integer. producer_catalog marks active_and_shadow GPU work.

## Bilingual matrix

plataforma/platform/mak_plataforma; trabajo/work/job/task; guardia/watchdog/guardian/vigia; bitácora/bitacora/log/ledger/journal; estado/state/status/salud/health; carpeta/directory/dir/ruta/route/path; servicio/service/unit/systemd; cron/timer/crontab/scheduled; cola/queue/backlog/pending; investigación/investigacion/research; curatoria/curation/curate; conductor/dispatcher/runner/handler/worker; entrega/delivery/deliver/output; respaldo/backup/archive/restore; labels/labels humanos/slug. Exact routes: handler_for_stage, repo_delivery, issue_render, platform.entregar.main, platform.puente_issues.una_pasada, QueueStore, dispatch_sync, LOCK, STATE, LOG, BANDEJA and WIN paths.

## Side-effect audit

repo_delivery requested command (not run): python3 /home/mak/flujo/cultura/mak_plataforma/entregar.py --dry-run --limit 0. main enters _exclusive_delivery_lock even in dry-run and opens/creates /home/mak/plataforma/codex_delivered.json.lock. _main_unlocked calls log(), appending /home/mak/plataforma/logs/entregar.log. limit 0 does not prove no-write isolation. Non-dry code contains git and gh publication; neither was called.

issue_render requested payload (not run): {dry_run: true}. una_pasada can dispatch_sync into durable SQLite, or enqueue_shadow/observe_shadow; it calls gh issue list against GitHub. Dry-run skips render/upload/close but does not eliminate network or persistent observation. No handler invocation occurred.

## Commands, codes, stdout/stderr

1. sed source inspection: exit 0; stdout showed registry, contracts, side effects; stderr empty.
2. rg attempt: exit 127; stderr said rg: orden no encontrada. find/grep fallback: exit 0.
3. AST count: exit 0; stdout HANDLERS 30 and PRODUCER_CATALOG 35.
4. stat and sha256sum before/after: exit 0; audited source/runtime/WIN hashes and sizes equal; values are in CSV.
5. compile-from-text panel_directivo.py: exit 1; SyntaxError line 145, expected except or finally; no pyc written.
6. compile-from-text rollback copy: exit 1; same line 145 error; no repair.
7. No handler command was issued: handler exit code/stdout/stderr are N/A by safety decision.

## Touched paths and rollback

Only these evidence files were created/edited:

- /home/mak/flujo/context/PHASE9_HANDLER_DRY_RUN.md
- /home/mak/flujo/context/PHASE9_HANDLER_DRY_RUN.csv

No source, runtime, WIN, log, JSON/JSONL, lock, database, credential, or state file changed. No rollback was needed.

## Residual false negatives

Search cannot prove absence of aliases hidden in generated files, Unicode normalization variants, symlinked/localized directories, dynamic imports, environment-variable paths, shell aliases, or producers with unrelated names. Fallback traversal differs from rg semantics. WIN was sampled and not promoted. These risks do not change no_change because visible lock/log/network/persistence boundaries already fail the safety gate.

## Result and next action

Result: audit complete; dry-run not executed; decision no_change. panel_directivo.py remains SyntaxError at line 145 and unchanged. No source/runtime/WIN divergence was promoted.

Next action: reassess only after an authorized harness proves temporary isolated home/config/queue, blocks network and external commands, suppresses live logging/locks, and measures before/after paths. Until then retain candidates as evidence and do not move, delete, integrate, or force historical tools.
