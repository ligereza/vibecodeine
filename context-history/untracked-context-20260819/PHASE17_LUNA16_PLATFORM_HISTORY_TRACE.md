Identity: LUNA-16

## Assigned scope

Trace the PHASE15 `LIVE/ADOPTABLE` rows owned by `mak_plataforma` and consumed by `mak_conductor`, excluding `providers.py`, `tandas.py`, `ledger.py` and `visual_index.py`. The assigned slice is the 18-row platform-core group: nine source paths under `/home/mak/flujo/cultura/mak_plataforma` and nine matching runtime paths under `/home/mak/plataforma`. No source, runtime or WIN file was modified.

## History reading method

Read the required handoff, semantic matrix and PHASE10–14 triage reports. Read `/home/mak/Descargas/historia git.odt` as ODT `content.xml` text: parsed its top-level JSON schema/summary and queried only `what_is_alive_in_git`, `branch_paths`, `key_path_journeys`, `decision_timeline`, `duplicate_tip_groups` and `unresolved_by_design`. For assigned paths, queried the targeted `/home/mak/WIN/git_history_context.full.json` `file_lineage` entries and first/last commit subjects. No Git command or live Git state was inspected. Git refs and subjects are historical orientation only; physical `/home/mak` and `/home/mak/WIN` remain authoritative.

ODT summary observed: schema `git-history-mega-summary-v1`; 6 local refs, 12 remote refs, 403 decision events, 450 key path journeys, 5 duplicate-tip groups. Its unresolved rules explicitly say that Git cannot prove physical currency, commit subjects are not confirmed decisions, `mak` is not the MAK Linux box, and duplicate paths require physical comparison.

## Bilingual matrix

Search vocabulary covered Spanish/English, accents/unaccented forms, casefold, aliases/slugs, human labels and exact identifiers, plus function/owner/consumer terms:

`plataforma/platform/mak_plataforma`; `trabajo/work/job/task`; `guardia/watchdog/guardian/vigia`; `bitácora/bitacora/log/ledger/journal`; `estado/state/status/salud/health`; `carpeta/directory/dir/ruta/route/path`; `servicio/service/unit/systemd`; `cron/timer/crontab/scheduled`; `cola/queue/backlog/pending`; `investigación/investigacion/research`; `curatoria/curation/curate`; `conductor/dispatcher/runner/handler/worker`; `entrega/delivery/deliver/output`; `respaldo/backup/archive/restore`; `legado/legacy`; `obsoleto/obsolete`; `reemplazado/superseded`; `improvisado/improvised`; `parche/patch`.

Residual false-negative risk: historical journeys are keyed by repository path, while runtime paths are physical projections absent from the historical lineage index. Human-language or renamed historical paths may therefore be underrepresented. Matching tips do not prove duplicate physical tools.

## Candidate counts

- PHASE15 total: 200 rows; `LIVE/ADOPTABLE`: 33.
- Assigned after owner/consumer filter and four-name exclusion: 18 rows.
- Historical exact source journeys found: 9/9.
- Historical exact runtime journeys found: 0/9; each runtime row is traced through its corresponding source journey and current physical pair evidence.
- Recommendation: keep all 18 as candidates for a later bounded contract review; no integration is claimed.

## Evidence table

