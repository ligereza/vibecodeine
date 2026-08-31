Identity: LUNA-14

# Historical redundancy triage

## Scope

Bounded semantic triage of the historical and possible redundant surfaces assigned to this phase:

- `/home/mak/WIN` and the Phase 1 bounded first-level routes (`claude_sesiones`, `codex`, `flujo`, `manifests`, `updates-20260813`), plus three safe identity files.
- `/home/mak/flujo-deploy` as a parallel deployment generation, with its README, package metadata and Windows hub launcher.
- `/home/mak/rollback` top-level rollback generations listed by the physical bounded listing, and `/home/mak/_archive`.

This is semantic house-ordering, not cleanup. No Git commands, Git history, branch/remotes, SSH, network, service, cron, watchdog, worker, server, API, copy, move, merge, delete, repair or source/runtime change was performed. No artwork SVG was touched. The known `panel_directivo.py` SyntaxError at line 145 was not touched.

Each CSV row has exactly one classification: `LIVE/ADOPTABLE`, `SUPERSEDED`, `WINDOWS_LEGACY`, `OBSOLETE`, `UNDEVELOPED`, `BLOCKED` or `EVIDENCE_ONLY`. The assigned surfaces produced zero `LIVE/ADOPTABLE`: no candidate has all of a current Debian 12 owner, consumer, dependency contract, physical path and foreground verification.

## Bilingual vocabulary matrix

Search and interpretation covered Spanish/English, accented/unaccented, casefolded and alias/slug forms. Function, owner and consumer terms were considered in addition to literal paths. The matrix used was:

| Function | Spanish forms | English forms / identifiers |
|---|---|---|
| platform | plataforma | platform, `mak_plataforma` |
| work | trabajo | work, job, task |
| supervision | guardia, watchdog, guardián, vigía | watchdog, guardian, watch, supervision |
| record | bitácora, bitacora, log | ledger, journal, log |
| state | estado | state, status, salud, health |
| path | carpeta, directorio, dir, ruta | directory, dir, route, path |
| service | servicio, unidad | service, unit, systemd |
| schedule | cron, temporizador | cron, timer, crontab, scheduled |
| queue | cola, pendientes | queue, backlog, pending |
| research | investigación, investigacion | research |
| curation | curatoria, curación | curation, curate |
| dispatcher | conductor | dispatcher, runner, handler, worker |
| delivery | entrega | delivery, deliver, output |
| preservation | respaldo | backup, archive, restore |
| lifecycle | legado, obsoleto, reemplazado, sin desarrollar | legacy, obsolete, superseded, undeveloped |

Residual false-negative risk remains for private/excluded content, deeply nested files outside the assigned bounded routes, localized human labels not containing these terms, and semantics encoded only in binary/session/database contents. Phase 1 explicitly excluded sensitive contents and did not provide an exhaustive recursive per-file inventory of the large trees. This report therefore classifies the bounded routes, not every descendant byte.

## Classification counts

Counts are over the 45 CSV evidence rows, not recursive descendant counts:

| Classification | Rows | Meaning in this scope |
|---|---:|---|
| LIVE/ADOPTABLE | 0 | No complete Debian 12 owner/consumer/dependency/foreground contract observed |
| SUPERSEDED | 3 | Parallel deployment generation with the active authoring baseline elsewhere |
| WINDOWS_LEGACY | 4 | Historical Windows tree/launchers without a current Debian contract |
| OBSOLETE | 4 | Historical guard/supervision generations with no current consumer; preserve as evidence |
| UNDEVELOPED | 1 | Conceptual XIO link surface with no current consumer or verification |
| BLOCKED | 1 | `mak-sync` promotion blocked by unsafe/missing owner and dependency contract |
| EVIDENCE_ONLY | 32 | Provenance, snapshots, manifests and rollback evidence; not runtime candidates |

## Evidence summary

