# Phase 151 — non-serve FLUJO CLI foreground gate

Date: 2026-08-15

## Runtime ownership

The active entrypoint is `/home/mak/venvs/flujo/bin/flujo`, generated from the
`pyproject.toml` entrypoint `flujo = "flujo.cli:app"`; its imports resolve to
`/home/mak/flujo/src/flujo`. `scripts/flujo.py` is a legacy dispatcher with
explicit retired-command behavior and is not the active runtime. Its tests
confirm that boundary, so it was not replaced or deleted.

## Foreground results

| command | result | mutation |
|---|---|---|
| `flujo version` | exit 0, version `0.56.1` | none |
| `flujo health` | exit 0, jobs/inbox/projects/scripts/tools/docs OK | none |
| `flujo doctor` | exit 0, Python/repo/workspace/index/encoding checks OK | none |
| `flujo suplementos list` | exit 0, 8 approved supplements listed | none |
| `flujo rd-db --help` | exit 0, build/read command contract visible | none |
| `flujo rd-datos --help` | exit 0, ingest/informe privacy contract visible | none |
| `flujo rd-db packs` | exit 0, 3 canonical packs returned | none |
| `flujo rd-db eventos` | exit 0, 2 event templates returned | none |

Before/after stat of `/home/mak/flujo/data/rd.db` was identical
(`mtime=1786763640`, `size=2699264`) across the read commands. No hub, serve,
generator, Vite or other persistent process remained.

## Decision

The non-serve CLI entrypoint and representative RD consumers are integrated at
runtime. The legacy dispatcher remains classified as a compatibility/history
surface; its retired commands must not be promoted back into the active CLI.
The broad CLI objective remains partial only because the repository's pytest
dependency is absent from the configured environment; no package was
installed.

## Next action

Inspect and run the local FLUJO automation contract next, keeping provider-backed
writers and external issue/email mutations behind their explicit gates.

