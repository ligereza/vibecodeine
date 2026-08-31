# Phase 277 — vibecodeine source divergence gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none

## Bounded comparison

Compared `vibecodeine/src` with active `/home/mak/flujo/src` by relative path
and AST symbol surface, without using Git as inventory and without executing
the snapshot.

```text
src files: vibecodeine 111; active flujo 104
common paths: 103
byte-identical common paths: 87
divergent common paths: 16
vibecodeine-only paths: 8 (including 2 non-generated source/contract paths)
active-only paths: 1 (`src/flujo/autonomia.py`)
```

The 16 divergent active modules are:

```text
src/flujo/__init__.py
src/flujo/airdrop.py
src/flujo/cli.py
src/flujo/eventos/blender_nodes_video.py
src/flujo/eventos/flyer_auto.py
src/flujo/index/db.py
src/flujo/intake/email_parser.py
src/flujo/paths.py
src/flujo/rd/README.md
src/flujo/rd/__init__.py
src/flujo/rd/database.py
src/flujo/rd/informe.py
src/flujo/rd/panel.py
src/flujo/route/README.md
src/flujo/route/resolver.py
src/flujo/web/hub.py
```

All listed Python files parse on both sides. The active side retains all
snapshot public symbols except the historical `handoff` name and adds active
symbols, including `autonomia_*`, `rd_testing`, `_readonly_connection`, RD
testing-evidence helpers and route adapters. This is evidence that the active
MAK/FLUJO source is ahead in the examined slice; no old function was promoted.

## Foreground consumer gate

The focused active suite initially exposed one real checkout issue:
`test_hub_comandos.py::test_a_successful_command_notifies_nobody` failed
because the hub child process ran `python -m flujo` without the source
checkout's `src/` on `PYTHONPATH`. The safe fix in
`src/flujo/web/hub.py` preserves the environment and prepends `<repo>/src`
only when that directory exists. Installed deployments keep their normal
environment.

Validation after the fix:

```text
target hub success/failure tests: 2 passed, code 0
focused RD/CLI/hub/intake/airdrop/ISKVW suite: all passed, code 0
```

No package was installed. No hub server, provider, airdrop, database mutator,
worker, external integration or snapshot code was launched. WIN and
`vibecodeine` were untouched.

## Disposition

The active `/home/mak/flujo/src` remains the owner. `vibecodeine/src` remains
historical evidence until the remaining 16 divergences are explained by
consumer, platform and provenance. The snapshot is not a merge source and is
not junk.

## Next concrete action

Continue the snapshot crosswalk with `vibecodeine/cultura/mak_plataforma` and
`mak_research`, the two largest divergent department families. Compare only
active consumers and write a disposition report; do not copy trees or start
workers/services.
