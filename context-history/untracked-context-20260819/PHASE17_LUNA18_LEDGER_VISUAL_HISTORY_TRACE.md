Identity: LUNA-18

# PHASE17 — Ledger / visual-index historical trace

## Assigned scope

Trace the LIVE/ADOPTABLE source/runtime candidates `ledger.py` and
`visual_index.py` under `cultura/mak_plataforma`, including the duplicate
PHASE13 ledger row. Reconcile PHASE16 no-change evidence with targeted Git
history orientation. No source, runtime, WIN, data, service, queue, provider,
cron, worker or Git state was changed.

## History reading method

Read `/home/mak/Descargas/historia git.odt` as an OpenDocument package and
extracted only its JSON text, top-level summary, `branch_paths`,
`what_is_alive_in_git`, targeted `decision_timeline` events, and
`unresolved_by_design`. The ODT reports schema `git-history-mega-summary-v1`,
6 local refs, 12 remote refs, 403 decision events and 450 selected path
journeys. Because the selected journey index did not contain these two exact
paths, one additional targeted lookup was made against the preserved full
history JSON for the exact `file_lineage` records; the full document was not
loaded into this report. No Git command was run.

History is orientation only. A ref tip is not proof of a live file, a matching
tip is not proof of duplicate physical tools, and commit subjects are inferred
signals rather than user decisions. The branch named `mak` is not the MAK
Linux box. Physical `/home/mak` and `/home/mak/WIN`, plus PHASE16 verification,
remain authoritative.

## Bilingual matrix

Search vocabulary covered function, owner and consumer in addition to literal
paths: `plataforma|platform|mak_plataforma`, `trabajo|work|job|task`,
`guardia|watchdog|guardian|vigia`, `bitácora|bitacora|log|ledger|journal`,
`estado|state|status|salud|health`, `carpeta|directory|dir|ruta|route|path`,
`servicio|service|unit|systemd`, `cron|timer|crontab|scheduled`,
`cola|queue|backlog|pending`, `investigación|investigacion|research`,
`curatoria|curation|curate`, `conductor|dispatcher|runner|handler|worker`,
`entrega|delivery|deliver|output`, `respaldo|backup|archive|restore`,
`legado|legacy`, `obsoleto|obsolete`, `reemplazado|superseded`,
`improvisado|improvised`, and `parche|patch`, with casefold, accents/no
accents, aliases/slugs, localized directories, human labels and exact ASCII
identifiers. Residual false-negative risk: history may omit physical files or
use a different historical spelling; current consumer references were taken
from PHASE16 rather than inferred from names alone.

## Candidate counts

- 4 unique physical candidates: source ledger, runtime ledger, source
  visual_index, runtime visual_index.
- 5 CSV rows: the source ledger is repeated once to preserve the PHASE13
  duplicate semantic row.
- PHASE16 group: 8 rows total, including 4 candidate source/runtime rows, 2
  WIN evidence rows and 2 consumer rows; all existence, AST, parity, import
  and help checks passed, with zero writes.
- Historical exact-path counts: ledger 15 changes, visual_index 2 changes.

## Evidence table

