Identity: LUNA-17

## Assigned scope

Trace the physical source/runtime candidates for `providers.py` and `tandas.py` consumed by `mak_conductor` and `flujo.autonomia`. The four assigned rows are:

- `/home/mak/flujo/cultura/mak_plataforma/providers.py`
- `/home/mak/flujo/cultura/mak_plataforma/tandas.py`
- `/home/mak/plataforma/providers.py`
- `/home/mak/plataforma/tandas.py`

The Windows copies were used only as historical contrast: `/home/mak/WIN/flujo/cultura/mak_plataforma/providers.py` and `tandas.py` are already classified WINDOWS_LEGACY. No source, runtime or WIN file was changed.

## History reading method

`/home/mak/Descargas/historia git.odt` is an OpenDocument wrapper whose `content.xml` contains JSON schema `git-history-mega-summary-v1`. I inspected only its top-level summary and targeted records in `decision_timeline`, plus the branch/ref summary. I queried exact historical paths for `cultura/mak_plataforma/providers.py`, `cultura/mak_plataforma/tandas.py`, and `src/flujo/autonomia.py`; I did not load the whole evidence document into the conversation and did not run Git commands.

The document reports historical orientation only. Matching refs (`main`, `mak`, `iskvw`, `rd`, `mak-svg`, `codex/three-plane-consolidation`, and associated remote refs) indicate ref convergence, not a current branch, duplicate physical tool, or user decision. The historical `mak` name is not treated as the MAK Linux box.

## Bilingual search matrix

The search vocabulary covered exact identifiers, aliases/slugs, owner and consumer names, and Spanish/English forms with casefold and accent variants:

`plataforma/platform/mak_plataforma`; `trabajo/work/job/task`; `guardia/watchdog/guardian/vigia`; `bitácora/bitacora/log/ledger/journal`; `estado/state/status/salud/health`; `carpeta/directory/dir/ruta/route/path`; `servicio/service/unit/systemd`; `cron/timer/crontab/scheduled`; `cola/queue/backlog/pending`; `investigación/investigacion/research`; `curatoria/curation/curate`; `conductor/dispatcher/runner/handler/worker`; `entrega/delivery/deliver/output`; `respaldo/backup/archive/restore`; `legado/legacy`; `obsoleto/obsolete`; `reemplazado/superseded`; `improvisado/improvised`; `parche/patch`.

## Candidate counts

- Assigned physical candidates traced: **4/4**.
- Source/runtime provider-batch candidates: 4; current Phase15 surface classification: LIVE/ADOPTABLE.
- Batch execution status: EVIDENCE_ONLY until an isolated fixture and write boundary are verified.
- Historical targeted path events: providers 5, tandas 10, autonomia 3.
- Historical domain: MAK for all targeted events.
- Historical refs observed per targeted path: 12 ref names (local, remote and dependency refs); none is asserted current.

## Evidence table

