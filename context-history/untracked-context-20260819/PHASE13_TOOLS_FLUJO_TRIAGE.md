Identity: LUNA-13

# Phase 13 — tools / flujo / tests / scripts / docs / RD-Portfolio triage

## Scope

This is semantic house-ordering, not cleanup. The bounded scope was selected from the Phase 1 inventory and existing phase reports: `src/flujo`, `cultura/mak_conductor`, `cultura/mak_plataforma`, selected tests, selected `scripts/`, `tools/`, CLI/script documentation, and the RD/Portfolio bridge tests. Physical evidence was compared on Debian MAK (`/home/mak/flujo`, `/home/mak/plataforma`) and historical Windows (`/home/mak/WIN/flujo`). Inventory rows, names, hashes, age, or branch-like labels were not treated as adoption evidence.

The SVG artwork and its generator are explicitly no_change: `/home/mak/flujo/arte-ascii-readme.svg` and `/home/mak/flujo/tools/update_readme_svg.py` remain untouched. `panel_directivo.py` also remains untouched with its known SyntaxError at line 145. No source, runtime, WIN, logs, JSON/JSONL, locks, databases, credentials, products, services, cron entries, or artwork were modified. Only this report and its CSV were created.

## Bilingual vocabulary matrix

Search and interpretation covered casefolded Spanish/English terms, accented/unaccented forms, aliases/slugs, localized directory labels, human labels, exact machine identifiers, and function/owner/consumer concepts:

| Function | Spanish | English / identifiers |
|---|---|---|
| platform | plataforma, mak_plataforma | platform, `mak_plataforma` |
| work | trabajo | work, job, task |
| guard | guardia, guardia de red, vigía, vigia | watchdog, guardian, watcher |
| journal | bitácora, bitacora | log, ledger, journal |
| state | estado | state, status, salud, health |
| path | carpeta, directorio, dir, ruta | directory, dir, path, route |
| service | servicio, unidad | service, unit, systemd |
| schedule | cron, temporizador | cron, timer, crontab, scheduled |
| queue | cola, pendientes | queue, backlog, pending |
| research | investigación, investigacion | research |
| curation | curatoria, curaduría | curation, curate |
| dispatch | conductor | dispatcher, runner, handler, worker |
| delivery | entrega | delivery, deliver, output, salida |
| backup | respaldo | backup, archive, restore |
| lifecycle | legado, reemplazado, obsoleto | legacy, superseded, obsolete |
| maturity | sin desarrollar | undeveloped |

Residual false-negative risk remains for unlisted project nicknames, opaque JSON payload values, generated data, Unicode transliterations outside the matrix, and consumers invoked indirectly by external UI or unavailable services. This report therefore does not infer LIVE status from importability alone.

## Classification counts

The CSV contains 30 classified physical paths. Counts are:

| Classification | Count |
|---|---:|
| LIVE/ADOPTABLE | 7 |
| SUPERSEDED | 3 |
| WINDOWS_LEGACY | 5 |
| OBSOLETE | 0 |
| UNDEVELOPED | 0 |
| BLOCKED | 6 |
| EVIDENCE_ONLY | 9 |

`OBSOLETE` and `UNDEVELOPED` were not assigned in this bounded sample: no examined path had sufficient evidence to distinguish those states from preserved evidence. Historical and unfinished items remain present as evidence.

## Evidence summary

| Area | Current owner / consumer evidence | Dependency contract | Result |
|---|---|---|---|
| `flujo` CLI | `flujo` maintainer; venv launcher and `python -m flujo` are named consumers | `pyproject.toml` declares `flujo = flujo.cli:app` and dependencies | LIVE/ADOPTABLE for entrypoint and packaging; command behavior beyond help remains untested |
| `mak_conductor` registry | `handler_registry` imported by conductor; 30 handlers observed | JSON payload plus lazy local handlers; delivery/issue handlers have side effects | EVIDENCE_ONLY; runtime/worker paths BLOCKED pending isolated fixture |
| ledger / tandas | `mak_conductor`, `mak_curatoria`, and `flujo.autonomia` import ledger/tandas | local state, locks, logs, SQLite/WAL or runtime paths | ledger LIVE/ADOPTABLE as a contract surface; batch execution EVIDENCE_ONLY |
| delivery / issue bridge | catalog names `repo_delivery` and `issue_render` consumers | locks/logs/jobs, Git/GH, network, queue shadow, render/rclone paths | BLOCKED; even nominal dry routes can persist or observe state |
| scripts | Make/CI documentation names `piezas_generar.py` and `flyer_create_project.py`; CLI supersedes several wrappers | source CLI, Make/CI, render/project dependencies | two LIVE/ADOPTABLE bounded interfaces; wrappers SUPERSEDED, retained |
| tests | test files name CLI, conductor, delivery, and portfolio contracts | pytest plus package/data fixtures | evidence only or BLOCKED; pytest unavailable in both checked environments |
| WIN | physical historical copies under `/home/mak/WIN/flujo` | no current Debian consumer | WINDOWS_LEGACY regardless of matching hash |

