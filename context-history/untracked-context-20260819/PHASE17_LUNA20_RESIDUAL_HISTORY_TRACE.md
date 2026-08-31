Identity: LUNA-20

## Assigned scope

Residual LIVE/ADOPTABLE rows from the 33-row Phase 15 ledger after the four physical Phase 16 occurrences for `ledger.py` and `visual_index.py` were consumed. The Phase 15 matrix has 33 rows but 32 unique paths; the second `cultura/mak_plataforma/ledger.py` row is intentionally retained and traced as a duplicate candidate row. Result: 29 residual rows, 4 assigned rows, 33/33 candidate rows accounted for. The requested `scripts/piezas_generar.py` is included.

No source, runtime or WIN file was modified. No Git command, service, cron, watchdog, worker, network, SSH, build, API or write-capable runtime was used.

## History reading method

The ODT was read as an archive and its `content.xml` text was parsed only until the embedded JSON object was decoded. The top-level schema is `git-history-mega-summary-v1`; summary metadata says 6 local refs, 12 remote refs, 403 decision events, 450 retained `key_path_journeys`, and 5 duplicate-tip groups. For each residual path I performed exact path lookups in `key_path_journeys` and `decision_timeline`, then recorded only matching dates, subjects, refs and domains. Source and runtime physical paths were not conflated. Missing exact records are reported as `unknown`/`unresolved`, never inferred from file existence or import.

The ODT explicitly says Git is historical orientation only: a ref tip is not physical liveness, a branch named `mak` is not the MAK Linux box, commit subjects are not user decisions, and duplicate tips do not prove duplicate physical tools. Historical matches therefore do not establish a current branch, integration, supersession, or adoption decision.

## Bilingual search matrix

Search vocabulary covered Spanish/English, accented/unaccented forms, casefolding, aliases/slugs, human labels, exact ASCII identifiers, function, owner and consumer: `plataforma/platform/mak_plataforma`; `trabajo/work/job/task`; `guardia/watchdog/guardian/vigia`; `bitácora/bitacora/log/ledger/journal`; `estado/state/status/salud/health`; `carpeta/directory/dir/ruta/route/path`; `servicio/service/unit/systemd`; `cron/timer/crontab/scheduled`; `cola/queue/backlog/pending`; `investigación/investigacion/research`; `curatoria/curation/curate`; `conductor/dispatcher/runner/handler/worker`; `entrega/delivery/deliver/output`; `respaldo/backup/archive/restore`; `legado/legacy`; `obsoleto/obsolete`; `reemplazado/superseded`; `improvisado/improvised`; `parche/patch`.

## Candidate counts

| Surface | Count |
|---|---:|
| Phase 15 LIVE/ADOPTABLE rows | 33 |
| Phase 16 assigned rows that match LIVE/ADOPTABLE | 4 |
| Residual rows traced here | 29 |
| Residual unique paths | 28 |
| Exact retained history journey matches | 2 (`backlog_codex.py`, `pyproject.toml`) |
| Exact timeline-only matches | 13 rows |
| No exact retained summary record | 14 rows |

## Evidence table

The CSV is the exhaustive row-level evidence table with the exact required header. The compact table below makes every residual path visible; `keep` means preserve as a candidate without promotion, while `defer` means preserve and postpone a bounded execution check.

