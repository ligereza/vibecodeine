# Phase 311 — vibecodeine source and dependency gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Status: `SEPARATE_SOURCE_CLONE_DIVERGENT_NOT_MERGEABLE`

## Scope

The physical search began at `/home/mak/*` and narrowed to
`/home/mak/vibecodeine`. Git metadata was excluded from the inventory and was
not inspected as history, branch state or migration authority. The local
MAK/FLUJO source and department surfaces were scanned for exact local path
consumers.

## Physical classification

`/home/mak/vibecodeine` is a complete separate source clone/workspace, not a
single tool. Outside its Git metadata it contains 10,655 files and 1,237
directories, including its own `src`, `cultura`, `data`, `projects`, `tools`,
`tests`, `web`, `xio`, external assets and a `.venv`. Its local README defines
the FLUJO/RD/ISKVW/CULTURA/XIO architecture, but it is not the active Linux
owner established in `agents.md`.

The local exact-path scan found zero active references to
`/home/mak/vibecodeine`. Existing code mentions the remote slug
`ligereza/vibecodeine` as a provider/repository boundary; that is not proof
that this local clone is a runtime consumer.

## Bounded comparison

| Pair | Result |
|---|---|
| `cultura/mak_lenguaje/lenguaje_lib.py` | byte-identical |
| `src/flujo/laser.py` | byte-identical |
| `src/flujo/plano/trazador.py` | byte-identical |
| `src/flujo/cli.py` | divergent size/hash |
| `pyproject.toml` | divergent size/hash |
| `requirements.txt` | divergent size/hash |
| `cultura/mak_plataforma/roles.py` | divergent size/hash |
| `cultura/mak_research/fuentes.py` | divergent size/hash |

Bounded file-set counts also diverge: `src/flujo` 104 vs 105 files,
`cultura` 171 vs 142, `data` 50 vs 38, `projects` 309 vs 307, `tools` 151
vs 144 and `tests` 250 vs 208 between active FLUJO and the clone. This
confirms that copying or merging the tree would overwrite semantic decisions,
data contracts and tests in both directions.

## Foreground validation

```text
AST parse selected clone files (CLI, laser, trazador, roles, fuentes): 5/5 OK
SHA-256 bounded source comparison: 3 exact pairs, 5 divergent pairs
exact local path consumer scan: 0 references to /home/mak/vibecodeine
no package installation, provider call, service, Git operation or file move
```

The clone's `.venv`, caches, generated outputs, XIO tree and data were not
executed or modified. No active MAK file changed.

## Decision and rollback

Classify `/home/mak/vibecodeine` as `SEPARATE_SOURCE_CLONE` with
`EXTERNAL_RUNTIME_AND_PROVENANCE` contents. Do not merge it into
`/home/mak/flujo`, do not promote its dependencies, and do not treat its
README branch model as an authorized Git operation. If a future slice is
needed, select one divergent file family with a named consumer and compare it
against the active owner; the rollback is the unchanged clone.

## Next action

Move to the next physical review surface in the architecture queue:
`/home/mak/flujo-deploy` and its explicit `mak_sync_safe.py` consumer. Audit
the deploy boundary statically, without running sync, Git, services or
external providers. Keep the source clone and WIN protected.