| Physical path | Layer | History | Historical purpose/domain | Current owner/consumer/dependency | Decision |
|---|---|---|---|---|---|
| `/home/mak/flujo/cultura/mak_plataforma/trabajo.py` | source | 33 changes; 2026-07-17 to 2026-08-12; MAK; high | Work/job/task and platform state; first event closes MAK organism, last integrates recovered MAK/RD work | `mak_plataforma` / `mak_conductor` / stdlib | keep candidate |
| `/home/mak/plataforma/trabajo.py` | runtime | Corresponding source journey; exact runtime journey absent; medium | Same work/job/task runtime projection | `mak_plataforma` / `mak_conductor` / stdlib | keep candidate |
| `/home/mak/flujo/cultura/mak_plataforma/discernment.py` | source | 12 changes; 2026-08-05 to 2026-08-12; MAK; high | Local discernment/curation ingest gate; last event adds conductor shadow circuit | `mak_plataforma` / `mak_conductor` / stdlib | keep candidate |
| `/home/mak/plataforma/discernment.py` | runtime | Corresponding source journey; exact runtime journey absent; medium | Same discernment/state runtime projection | `mak_plataforma` / `mak_conductor` / stdlib | keep candidate |
| `/home/mak/flujo/cultura/mak_plataforma/mineria_rd.py` | source | 4 changes; 2026-07-22 to 2026-08-12; MAK; high | RD-folder OCR/vision mining and delivery candidates; last event adds conductor shadow circuit | `mak_plataforma` / `mak_conductor` / stdlib | keep candidate |
| `/home/mak/plataforma/mineria_rd.py` | runtime | Corresponding source journey; exact runtime journey absent; medium | Same RD delivery/mining runtime projection | `mak_plataforma` / `mak_conductor` / stdlib | keep candidate |
| `/home/mak/flujo/cultura/mak_plataforma/revisor.py` | source | 6 changes; 2026-07-20 to 2026-08-12; MAK; high | Review/expulsion governance; last event adds conductor shadow circuit | `mak_plataforma` / `mak_conductor` / stdlib | keep candidate |
| `/home/mak/plataforma/revisor.py` | runtime | Corresponding source journey; exact runtime journey absent; medium | Same review/curation state runtime projection | `mak_plataforma` / `mak_conductor` / stdlib | keep candidate |
| `/home/mak/flujo/cultura/mak_plataforma/capataz.py` | source | 11 changes; 2026-07-20 to 2026-08-12; MAK; high | Foreman/guard/watchdog governance; last event adds conductor shadow circuit | `mak_plataforma` / `mak_conductor` / stdlib | keep candidate |
| `/home/mak/plataforma/capataz.py` | runtime | Corresponding source journey; exact runtime journey absent; medium | Same guard/state runtime projection; no worker was started | `mak_plataforma` / `mak_conductor` / stdlib | keep candidate |
| `/home/mak/flujo/cultura/mak_plataforma/junta.py` | source | 5 changes; 2026-07-20 to 2026-08-12; MAK; high | Daily reflection/posture board loading CAPATAZ; no cron execution inferred | `mak_plataforma` / `mak_conductor` / stdlib | keep candidate |
| `/home/mak/plataforma/junta.py` | runtime | Corresponding source journey; exact runtime journey absent; medium | Same board/state runtime projection; no timer/service claim | `mak_plataforma` / `mak_conductor` / stdlib | keep candidate |
| `/home/mak/flujo/cultura/mak_plataforma/latido.py` | source | 3 changes; 2026-07-30 to 2026-08-12; MAK; high | Source gate/heartbeat/health signal; last event adds conductor shadow circuit | `mak_plataforma` / `mak_conductor` / stdlib | keep candidate |
| `/home/mak/plataforma/latido.py` | runtime | Corresponding source journey; exact runtime journey absent; medium | Same health/heartbeat runtime projection; no heartbeat process started | `mak_plataforma` / `mak_conductor` / stdlib | keep candidate |
| `/home/mak/flujo/cultura/mak_plataforma/material.py` | source | 7 changes; 2026-07-26 to 2026-08-12; MAK; high | Operates on user material rather than its own output; delivery/directory handling | `mak_plataforma` / `mak_conductor` / stdlib | keep candidate |
| `/home/mak/plataforma/material.py` | runtime | Corresponding source journey; exact runtime journey absent; medium | Same material/directory delivery runtime projection | `mak_plataforma` / `mak_conductor` / stdlib | keep candidate |
| `/home/mak/flujo/cultura/mak_plataforma/backlog_codex.py` | source | 4 changes; 2026-07-20 to 2026-08-12; MAK; high | Self-filling coder backlog/queue; last event adds durable conductor shadow circuit | `mak_plataforma` / `mak_conductor` / stdlib | keep candidate |
| `/home/mak/plataforma/backlog_codex.py` | runtime | Corresponding source journey; exact runtime journey absent; medium | Same backlog/queue runtime projection; no backlog mutation performed | `mak_plataforma` / `mak_conductor` / stdlib | keep candidate |

## Historical interpretation

All nine exact source journeys are in historical domain `MAK` and share the six local refs `codex/three-plane-consolidation`, `iskvw`, `main`, `mak`, `mak-svg`, `rd` (with corresponding origin refs in the evidence). The shared tips are ref convergence, not duplicate physical implementations. The historical paths are not superseded by an identified replacement in the queried evidence. Several first events are additions or recovered-work integrations, so they are best described as first-working-path or recovered-path signals, not confirmed user decisions. This is especially relevant to `discernment`, `mineria_rd`, `latido` and `backlog_codex`; the present keep recommendation comes from PHASE15 physical owner/consumer/verification evidence, not from commit subjects.

The current PHASE15 rows report source/runtime hash equality, AST/import/help verification and stdlib dependencies; no job, extraction, guard, heartbeat, cron, timer, service, worker or backlog mutation was run. No candidate is marked superseded, replaced or evidence-only on historical evidence alone.

## Commands and exit codes

- `sed -n ... agents.md LAST_HANDOFF.md PHASE15_HOUSE_SEMANTIC_MATRIX.md`: exit 0.
- `find context ... PHASE10–14`: exit 0; all five CSV/MD reports located.
- Python stdlib CSV filter over PHASE15: exit 0; 18 assigned rows identified.
- Python ODT `content.xml` extraction/JSON top-level query: exit 0; schema and requested summary keys read.
- Python targeted query over `/home/mak/WIN/git_history_context.full.json`: exit 0; 9 source journeys returned, 0 exact runtime journeys.
- Initial `rg` discovery attempt: exit 127 (`rg` unavailable); replaced with `find`/Python without changing files.
- No Git command was run. No SSH, network, service, cron, watchdog, worker, provider, build, repair or write-capable runtime function was used.

## Uncertainty

History confidence is high for exact source journeys because each has an indexed path, change count, dates, first/last subjects and refs. Runtime confidence is medium because physical source/runtime equality and PHASE15 verification establish the current pair, while Git history does not index the runtime path. Historical domain/purpose and first-working interpretation remain inferred signals. No branch is called current and no commit is treated as a confirmed decision.

## Next action

Recheck one platform source/runtime pair in a bounded foreground contract review with the named `mak_conductor` consumer, preserving the current no-change boundary. Do not integrate, start services, schedule timers, or promote any pair until its input/output contract and safe write boundary are explicitly verified.