The full row-level evidence, sizes, hashes, aliases, verification, owners, consumers, and dependencies is in [PHASE13_TOOLS_FLUJO_TRIAGE.csv](/home/mak/flujo/context/PHASE13_TOOLS_FLUJO_TRIAGE.csv).

## Commands and exit codes

All commands were foreground and side-effect-free unless noted; no external API, SSH, Git, server, worker, cron, systemd, or delivery command was run.

| Command / check | Exit | Observed |
|---|---:|---|
| Read `/home/mak/flujo/agents.md` and `context/LAST_HANDOFF.md` | 0 | required operating contract and prior phase evidence read |
| Phase 1 CSV parse and bounded path selection | 0 | existing inventory used; no unbounded re-scan as inventory authority |
| `PYTHONDONTWRITEBYTECODE=1` AST parse of 188 Python files across selected source/tool roots | 0 | 188 parsed; 0 syntax failures |
| `PYTHONPATH=/home/mak/flujo/src /home/mak/venvs/flujo/bin/python -m flujo --help` | 0 | Debian venv CLI help rendered |
| `/home/mak/venvs/flujo/bin/python -c 'import cultura.mak_conductor.handler_registry...'` | 0 | 30 handlers imported |
| `command -v pytest` | 1 | pytest absent on PATH |
| `/home/mak/venvs/flujo/bin/python -c 'import pytest'` | 1 | `ModuleNotFoundError: No module named pytest` |
| read-only `--help` probes for selected scripts/tools | mixed | `flujo.py` 2, `flujo_health.py` 1, `flujo_daily.py` 0, `piezas_check_outputs.py` 0, conductor probe 0, SVG generator 0 |
| AST parse `/home/mak/plataforma/panel_directivo.py` | 1 | unchanged `SyntaxError` line 145: expected `except` or `finally` |
| `stat`/`sha256sum` on selected MAK/WIN paths | 0 | physical metadata recorded; no mutation |

## Risks and conflicts

- Import success, AST success, matching hashes, a catalog row, or a test filename does not prove a current owner/consumer/dependency contract.
- `mak_conductor.runtime`, `queue_worker`, `entregar.py`, and `puente_issues.py` can touch persistent state, locks, logs, queues, Git/GH, network, or render paths. They were not executed.
- `panel_directivo.py` is blocked by the known SyntaxError and must not be repaired in this phase.
- `pytest` is unavailable, so tests are contract evidence rather than foreground verification. Installing dependencies was out of scope.
- `flujo_health.py --help` returned 1; documentation still names it as a historical render/CI caller. This is a superseded-wrapper conflict, not evidence to revive it.
- Windows copies are evidence only. A matching hash, identical name, or historical caller does not establish Debian adoption.
- `tools/update_readme_svg.py` reports known generator/artwork drift. No artwork normalization or regeneration was attempted.

## No-change decisions

No adoption, merge, delete, move, copy, revive, repair, install, service start, cron edit, or source change was performed. The SVG artwork and generator are no_change. The CSV `decision` field records the semantic disposition (`adoptable`, `blocked`, `evidence_only`, `superseded`, `windows_legacy`, or the explicit no-write note); every row is a filesystem no-change. Obsolete/undeveloped absence of a row is not permission to remove anything: unresolved paths remain in their physical locations and historical evidence remains under WIN.

## Next action

Create a disposable, non-live fixture contract for one `mak_conductor` handler that uses a temporary state root and no network, then run its focused test after a verified pytest dependency is available. Until that owner, consumer, dependency isolation, and foreground result exist, keep `runtime.py`, `queue_worker.py`, delivery/issue bridges, and their tests classified BLOCKED or EVIDENCE_ONLY. Separately, reconcile the explicit Make/CI consumers of `piezas_generar.py` and `flyer_create_project.py` with fixture-backed output checks; do not execute production output generation during triage.
