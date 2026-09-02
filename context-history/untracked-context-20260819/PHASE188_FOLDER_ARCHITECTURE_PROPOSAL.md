# Phase 188 — reversible MAK folder architecture proposal

Status: `PROPOSAL_ONLY; NO_MOVES`

This is the order for the house after consumer gates. It is not a delete,
move, branch, or Git operation.

## Ownership map

| Layer | Owner/path | Rule |
|---|---|---|
| Authoring source | `/home/mak/flujo` | One semantic owner for active MAK code and tests. |
| Active runtime projections | `/home/mak/research`, `/home/mak/codex`, `/home/mak/curatoria`, `/home/mak/plataforma`, `/home/mak/vigia` | One projection per department; wrappers delegate to `flujo/cultura/*` when a canonical owner exists. |
| RD creative corpus | `/home/mak/RD` | Real creative/source/editable/delivery assets; classify by consumer before any merge. |
| Operational catalog | `/home/mak/flujo/data/rd.db` | Regenerable catalog projection; read-only for consumers. |
| Field data | `/home/mak/flujo/data/rd_datos.db` | Separate privacy-first store; currently empty; never merge into `rd.db`. |
| Derived/lab evidence | `/home/mak/labs` | Timestamped provenance, SQLite/WAL, summaries and pending work; preserve and never promote blindly. |
| Runtime outputs/state | `/home/mak/research`, `/home/mak/curatoria`, `/home/mak/plataforma`, and their declared state dirs | Keep outputs with their consumer and mark generated/state separately from source. |
| External applications | `/home/mak/apps` | Installed binaries/resources; never merge into Python source. |
| External source/dependencies | `/home/mak/src` | Source evidence such as MobileCLIP; connect by declared consumer, never copy whole trees. |
| Historical archive | `/home/mak/WIN` | Historical source only; never active runtime or cleanup target. |
| Audit/quarantine | `/home/mak/flujo/context/quarantine/<phase>` | Reversible candidates only, with original path/hash/reason/consumer/rollback. |

## Duplicate/document/tool policy

1. Exact hash is a candidate signal, not deletion authority. First classify
   source master, editable project, delivery output, cache, generated result,
   historical evidence, and active consumer.
2. Exact duplicate with one active consumer: retain the canonical owner and
   replace the secondary code path with a thin projection only after a
   foreground gate; preserve the previous file in phase quarantine.
3. Exact duplicate with no consumer: quarantine reversibly, never delete
   immediately. Generated products, databases, logs, locks and memories stay
   preserved even when their bytes match another artifact.
4. Semantic variants are not duplicates. Compare structure/content and keep
   both until a human or consumer contract identifies the winner.
5. Similar tools merge by consumer contract, not by filename: Research has one
   active UI/worker owner; Codex has one semantic engine; RD catalog/data are
   separate; visual index remains a derived read surface; XIO is excluded as
   requested and n8n is discarded.
6. Documents merge by provenance: canonical policy/spec first, dated evidence
   retained as evidence, generated/readme artwork untouched. No SVG README
   replacement.

## Ordered implementation sequence

1. Freeze this map and refresh the top-level inventory from `/home/mak/*`.
2. Complete consumer/route/dependency gates for remaining active projections.
3. Produce a path-level duplicate ledger with hashes and role labels.
4. Select one canonical owner for each equivalent tool family.
5. Add/update thin runtime projections and validate foreground.
6. Move only explicitly classified, reversible candidates into phase quarantine.
7. Re-run compile/import/fixture/consumer gates and record rollback paths.
8. Leave `RD`, databases, labs, generated outputs, memories, credentials,
   `WIN` and Git history intact unless a separate authority explicitly changes
   that rule.
9. Only after the house is stable, propose the new Git branch system; no Git
   branch or history action is part of this phase.

## Current decisions already supported by evidence

- `/home/mak/research/interfaz.py` owns the active Research UI; the old
  `/home/mak/plataforma/interfaz.py` has no launcher reference and is a
  preserved legacy candidate.
- `/home/mak/flujo/cultura/mak_*` owns active semantics where the runtime has a
  wrapper; the wrapper is tested independently.
- `/home/mak/RD` is fully represented by its own lab-index source-key rows by
  path/size/mtime; seven other index rows belong to an external render root.
- `panel_directivo.py` is incomplete evidence, not a safe merge target.

## Rollback requirement

Every future move must have a phase quarantine path, original absolute path,
SHA-256, file mode, consumer search result, command, exit code, and a reverse
move command. Until that ledger exists, no cleanup move is authorized.