| Physical candidate | Current classification | Historical refs / events | First → last / count | Domain and likely purpose | Current owner / consumer / dependency | Decision |
|---|---|---|---|---|---|---|
| `/home/mak/flujo/cultura/mak_plataforma/ledger.py` | LIVE/ADOPTABLE; PHASE12 also evidence-only; PHASE13 duplicate adoptable row | Local and remote refs including `codex/three-plane-consolidation`, `iskvw`, `main`, `mak`, `mak-svg`, `rd`, and corresponding `origin/*`; first `44e3e7...` “feat(mak): route research formats and ledger batches”; last `04afc1...` “fix: preserve opportunity next actions in ledger” | 2026-08-05 08:49 → 2026-08-09 04:02; 15 changes, statuses A=2/M=13 | MAK; ledger envelope, batch/research routing, opportunity traceability and queue-facing records. History reads as iterative first-working circuit/improvisation, not superseded. Confidence medium. | Owner candidate `mak_plataforma`; consumers `mak_conductor`, `mak_curatoria`, also `flujo.autonomia`/tandas references. Python stdlib plus local state paths; writes JSONL/quarantine and creates directories. | keep candidate, but no promotion: retain PHASE16 `no_change` until disposable fixture, explicit output root and rollback are proven. |
| `/home/mak/flujo/cultura/mak_plataforma/ledger.py` (PHASE13 duplicate row) | Same physical candidate; duplicate matrix representation, not a second tool | Same history; duplicate PHASE13 row is semantic/report duplication, not a Git duplicate-tip claim | Same 15 changes and dates | Same historical ledger circuit; duplicate row does not prove a second implementation or replacement. Confidence medium. | Same owner/consumers/dependencies; PHASE16 found source/runtime hash parity. | keep candidate as one physical path; evidence-only duplicate row, no merge/copy. |
| `/home/mak/plataforma/ledger.py` | LIVE/ADOPTABLE; PHASE12 evidence-only | Same historical source path refs as source runtime projection; no separate physical Git identity established | Historical source lineage: 15 changes, 2026-08-05 → 2026-08-09 | MAK runtime projection of the ledger circuit; likely first-working operational surface, not shown superseded. Confidence medium-low for runtime ownership because history cannot prove physical currentness. | Owner candidate `mak_plataforma`; consumers `mak_conductor` and `mak_curatoria`. Stdlib plus local state; append/quarantine boundaries are live-state risk. Source/runtime hash parity and import/AST passed in PHASE16. | keep candidate, defer adoption/integration pending isolated fixture and owner sign-off. |
| `/home/mak/flujo/cultura/mak_plataforma/visual_index.py` | LIVE/ADOPTABLE | Same local/remote ref families; first `4bb71f...` “integrate MAK portfolio visual circuit”; last `eaa5b2...` “feat: add durable MAK conductor shadow circuit” | 2026-08-10 21:48 → 2026-08-12 08:28; 2 changes, A=1/M=1 | MAK portfolio/curatoria visual indexing and conductor shadow path. History suggests a first-working visual circuit with a later durability patch, not superseded. Confidence medium-low: two events and inferred subjects only. | Owner candidate `mak_plataforma`; consumers `mak_conductor` registry and `mak_curatoria`/portfolio ingestion. Stdlib plus deferred PIL/numpy/torch/mobileclip/faiss and local media/catalog/model paths; can write vectors/index/manifest, temp frames, locks and shadow queue. PIL/numpy found; torch/mobileclip/faiss/standalone `percepcion` unresolved in PHASE16 probe. | keep candidate, defer adoption; do not replace or execute against live state until dependency pinning, fixture roots, lock/GPU/shadow behavior and rollback are verified. |
| `/home/mak/plataforma/visual_index.py` | LIVE/ADOPTABLE | Same historical source lineage; no independent runtime history proven | 2 historical changes, 2026-08-10 → 2026-08-12 | Runtime projection of the portfolio visual circuit; not proven superseded or independently current by Git. Confidence low-medium for physical runtime meaning. | Owner candidate `mak_plataforma`; registry/curatoria consumers. Same optional heavy dependency and derived-output risks; PHASE16 source/runtime parity, AST, import and help passed without build. | defer; retain as candidate, no copy or replacement. |

### Historical interpretation

The ledger path is older and repeatedly extended around research batches,
opportunity queues, traceability and resilient continuation. This supports
“first-working path with later patches” more than “finished canonical tool.”
The visual path appears as a compact portfolio integration followed by a
durable shadow-circuit change. Neither path has a historical signal that proves
supersession. The apparent source/runtime and WIN hash matches are physical
parity evidence only; the WIN ledger copy remains WINDOWS_LEGACY/evidence and
was not treated as a third current candidate.

## Commands and exit codes

- Required context reads with `sed`: exit 0.
- `find context ...` inventory and targeted `grep` of PHASE10–15 CSVs: exit 0;
  matched source/runtime ledger and visual rows plus PHASE13 duplicate ledger.
- ODT package inspection with Python stdlib `zipfile`/XML: exit 0; identified
  `content.xml` and schema/top-level summary without conversationally loading
  the body.
- Targeted JSON extraction from ODT and preserved full-history JSON: exit 0;
  extracted exact lineage counts, dates, refs and event subjects only.
- PHASE16 evidence: source/runtime/WIN existence, AST and hash checks 8/8,
  source/runtime parity 4/4, imports 4/4, help 2/2; all reported exit 0.
- No Git command, source/runtime/WIN modification, write-capable module call,
  queue/provider/worker/service/cron/watchdog/API/network/build or repair was
  run.

## Uncertainty

History confidence is medium for ledger and medium-low for visual_index. The
ODT explicitly leaves physical currentness, duplicate consolidation and user
decision semantics unresolved. Current dependency availability is incomplete
for visual indexing, and ledger/visual functions have side-effect paths that
were intentionally not invoked. “LIVE/ADOPTABLE” remains a candidate label,
not an integration result. PHASE16 `no_change` is incorporated unchanged.

## Next action

Obtain explicit owner approval for isolated fixture roots, then test ledger
read/write boundaries and visual-index derived outputs only inside that
fixture. Pin/probe the optional visual dependencies, hash fixture outputs,
observe rollback, and leave `/home/mak/plataforma` and all live queues/providers
untouched. Until then keep both source/runtime pairs and classify the duplicate
PHASE13 ledger row as evidence-only duplication.
