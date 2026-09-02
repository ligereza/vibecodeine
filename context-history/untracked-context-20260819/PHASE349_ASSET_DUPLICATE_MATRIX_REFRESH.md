# Phase 349 — asset and duplicate matrix refresh

Date: 2026-08-15 (America/Santiago)

| Phase | Surface | Evidence | Disposition | Real mutation |
|---|---|---|---|---|
| 347 | `flujo.index.indexer._basekey` | underscore/dash normalization fixture; exact hash and grouping checks | `FIXED_MINIMAL_GROUPING_BUG` | source only; no asset/index move |
| 348 | `flujo.index.db` | temporary SQLite missing-path, status-list and duplicate-group checks | `VERIFIED_READONLY_INDEX_CONSUMER` | temporary DB only |

## Current decision

The indexer and its database consumer form one compatible read/classification
slice. Filename grouping is now stable across spaces, underscores and version
tokens, while the database layer remains read-only for list and duplicate
queries. The real index must not be rebuilt as part of this refresh because
that would be a broader data mutation and is not required to establish the
consumer contract.

## Open boundary

The next review is a path-level asset validator/consumer outside the index
database. It must be tested with temporary fixtures before any real asset is
rewritten, moved or deleted. Exact duplicates, historical evidence and
generated products remain protected until a later disposition has an explicit
owner and rollback.
