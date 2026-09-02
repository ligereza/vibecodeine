# Phase 338 — root installer candidate gate

Date: 2026-08-15 (America/Santiago)

## Candidates

1. `/home/mak/install_mak.sh` — SHA-256
   `46a231f1ce5c44bef388f745f4a32fa763e1df55ee98adbdbc5d67fa200051a`,
   4,066 bytes. It creates/modifies cron and user systemd units, patches
   Research files, may generate a token and invokes dictionary/lexicon work.
2. `/home/mak/instalar.sh` — SHA-256
   `20ac37fd1169db6589c2eee4735f519e2e9840c964a0f7ce1f87df3f20b81de0`,
   1,537 bytes. It installs Docker/Open WebUI, starts/enables Docker and
   creates a persistent container.

Both pass `bash -n` with rc=0, but no active code consumer was found in the
bounded source/tool/cultural/context scan. The only references are audit
documentation. `cron_active=0` remains unchanged.

## Disposition

`QUARANTINE_CANDIDATE_PRESERVE_PROVENANCE`.

These are not active MAK tools and must never be executed automatically. They
are suitable for a later reversible quarantine under
`context/quarantine/<phase>/` after the cleanup ledger records original path,
hash, mode, consumer scan and inverse move. They are not deleted: the first
contains historical MAK installation knowledge, and the second documents an
obsolete external Docker/Open WebUI route.

No file moved or changed, and no installer/service/container/package ran.

