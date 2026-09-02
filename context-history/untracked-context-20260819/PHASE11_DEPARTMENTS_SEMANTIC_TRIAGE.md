Identity: LUNA-11

# Phase 11 — semantic triage of research, curatoria and codex

## Scope

Bounded semantic house-ordering of the research, curatoria, codex and directly connected culture departments under `/home/mak/flujo/cultura`, their Debian runtime counterparts under `/home/mak`, and corresponding historical material under `/home/mak/WIN`. Direct consumers included `mak_research.interfaz`, `mak_curatoria.diagnostico_proyectos`, `mak_plataforma.research_router`, `mak_plataforma.puente_issues` and `mak_conductor.handler_registry`. No LLM, provider, queue, worker, server, service, cron, network or external API was run. No source, runtime data, WIN material, logs, locks, database, credential or product was modified.

This is a bounded triage, not an unbounded content inventory. Department roots and named interfaces are represented in the CSV; large data/output subtrees were not expanded. Existing Phase 1, 8 and 9 inventories were used as the baseline.

## Classification counts

The CSV contains 40 classified items:

| Status | Count | Meaning in this phase |
|---|---:|---|
| LIVE/ADOPTABLE | 0 | No item met the current Debian 12 owner + consumer + dependency contract + foreground verification bar. |
| SUPERSEDED | 2 | Explicit `.bak` variants retained as evidence; no promotion or deletion. |
| WINDOWS_LEGACY | 6 | WIN roots/files without a current Debian 12 contract. |
| OBSOLETE | 0 | No evidence justified declaring an item obsolete. |
| UNDEVELOPED | 0 | No item was assigned this status without stronger evidence than absence/age. |
| BLOCKED | 29 | Owner/consumer shape is visible, but safe verification/adoption is blocked by providers, queues, service execution, persistent state or network/data contracts. |
| EVIDENCE_ONLY | 3 | Reports/state/findings retained as evidence, not executable adoption candidates. |

Each CSV row has exactly one of the seven permitted statuses. Presence, matching names, imports, hash equality or inventory classification was never treated as proof of live adoption.

## Bilingual vocabulary matrix

Search coverage used casefolded Spanish/English aliases, accented and unaccented forms, localized labels, slugs and exact identifiers. Function, owner and consumer terms were included, not only literals:

| Function | Spanish forms | English forms / identifiers |
|---|---|---|
| platform/work | plataforma, trabajo, tarea | platform, work, job, task, `mak_plataforma`, `trabajo.py` |
| guard/health | guardia, guardián, vigía, estado, salud | watchdog, guardian, vigia, state, status, health |
| log/state/path | bitácora, bitacora, log, diario, estado, carpeta, ruta | ledger, journal, state, directory, dir, path, route |
| service/schedule | servicio, unidad, programado | service, unit, systemd, cron, timer, crontab, scheduled |
| queue/dispatch | cola, pendiente, conductor, entrega | queue, backlog, pending, dispatcher, runner, handler, worker, delivery |
| departments | investigación, investigacion, curatoria, código, codex | research, curation, code, codex |
| archive/lifecycle | respaldo, archivo, legado, obsoleto, reemplazado | backup, archive, restore, legacy, obsolete, superseded |
| development | sin desarrollar | undeveloped |

Aliases and human labels checked included `mak_research`/`research`/`investigación`, `mak_curatoria`/`curatoria`/`curation`, `mak_codex`/`codex`/`code`, `interfaz`/`interface`, `percepción`/`percepcion`/`perception`, `guardia`/`watchdog`/`vigia`, and `conductor`/`dispatcher`/`handler`.

## Evidence summary

| Surface | Owner/consumer evidence | Dependency evidence | Decision |
|---|---|---|---|
| `cultura/mak_research` ↔ `/home/mak/research` | `interfaz.py`, `worker.py`, Hub `/research/`, report directories | `research_lib` uses env/provider/model paths; queue, JSONL, locks and service declarations | BLOCKED |
| `cultura/mak_curatoria` ↔ `/home/mak/curatoria` | `diagnostico_proyectos.py`, `percepcion.py`, guardia and research-memory references | project files, JSONL/log outputs, locks, GPU/external archive paths | BLOCKED |
| `cultura/mak_codex` ↔ `/home/mak/codex` | `interfaz_codex.py`, `worker_codex.py`, pieces/jobs | model/provider boundary, queue/job files, locks and service declaration | BLOCKED |
| direct platform/conductor consumers | `research_router.py`, `puente_issues.py`, `handler_registry.py`; Phase 8/9 observed 30 handlers | route/issue network, shadow queue, delivery locks and lazy side-effect handlers | BLOCKED |
| WIN department copies | historical copies under `WIN/flujo/cultura` only | current Debian owner/consumer/contract absent | WINDOWS_LEGACY |
| reports/state/findings | `DIGEST.md`, curatoria `estado.json`, codex findings | evidence formats only; no execution contract | EVIDENCE_ONLY |