| Candidate | Physical layer and current classification | History | Likely purpose and current contract | Superseded / first-working assessment | Decision |
|---|---|---|---|---|---|
| `flujo/cultura/mak_plataforma/providers.py` | source; LIVE/ADOPTABLE | 2026-08-05 to 2026-08-09; 5 events; medium confidence | Provider registry/routing and bounded calls; owner `mak_plataforma`; consumers `mak_conductor`, `flujo.autonomia`; stdlib plus optional credentials, HTTP providers and Ollama/local GPU | Not superseded. Subjects indicate an evolving adapter: autonomous batch promotion, deployed credential loading, Ollama schema, provider-drift repair and portfolio closure. It may include first-working improvisation; subjects are inferred, not decisions. | **Keep candidate** as contract surface; no provider call or promotion. |
| `flujo/cultura/mak_plataforma/tandas.py` | source; LIVE/ADOPTABLE surface, EVIDENCE_ONLY for execution | 2026-08-05 to 2026-08-09; 10 events; medium confidence | Provider-agnostic batch brief, validation, ingestion and ledger writes; owner `mak_plataforma`; consumers `mak_conductor`, `flujo.autonomia`; depends on `providers.py`, `ledger.py`, JSONL/state paths | No evidence of supersession. Repeated schema, budget, manifest and review repairs strongly resemble a first-working/improvised path that was iterated into a contract; not proof of viability. | **Defer** execution pending fixture and write-boundary verification. |
| `/home/mak/plataforma/providers.py` | runtime; LIVE/ADOPTABLE | Same source-path history as above; 5 events; medium confidence | Runtime projection consumed by registry/autonomia imports; provider/network and GPU boundary remains unverified | Historical Git does not establish this physical deployment. Source/runtime hash parity is evidence of correspondence, not fitness. | **Defer** runtime promotion pending Debian/provider contract. |
| `/home/mak/plataforma/tandas.py` | runtime; LIVE/ADOPTABLE surface, EVIDENCE_ONLY for execution | Same source-path history as above; 10 events; medium confidence | Runtime batch path with local ledgers/state; consumed by conductor/autonomia imports | Phase10 records source/runtime divergence and Phase13 records no executed batch. Historical path is best read as a repaired first-working route, not superseded and not confirmed viable. | **Defer**; preserve and test only in disposable state. |

## Targeted historical events

`providers.py` first appears in the targeted timeline under `feat(mak): promote autonomous batch ledger circuit` (2026-08-05), then receives credential-path, Ollama/schema and provider-drift repairs, ending in `feat: close MAK portfolio and README circuit` (2026-08-09). `tandas.py` begins with `feat(mak): route research formats and ledger batches` and receives ten batch/schema/ledger/review repairs through `fix: preserve safe opportunity review actions` (2026-08-09). `src/flujo/autonomia.py` has three targeted events on 2026-08-06: route external batches through MAK, enforce batch budgets/judge traceability, and include opportunities in autonomy rounds.

These subjects support “iterative first-working path” as a cautious historical interpretation. They do not prove a branch is current, a commit is a confirmed decision, or that credentials, providers, network, queues, ledgers, services or workers are healthy.

## Commands and exit codes

| Command | Exit | Result |
|---|---:|---|
| `sed -n ... agents.md LAST_HANDOFF.md PHASE15_HOUSE_SEMANTIC_MATRIX.md` | 0 | Required governance and prior classifications read. |
| `find context ...` / targeted `grep` over PHASE10–14 reports | 0 | Assigned source/runtime/WIN rows and owner/consumer notes located. |
| Python stdlib ODT `zipfile` + XML parser + JSON parser top-level inspection | 0 | Schema and top-level summary inspected without conversationally loading full evidence. |
| Python stdlib targeted ODT timeline query | 0 | Exact provider/tandas/autonomia events, dates, counts, subjects and refs extracted. |
| Read-only source `grep` for imports/functions/provider/batch contracts | 0 | Current dependencies and consumers confirmed statically. |
| Git commands, provider calls, workers, services, cron, SSH, network, builds | not run | Explicitly prohibited by mission. |

## Uncertainty

History confidence is **medium** because the ODT provides path/event summaries and inferred commit subjects, but does not establish current physical ownership or runtime health. Runtime paths have no independent historical path journey in the targeted evidence; their historical fields are mapped from the corresponding `cultura/mak_plataforma` source path and labeled accordingly. Phase10’s LIVE/ADOPTABLE label means candidate surface only. Phase13’s EVIDENCE_ONLY label for `tandas` execution is the controlling caution: imports and help do not prove a safe batch run. The provider path additionally crosses credentials, external HTTP, Ollama/GPU and optional network boundaries.

## Next action

Keep the provider source as a candidate contract. Defer both `tandas` execution and runtime promotion until the principal names a Debian 12 owner, disposable state root, provider-disabled fixture path, dependency contract and a bounded foreground test that cannot write live ledgers, logs, queues, locks or products. No replacement is justified by the historical evidence; no integration should be inferred from existence, import, hash or ref matching.