| Physical path / layer | Current classification | History result; likely purpose and physical consumer | Superseded / first-working reading | Recommendation |
|---|---|---|---|---|
| `cultura/mak_plataforma/{trabajo,providers,discernment,mineria_rd,tandas,revisor,capataz,junta,latido,material,backlog_codex}.py` / source | LIVE/ADOPTABLE | MAK platform functions for work, provider/state, discernment, RD mining, batches, review, guardia, scheduling, heartbeat, material and backlog; owner `mak_plataforma`, consumer `mak_conductor` (plus `flujo.autonomia` for providers/tandas); exact timeline for 9, no exact record for 3 | Subjects imply implementation/promotion or circuit work where present; no historical supersession is proven. Missing paths cannot be called first-working or obsolete. | keep candidate |
| `plataforma/{trabajo,providers,discernment,mineria_rd,tandas,revisor,capataz,junta,latido,material,backlog_codex}.py` / runtime | LIVE/ADOPTABLE | Physical Debian runtime layer, owner `mak_plataforma`, same conductor consumers; source/runtime parity is a Phase 15 physical fact except `tandas` divergence | No exact Git record for these runtime paths; source history cannot prove runtime lineage or replacement. | keep candidate |
| `src/flujo/cli.py` / source | LIVE/ADOPTABLE | Debian CLI owner `flujo maintainer`; venv launcher and users consume it; exact timeline, shared/unknown historical domain | No supersession proven; historical subjects are not a decision. | keep candidate |
| `src/flujo/__main__.py` / source | LIVE/ADOPTABLE | Thin `python -m flujo` entrypoint; exact journey absent; physical Phase 13 contract is the authority | Neither superseded nor first-working can be established from summary. | keep candidate |
| `src/flujo/autonomia.py` / consumer | LIVE/ADOPTABLE | Autonomy commands consume `mak_plataforma` ledger/providers/tandas; exact timeline, shared/unknown domain | Subjects suggest routing work through MAK, not a confirmed adoption decision. | keep candidate |
| `pyproject.toml` / contract | LIVE/ADOPTABLE | Packaging/venv contract owned by flujo maintainer; exact 28-change journey; dependencies include setuptools, Typer, pydantic, yaml, rich, jsonschema, requests, boto3 | Not superseded; declaration does not prove installation. | keep candidate |
| duplicate `cultura/mak_plataforma/ledger.py` / platform | LIVE/ADOPTABLE | Residual duplicate matrix row; MAK owner, `mak_conductor` + `mak_curatoria` consumers, stdlib/local state; timeline-only | Duplicate row/tip is not proof of a duplicate physical tool; no supersession claim. | keep candidate |
| `scripts/piezas_generar.py` / script | LIVE/ADOPTABLE | RD production maintainer; Make render and CI consumer; `flujo render run` plus render dependencies; exact history journey absent | No historical evidence supports supersession or first-working status. Generation was not run. | defer |
| `tests/test_cli_smoke.py` / test | LIVE/ADOPTABLE | flujo maintainer; pytest suite consumer; pytest plus flujo package; exact history journey absent | No supersession or first-working claim; pytest remains unavailable per earlier triage. | defer |

The grouped platform rows expand to all 29 CSV records; each record retains its exact path, layer, history refs/branches, dates, event subjects, history confidence, owner, consumer, dependency and decision.

## Commands and exit codes

| Command / operation | Exit | Result |
|---|---:|---|
| `find context -maxdepth 1 -type f ...` | 0 | Located all Phase 10–16 reports. |
| Python stdlib CSV read/count of Phase 15 and Phase 16 | 0 | Confirmed 33 LIVE rows, 4 matched assigned rows, 29 residual rows, 33 accounted rows. |
| Python stdlib ODT ZIP/XML extraction and JSON `raw_decode` | 0 | Decoded schema and targeted summary sections without loading the full evidence document into conversation. |
| Targeted exact path lookups in `key_path_journeys` and `decision_timeline` | 0 | Produced the history fields in the CSV; no Git command was run. |
| Python stdlib CSV validation of the two new files | 0 | Required header present; CSV has 29 data rows. |

## Uncertainty

History confidence is `medium` only for exact retained journeys, `low-medium` for exact timeline-only matches, and `low` where no exact summary record exists. Historical domains are `MAK`, `SHARED_OR_UNKNOWN`, or `unresolved` as recorded. A historical path with promotion-like subjects may be a first-working improvisation, but this report does not relabel it without physical evidence. No candidate is marked superseded, replaced, obsolete, or integrated. Current existence/import is not used as fitness proof.

## Next action

Have the principal reconcile these residual candidates by physical owner/consumer, beginning with the RD render contract for `scripts/piezas_generar.py` and the source/runtime `mak_plataforma` group. Before any adoption, define an isolated fixture, write boundary, dependency availability and rollback proof. Keep all decisions `no_change` until that contract is verified.
