# Phase 313 — bounded regenerable residue cleanup

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Status: `CONFIRMED_REGENERABLE_CACHE_CLEANED`

## Candidate gate

The candidate set was limited to regular `*.pyc` files inside
`__pycache__` under these explicit active roots:

```text
/home/mak/flujo/src
/home/mak/flujo/cultura
/home/mak/plataforma
/home/mak/research
/home/mak/codex
/home/mak/curatoria
/home/mak/vigia
/home/mak/lenguaje
```

Virtual environments, node modules, rollback, backups, quarantine and logs
were excluded. The preflight found exactly 278 targets. No `.DS_Store` or
temporary file was included; 17 `.bak` files remained protected because they
are source/state evidence rather than confirmed junk.

## Action and validation

```text
preflight target count: 278
bounded unlink of only those 278 *.pyc files: completed
postflight safe target count: 0
source SHA /home/mak/flujo/src/flujo/laser.py:
  before = 3918ff875cc0aaad8fe6c3d0e39c9f10ee5d1c2f331b0fa8dfe3a840b5dcb565
  after  = 3918ff875cc0aaad8fe6c3d0e39c9f10ee5d1c2f331b0fa8dfe3a840b5dcb565
initial health attempt: rc=1, invalid PYTHONPATH (/home/mak/flujo only)
corrected PYTHONPATH=/home/mak/flujo/src:/home/mak/flujo:
  python3 -m flujo health -> rc=0
AST laser/language/ledger: 3/3 AST_OK
active cron entries: 0
MAK units: 5 inactive
```

The removed files are interpreter caches and regenerate from source. No source,
database, evidence, media, output, credentials, WIN content or environment
package was touched.

## Decision and rollback

The 278 files are `JUNK_CONFIRMED` as regenerable cache only. Rollback does
not require restoring bytes: Python recreates them from the unchanged source
on the next import. The 6,024 excluded cache files remain outside this cleanup
because they belong to external/virtual environments or protected surfaces.

## Next action

Use the existing duplicate/tool crosswalk to select one named exact family
with a real consumer and owner. Revalidate ledger/contract/language parity,
then produce a candidate manifest separating `CONSOLIDATE`, `PROTECT`,
`QUARANTINE_CANDIDATE` and `UNRESOLVED`. Do not remove projections merely
because their bytes match.
