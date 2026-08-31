Identity: LUNA-22

# Phase 20 — mak_plataforma core contract review

## Scope and counts

- Source group: 9 files under `/home/mak/flujo/cultura/mak_plataforma`.
- Runtime equivalents: 9 files under `/home/mak/plataforma`; metadata/hash only.
- Audited paths: 18; existing: 18; missing: 0.
- Source AST: 9/9 PASS. Runtime content was not inspected beyond metadata/hash.
- Source/runtime pairs: 9/9 byte-identical by SHA-256.
- Status counts: `ADOPTABLE_CANDIDATE` 2 paths, `DEFER` 16 paths; other statuses 0.
- No operational function was executed. No source, runtime, WIN, data, log, lock, DB, credential, artwork or product was modified.

## Required inputs and discrepancy

`/home/mak/flujo/agents.md` was read successfully. The literal requested
`/home/mak/flujo/LAST_HANDOFF.md` is absent (path check exit 1); the present
canonical file `/home/mak/flujo/context/LAST_HANDOFF.md` was read. The
PHASE18 and PHASE17 files were also present and read under `context/`. This
was recorded as provenance and not repaired.

## Commands and exit codes

- `sed -n ... agents.md`: exit 0.
- Handoff presence/discovery: root handoff absent; context copies present; exit 0.
- `command -v rg`: exit 1 (`rg` unavailable); bounded `grep -RInE` fallback used.
- Python stdlib metadata/hash/AST scanner: exit 0; 18 paths, 9 source AST passes, 9 equal source/runtime hashes.
- `timeout 10s python3 cultura/mak_plataforma/mineria_rd.py --help`: exit 0.
- `timeout 10s python3 cultura/mak_plataforma/revisor.py --help`: exit 0.
- No import probe was run: importing these modules can resolve operational integrations and was unnecessary for the static contract.
- No job, `main`, `_main_unlocked`, OCR, subprocess, HTTP, LLM, queue, worker, service, systemd, cron or watchdog operation was run.
- No Git, SSH, network/API/provider call, worker/service start, `repair_mak_sync.py` or persistent write was performed.

## Owner, consumer and dependencies

The candidate owner is `mak_plataforma`. The named consumer is
`cultura.mak_conductor.handler_registry`, with producer identities/stages in
`cultura/mak_conductor/producer_catalog.py`. Handlers are explicit for all
nine modules. `ollama_judge` and `mineria_vision` are active/shadow
boundaries; `cron_tick`, `heartbeat` and `capataz_cycle` are orchestration;
`junta_cycle` is advisory; `pr_merge` is human-gate pending; and
`material_rebuild`/`codex_backlog` are legacy-store pending. This proves a
route, not safe adoption.

Static dependencies are standard library plus local `mak_conductor.runtime`
and deployment fallbacks. Optional operational dependencies were not executed:
Ollama; `pdftotext`; `tesseract`; `gh`/remote PR access; and local
research/platform/RD/curatoria data roots.

## Side effects, inputs, outputs, locks and rollback

- `trabajo.py`: reads platform/research/material/backlog; writes state, logs, JSONL and queue files; uses `fcntl`/`RLock), loopback Research/Codex HTTP and cron-described dispatch. DEFER pending fixture, bounded dry-run and rollback map.
- `discernment.py`: validates review JSON and calls bounded local Ollama with shared GPU/conductor hooks; no direct persistent write pattern found. ADOPTABLE_CANDIDATE only; endpoint/import/fixture remain unverified.
- `mineria_rd.py`: reads `~/RD`, runs OCR subprocesses, calls Ollama, writes resumable state/JSONL/proposals and uses GPU lease. DEFER pending disposable fixture and tool verification.
- `revisor.py`: reads jobs/PR metadata, invokes `gh`/Git subprocesses and writes observation output/logs; `--enforce` can mark/comment/merge. DEFER; rollback/external authority not proven.
- `capataz.py`: reads health/backlog/jobs, may call LLM/loopback services, invokes subprocesses including revisor, writes bitácora/research/backlog state under lock. DEFER pending human gate and rollback.
- `junta.py`: reads health/backlog/jobs and doctrine, calls LLM, writes reflections and `ajustes_junta.json` atomically under lock. DEFER pending fixture and rollback boundary.
- `latido.py`: cron-described heartbeat reads seeds/state, calls loopback Research, writes index/state/log atomically and can dispatch through conductor. DEFER pending timer ownership and rollback.
- `material.py`: reads curatoria fichas, rebuilds `material.jsonl`, uses exclusive lock and conductor dispatch. DEFER pending queue ownership/migration and restore fixture.
- `backlog_codex.py`: reads roles/events/provider health and appends auto-items to `backlog_codex.txt` under lock; catalog says legacy-store pending. DEFER pending queue migration and append rollback.

Some modules have atomic replacement, but no complete per-module
backup/archive/restore procedure was verified. No rollback action was attempted.

## Bilingual search and false-negative risk

Vocabulary covered: `plataforma/platform/mak_plataforma`,
`trabajo/work/job/task`, `guardia/watchdog/guardian/vigia`,
`bitácora/bitacora/log/ledger/journal`, `estado/state/status/salud/health`,
`carpeta/directory/dir/ruta/route/path`, `servicio/service/unit/systemd`,
`cron/timer/crontab/scheduled`, `cola/queue/backlog/pending`,
`investigación/investigacion/research`, `curatoria/curation/curate`,
`conductor/dispatcher/runner/handler/worker`,
`entrega/delivery/deliver/output`, `respaldo/backup/archive/restore`,
`legado/legacy`, `obsoleto/obsolete`, `reemplazado/superseded`,
`improvisado/improvised`, `parche/patch`, plus function/owner/consumer
identifiers.

Residual risk: renamed or human-described paths can evade literal search;
runtime content was intentionally not read; data/log/DB consumers were not
traversed; and static analysis cannot prove environment-dependent effects.
Historical KEEP_CANDIDATE is not safety proof.

## Decisions and next action

`discernment.py` source/runtime remain `ADOPTABLE_CANDIDATE`, with no
promotion claimed. The other 16 paths are `DEFER`, not obsolete, superseded,
legacy or evidence-only. No path is classified `WINDOWS_LEGACY`,
`SUPERSEDED`, `OBSOLETE`, `UNDEVELOPED`, `NO_CHANGE` or
`EVIDENCE_ONLY) on this evidence.

Next action: run a separately authorized disposable foreground contract test
for `discernment.call_ollama` with a local fixture/mock and no network or
persistent writes; then define isolated fixtures and rollback manifests for
the deferred modules. Do not start cron, services, workers, watchdogs or PR
enforcement.

## Integrity and modifications

The companion CSV has the exact requested header and 18 path rows. Source and
runtime hashes are recorded there. Only these two Phase 20 report files were
created; no other modification occurred.