| Surface | Evidence | Semantic decision |
|---|---|---|
| `/home/mak/WIN` | Phase 1 identifies it as a Windows historical archive; README/manifests declare transfer/provenance; Phase 2/6/7/8/9 already compare selected routes and do not establish adoption | `EVIDENCE_ONLY` at root; selected fluxo/launcher routes are `WINDOWS_LEGACY` |
| `/home/mak/flujo-deploy` | Bounded listing shows a large parallel source/data/docs tree, Windows helpers and its own package metadata; active `/home/mak/flujo` has the verified venv CLI contract | Root and package/readme are `SUPERSEDED`; `.bat` launcher is `WINDOWS_LEGACY` |
| `/home/mak/rollback` | Bounded top-level names show atlas/faro/fondart/reconciliation/process/runtime/XIO generations; contents are snapshots, before/after files or units, not mounted consumers | Mostly `EVIDENCE_ONLY`; process supervision generations `OBSOLETE`; `mak-sync` `BLOCKED`; XIO human-link `UNDEVELOPED` |
| `/home/mak/_archive` | Bounded listing contains archive metadata and patch evidence; no restore or merge contract | `EVIDENCE_ONLY` |

The presence of matching names, parallel hashes, dates, labels such as `live`/`final`, or imports in historical material was not treated as proof of liveness. In particular, `faro-conductor-*` remains rollback evidence despite the word conductor; `fondart-*-live` remains evidence because no current owner/consumer/dependency contract was found; and process guard/service snapshots are not revived.

## Commands and exit codes

| Command / check | Exit | Observed result |
|---|---:|---|
| `sed -n '1,240p' agents.md` | 0 | Read MAK agent contract before action |
| `sed -n '1,260p' context/LAST_HANDOFF.md` | 0 | Read current handoff before action |
| `rg --files context` | 127 | `rg` unavailable; fallback used |
| `find context -maxdepth 1 -type f ...` | 0 | Existing phase reports enumerated |
| `grep -Ein ... context/PHASE1* context/PHASE*.md/csv` | 0 | Phase 1 and existing semantic evidence located |
| bounded `find ... -maxdepth 2 ...` on deploy/rollback/WIN | 0 | Physical routes and safe metadata listed; no unbounded tree copy/scan |
| `stat` and `sha256sum` on selected identity files | 0 | Sizes/hashes recorded for README, manifests/source launchers and package metadata |
| Python `csv.DictReader` validation of this CSV | 0 | 45 rows; exact 13-column header; classification counter recorded above |
| Python `find ... -maxdepth 1 ... | wc -l` | 0 | 68 bounded root entries across the four assigned physical surfaces; report rows are semantic route representatives |

No command imported, installed, launched or modified an assigned historical tool. No service, cron, watchdog, worker or network process was started.

## Conflicts and risks

- A physical duplicate or hash match can be a wrapper, parallel generation, replacement, or preserved evidence. This report does not merge or delete on that basis.
- `/home/mak/WIN/flujo` resembles the active package but is explicitly historical Windows material; Debian 12 parity and a current consumer remain unproven.
- `/home/mak/flujo-deploy` contains source-like and operational-looking material, but no current owner and no verified consumer/dependency contract were found in the bounded evidence. Treating its package metadata as adoption would be unsafe.
- Rollback names such as `live`, `final`, `worker`, `service`, `watchdog` and `conductor` are historical labels, not foreground verification.
- `mak-sync` is especially risky: existing phase evidence describes SSH/Git/copy/rollback behavior and missing authorization/contract. It was not executed.
- Process supervision routes could be mistaken for a request to create a permanent service. They remain historical `OBSOLETE` evidence; no service or watchdog was installed.
- Deep descendants, excluded private material, binary/session/database semantics and localized labels may contain additional candidates not represented by this bounded matrix.

## No-change decisions

The only created files are `context/PHASE14_HISTORICAL_REDUNDANCY_TRIAGE.md` and `context/PHASE14_HISTORICAL_REDUNDANCY_TRIAGE.csv`. Source, runtime, WIN, rollback, archive, logs, JSON/JSONL, locks, databases, credentials, artwork and products were unchanged. No path was deleted, moved, copied, merged, revived, repaired or promoted.

## Next action

The principal should consolidate this 45-row historical matrix with the other phase reports. Before any adoption proposal, require an explicitly named Debian 12 owner, real consumer, dependency/interface contract, exact target path and a side-effect-free foreground verification. The next safe historical action is a human-gated review of the single `BLOCKED` `mak-sync` route; do not execute it or alter rollback/WIN evidence while those contract fields are absent.
