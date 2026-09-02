Identity: LUNA-15

# Phase 16 — First adoptable-group contract review

## Scope and decision

Reviewed the first LIVE/ADOPTABLE group selected from Phase 15: `ledger.py` and `visual_index.py` in source (`/home/mak/flujo/cultura/mak_plataforma`) and runtime (`/home/mak/plataforma`), with real static consumers in `mak_conductor` and `mak_curatoria`. This is verification, not promotion.

Final decision: `no_change` for all reviewed rows. `adoptable_candidate` remains a candidate label only; the contract is not safe to promote because write boundaries, isolated fixtures, dependency availability, and rollback have not been proven without touching live state.

Counts: 8 CSV rows; 4 candidate source/runtime rows; 2 comparable WIN evidence rows; 2 consumer rows; existence 8/8; AST 8/8; source/runtime hash parity 4/4; WIN hash parity 2/2; imports 4/4; help 2/2; writes executed 0; providers/workers/queues/build/append executed 0; source/runtime/WIN changes 0.

## Evidence and commands

- `sed -n '1,240p' agents.md`, `sed -n '1,260p' context/LAST_HANDOFF.md`, `sed -n '1,320p' context/PHASE15_HOUSE_SEMANTIC_MATRIX.md` — exit 0; required context read first.
- `find ... -iname '*ledger*' -o -iname '*visual*index*'` — exit 0; source/runtime and comparable WIN files found. Data ledgers were identified as existing state but not read or mutated.
- Python stdlib path/hash/AST scan over source, runtime and WIN — exit 0; exact sizes and hashes are recorded in the CSV; all six module parses passed.
- Python AST side-effect scan — exit 0; `ledger` exposes `append_item`, `append_unique`, `write_quarantine`, `main`; `visual_index` exposes `build_index` and writes temporary/index artifacts, can call subprocess and `enqueue_shadow`.
- Bilingual semantic scan across `mak_conductor` and `mak_curatoria` — exit 0; real references found in `handler_registry.py`, `diagnostico_proyectos.py`, plus platform hub/runtime references. Search vocabulary is recorded in CSV and covers Spanish/English, accents/no accents, case-insensitive aliases/slugs, human labels and ASCII keys.
- `stat -c '%n|owner=%U:%G|mode=%A|size=%s|mtime=%y' ...` — exit 0; current source/runtime owner is `mak:mak`, mode `-rw-r--r--`.
- `importlib.util.find_spec` dependency probe — exit 0; stdlib, numpy and PIL found; `torch`, `mobileclip`, `faiss` and standalone `percepcion` not resolved in the probe environment. The module keeps heavy imports deferred and remains importable.
- `PYTHONPATH=/home/mak/flujo:/home/mak/flujo/cultura python3 - <<... import ...` — exit 0 for `cultura.mak_plataforma.ledger`, `cultura.mak_plataforma.visual_index`, `cultura.mak_conductor.handler_registry`, and `cultura.mak_curatoria.diagnostico_proyectos`.
- `PYTHONPATH=/home/mak/flujo:/home/mak/flujo/cultura python3 -m cultura.mak_plataforma.ledger --help` — exit 0.
- `PYTHONPATH=/home/mak/flujo:/home/mak/flujo/cultura python3 -m cultura.mak_plataforma.visual_index --help` — exit 0.
- `test ! -e context/PHASE16_FIRST_ADOPTABLE_GROUP_REVIEW.md` and `.csv` — exit 0 before creation; only the two requested files were then created.

## Owner, consumers and dependencies

Current owner candidate for source/runtime is `mak_plataforma`; filesystem owner is `mak:mak`. `mak_conductor/handler_registry.py` lazily references `cultura.mak_plataforma.visual_index.build_index` and multiple ledger-related handlers. `mak_curatoria/diagnostico_proyectos.py` imports ledger envelope/validation functions. The platform hub also reads the ledger and derived visual surface, but was treated as supporting evidence rather than an adoption target.

`ledger.py` uses Python stdlib plus local state paths. `visual_index.py` uses stdlib, deferred PIL/numpy/torch/mobileclip/faiss, local media/catalog/model paths, and conductor runtime hooks. WIN copies are historical evidence only: identical hashes do not establish a current Debian 12 owner or consumer.

## Contract input/output

`ledger.py` accepts JSON work envelopes/items, evidence paths and review payloads. Read/validation functions return normalized records, errors, summaries or quarantine classifications. Mutating functions append JSONL records or quarantine evidence and create parent directories.

`visual_index.py` accepts a bounded portfolio/catalog sample, media assets and a model/output configuration. Read-only helpers return surface/profile/relations. The build contract produces derived `vectors.jsonl`, `vectors.npy`, FAISS index, `neighbors.json` and `manifest.json`; it also uses temporary video frames and lock/GPU/shadow coordination. `mak_conductor` names this operation as stage `visual_index`, but no job was dispatched.

## Side-effect boundary and residual risk

No function with writes was called. In `ledger`, append/quarantine paths use `os.makedirs`, file open/write and JSONL append. In `visual_index`, build paths use `mkdir`, temporary write/replace, FAISS writes, JSON/JSONL writes, `subprocess.run`, and possibly `enqueue_shadow`. Consumers additionally expose SQLite queue, locks, provider, service and output paths. No queue, provider, worker, service, cron, watchdog, network, API, build, append or repair path was run.

Residual risk: a safe contract still needs a disposable fixture with explicit input/output roots, dependency pin/availability proof for the visual encoder, lock/GPU/shadow behavior, and an observed rollback that restores only fixture artifacts. The current evidence cannot prove that against live state, so `no_change` is required.

## Rollback and next action

Rollback for this review is evidence-preserving no-change: source/runtime/WIN and data remain untouched. A future adoption review must use a disposable fixture, hash all fixture outputs before/after, invoke only a read-only or explicitly isolated operation, and remove/restore fixture artifacts after verification. It must not reuse `/home/mak/plataforma` state or invoke live queues/providers/workers.

Next action: obtain an approved isolated fixture and explicit owner sign-off for the ledger path and visual-index output root; then rerun a bounded contract test. Until that exists, retain all eight rows as `no_change` and do not promote or copy either module.

## Files created

- `/home/mak/flujo/context/PHASE16_FIRST_ADOPTABLE_GROUP_REVIEW.md`
- `/home/mak/flujo/context/PHASE16_FIRST_ADOPTABLE_GROUP_REVIEW.csv`
