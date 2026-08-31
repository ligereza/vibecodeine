# Phase 86 — POST duplicate consolidation

## Physical finding

The root department `/home/mak/post` contained only `__init__.py` and
`pipeline.py`. Both were byte-for-byte identical to the canonical
`/home/mak/flujo/cultura/mak_post` implementation and to the historical
`/home/mak/WIN/flujo/cultura/mak_post` copy. Consumer search found the active
registry and tests using `cultura.mak_post`; no active import referenced the
root `post` package.

## Action

Removed the exact redundant root package and its empty regenerable cache:

- `/home/mak/post/__init__.py`
- `/home/mak/post/pipeline.py`
- `/home/mak/post/__pycache__/`
- empty `/home/mak/post/` directory

Kept the canonical implementation and WIN evidence unchanged.

## Foreground validation

- Canonical `cultura.mak_post.pipeline` AST parse -> pass.
- Canonical POST fixture -> `mak-post-package-v1`, status `candidate`,
  `public_gate=human_required`.
- Canonical package compileall -> exit `0`.
- Consumer search after removal found no `/home/mak/post`, `import post` or
  `from post` references in active source/cultura/tests.

## Rollback

The removed root files are recoverable byte-for-byte from
`/home/mak/flujo/cultura/mak_post` or `/home/mak/WIN/flujo/cultura/mak_post`.
No database, job, asset, source-of-truth package or historical evidence was
deleted.

## Decision

Root POST duplicate is `CONSOLIDATED_TO_CANONICAL`; this is a confirmed cleanup
and tool merge by real consumer, not a filename-based deletion.

## Next

Continue with the next MAK department/tool duplicate that has a bounded
consumer and disjoint ownership. Preserve projections and evidence until the
same consumer/rollback gate is met.
