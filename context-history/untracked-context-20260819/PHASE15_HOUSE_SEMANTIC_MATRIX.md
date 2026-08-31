# Phase 15 — MAK house semantic matrix

Identity: LUNA

## Objective

Consolidate the five bounded semantic triages into one decision surface for
the physical house. This is a classification and verification checkpoint,
not a merge, cleanup, deletion or deployment step.

## Inputs

- PHASE10_PLATFORM_SEMANTIC_TRIAGE.csv — LUNA-10, 47 rows
- PHASE11_DEPARTMENTS_SEMANTIC_TRIAGE.csv — LUNA-11, 40 rows
- PHASE12_OPERATIONAL_DECLARATIONS_TRIAGE.csv — LUNA-12, 38 rows
- PHASE13_TOOLS_FLUJO_TRIAGE.csv — LUNA-13, 30 rows
- PHASE14_HISTORICAL_REDUNDANCY_TRIAGE.csv — LUNA-14, 45 rows

The derived matrix is
PHASE15_HOUSE_SEMANTIC_MATRIX.csv. It preserves source paths, hashes,
verification, candidate owner/consumer/dependency fields, raw source
decisions and a normalized classification. Normalization uses the status
field because source decision labels were not uniform across agents.

## Consolidated classification

| Classification | Rows | Meaning at this checkpoint |
|---|---:|---|
| LIVE/ADOPTABLE | 33 | Candidate for a bounded owner/consumer contract review; not integrated |
| BLOCKED | 56 | Cannot proceed without an external contract, dependency or safe gate |
| EVIDENCE_ONLY | 66 | Historical/catalog evidence; no current operational claim |
| WINDOWS_LEGACY | 32 | Historical Windows path without a current Debian 12 contract |
| SUPERSEDED | 8 | Replaced or structurally overtaken by another path |
| OBSOLETE | 4 | No current role found; preserve evidence, do not revive |
| UNDEVELOPED | 1 | Path exists as an unfinished direction, not a working tool |
| **Total** | **200** | Five bounded triage inputs |

## Direction

The house is not ready for broad merging. The 33 LIVE/ADOPTABLE rows are
candidate surfaces only. Before any edit, each must pass:

1. physical path and hash recheck;
2. current Debian 12 owner;
3. named consumer and input/output contract;
4. available dependency and entrypoint verification;
5. bounded foreground test with explicit write boundary;
6. rollback or evidence-preservation route.

Blocked, Windows-legacy, superseded, obsolete, undeveloped and evidence-only
rows remain untouched. Duplicate-looking paths are not merged from this
matrix alone.

## Validation

- Five source CSVs read with Python stdlib CSV reader.
- Derived CSV: 200 rows, 14 columns, header and hashes present.
- Derived CSV SHA-256:
  f2e1a79151b0540e46802ec1908bd4dcf57f2bdc9d3ba8979efe904877ecff18
- No source, runtime, WIN, artwork, data, lock, credential, service or Git
  state was modified.

## Next action

Select the first bounded LIVE/ADOPTABLE candidate group by shared owner and
consumer, recheck its physical contract in foreground, and propose the
smallest safe integration. Do not touch the 167 non-adoptable rows or the
known SVG, handler, SSH, repair_mak_sync.py and panel_directivo.py
no-change decisions.

## Last checkpoint

2026-08-14 America/Santiago — five semantic triages consolidated; no
operational promotion performed.
