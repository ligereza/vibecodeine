# Phase 206 — job status fix and objective reconciliation (LUNA-1)

Date: 2026-08-15 (America/Santiago)

## Concrete fix

`python -m flujo job status /home/mak/flujo/jobs/2026-07-04_eventos-brief`
previously failed with `TypeError: sequence item 0: expected str instance,
dict found` because the RD brief stores product entries as mappings. The CLI
now formats mapping products as `name (value CLP)` and renders mapping pending
items as `key: value`. No brief, database, output or runtime projection was
edited.

Validation:

- `python -m py_compile /home/mak/flujo/src/flujo/cli.py`: exit 0.
- `python -m flujo job status ...`: exit 0; three products and three pending
  items rendered cleanly.
- `python -m flujo knowledge show productora thegrid`: exit 0; canonical YAML
  entity rendered.
- `systemctl --user is-active ...`: four expected `inactive` states; no service
  was started.

## Objective matrix after Phase 206

| # | Objective | State | Evidence/decision |
|---:|---|---|---|
| 1 | RD field data | OPEN / DEFERRED | `rd_datos.db` is valid and empty; no field authority supplied. |
| 2 | Relate RD databases | GATED | `rd.db` catalog and `rd_datos.db` field store remain separate authorities; no merge. |
| 3 | RD mutating routes | DEFERRED | Logo upload, symbol writes, renders and datadrops require bounded authority/rollback. |
| 4 | FLUJO automations | CLASSIFIED | Issue URL workflow is user-confirmed working; paused local automation remains documented, no providers called. |
| 5 | Non-serve FLUJO | GATED / PARTIAL | Read-only CLI surfaces pass; writers and external calls remain deferred. |
| 6 | RD assets | INTEGRATED | 1,742 regular RD files reconcile to local index by path, size and mtime; exact duplicates role-classified. |
| 7 | Dependencies | CLASSIFIED / PARTIAL | Pillow declaration repaired; per-slice runtime compatibility still open. |
| 8 | MAK folder architecture | PROPOSED | Canonical `flujo`, runtime projections, RD corpus, labs, external source and WIN history mapped. |
| 9 | Duplicate documents | LEDGERED / PRESERVE | Exact and semantic families classified; protected evidence not deleted. |
| 10 | Fuse equivalent tools | ROLE-MAPPED | Research/Codex/platform owners and projections mapped; no unsafe fusion. |
| 11 | Full MAK audit | IN PROGRESS | Top-level, consumers and functional surfaces covered incrementally; closeout pending. |
| 12 | Remove confirmed junk | PENDING GATE | Phase 203 has one quarantine candidate only; no move/delete authorized yet. |
| 13 | New Git branches | DEFERRED | Propose only after cleanup and functional gates close; no Git mutation. |

## Next concrete action

Select and document the first bounded write-capable fixture gate. Prefer a
minimal hand-authored job fixture for `job report` only if it can be created
without copying a tree and removed/reverted safely; otherwise proceed with
static audit of remaining writers. Keep all real jobs, RD databases, media,
WIN and Git untouched.

