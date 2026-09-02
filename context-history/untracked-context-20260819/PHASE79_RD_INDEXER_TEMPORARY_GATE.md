# Phase 79 — RD indexer temporary gate

## Objective

Verify the active RD material indexer as a complete read/classification slice
without creating or replacing the operational index.

## Consumer and boundary

- Consumer: `src/flujo/index/indexer.py`, exposed as `flujo hub index`.
- Input: `/home/mak/RD`.
- Temporary output: `/tmp/phase79-index_rd-1786765475.json`.
- Operational output: `/home/mak/flujo/src/flujo/index/index_rd.json` was absent
  before and remains absent after the gate.

## Foreground validation

- `... hub index --out <temp> build --base /home/mak/RD` → exit `0`; indexed
  1,743 files, reported 56.8 GB.
- `... stats` → exit `0`; loaded the temporary index and produced area,
  piece and extension summaries.
- `... find etiqueta --limit 5` → exit `0`; returned five classified local
  paths, including HONGOS.pdf, CREATINA.pdf and MAGNESIO.pdf.
- `... dupes` → exit `0`; no exact hashes were claimed because the build did
  not use `--hash`; near-duplicate analysis completed and reported 532.2 MB
  potential savings.
- `... cleanup` → exit `0`; classified 17 build-cache files / 45.7 MB and
  6.6 GB total estimated candidates. This is analysis only; nothing was
  deleted.
- Temporary JSON size: 490,255 bytes.

## Decision

The indexer is integrated as a safe temporary/read-analysis slice. A
production `build` requires an explicit output policy because it writes an
index, and `--hash` would increase I/O. No source, RD asset, data, evidence or
operational index changed.

## Next

Move to the next unresolved live consumer or externally authorized boundary;
do not turn the cleanup estimate into deletion and do not scan/hash the whole
house again.