Notable foreground evidence: the source/runtime hashes for the named research, curatoria and codex interfaces match in the checked pairs, but this establishes only content equality. Phase 8 recorded the real `mak_curatoria.diagnostico_proyectos` import and Phase 9 recorded the `handler_registry` import/30 handlers; Phase 9 also established that delivery and issue dry paths still touch locks/logs or network/persistent observation. The source tree’s bounded Python AST parse passed for 47 files. Bash syntax checks passed for the checked guard/research scripts. None of these are live/adoption proofs.

## Commands and exit codes

| Command/check | Exit/result |
|---|---|
| `sed -n '1,240p' /home/mak/flujo/agents.md` and `sed -n '1,260p' context/LAST_HANDOFF.md` | 0; instructions and prior evidence read first |
| `rg --files ...` | 127; `rg` unavailable, bounded `find`/`grep` fallback used |
| `find context -maxdepth 1 -type f` | 0; existing phase reports enumerated |
| targeted `grep -Ein` over Phase 1/8/9 and department paths | 0; bilingual/function/owner/consumer references observed |
| bounded `find ... -maxdepth 2` on culture/runtime/WIN department roots | 0; metadata only; large outputs truncated from display, not copied |
| read-only `stat`/SHA-256 probe for 40 CSV items | 0; exact file hashes recorded where applicable; directories marked non-applicable |
| `PYTHONDONTWRITEBYTECODE=1 python3` AST parse of 47 source Python files | 0; 0 AST errors |
| `bash -n` on checked source shell/service declarations | 0 for each checked file |
| CSV stdlib validation | 0; 40 rows, exact required 13-column header, permitted statuses only |

Files examined directly or through existing reports include `context/PHASE1_INVENTORY.{md,csv}`, `context/PHASE8_MAK_PLATAFORMA_MAP.csv`, `context/PHASE9_HANDLER_DRY_RUN.csv`, all named department roots, the named source/runtime interface files in the CSV, and corresponding `/home/mak/WIN/flujo/cultura` department roots/files. No Git command or Git metadata was used.

## Risks and residual false-negative risk

- Large runtime data/output surfaces such as research corpus/checkpoints and curatoria inbox/output were not expanded; a consumer hidden below the bounded depth could be missed.
- Localized labels, transliterations, aliases and human descriptions not containing the matrix terms can evade literal search. Exact machine identifiers were covered only for the named department maps and direct consumers.
- A matching source/runtime hash can conceal a broken environment, wrong working directory, unavailable dependency or unowned consumer.
- Service files, PID/lock files and logs prove declarations or historical activity only; they do not prove an active healthy unit.
- No model/provider/queue/worker/network execution was permitted, so runtime behavior remains unverified by design.
- `/home/mak/OneDrive` remains inaccessible per handoff; no retry was made.
- The known `panel_directivo.py` SyntaxError at line 145 remains untouched and outside this department triage.

## No-change decisions

No files outside the two assigned evidence files were changed. No source/runtime/WIN item was merged, moved, copied, deleted, revived, repaired or promoted. Historical WIN and backup material remains in place. No services, cron/timers, watchdogs, workers, queues, servers, external APIs or LLMs were started. Artwork SVGs were not inspected for repair or modified.

## Next action

For any future adoption proposal, obtain an explicit current Debian 12 owner, named consumer, dependency contract, isolated fixture/data boundary and a foreground verification command that cannot touch live locks, logs, queues, providers, network or products. Then re-triage the smallest vertical slice. Until those conditions exist, keep the 29 BLOCKED and 6 WINDOWS_LEGACY items as evidence and do not infer adoption from presence, imports, hashes, names or service declarations.
