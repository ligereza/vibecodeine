# Phase 215 — dependency declarations by slice

Date: 2026-08-15 (America/Santiago)

## Declaration boundary

`/home/mak/flujo/requirements.txt` and the base `[project.dependencies]` in
`pyproject.toml` contain the same nine runtime constraints:

`matplotlib`, `pyyaml`, `Pillow`, `pydantic`, `typer`, `rich`, `jsonschema`,
`requests`, `boto3`.

The canonical runtime environment `/home/mak/venvs/flujo` reports:

```text
python -m pip check -> No broken requirements found. (exit 0)
```

The earlier Windows global-environment `pip check` conflicts are not copied
into MAK requirements; they describe a different mixed environment.

## Slice matrix

| Slice | Required base | Optional/add-on | Evidence |
|---|---|---|---|
| FLUJO CLI, jobs, knowledge and read-only RD | `typer`, `rich`, `pyyaml`, `pydantic`, `requests`, `jsonschema` plus base package | none for validated reads | CLI/import smoke passed; `health`, jobs, knowledge and RD reads exit 0 |
| RD catalog and field report | `pyyaml`/SQLite stdlib; CLI base | none for empty report | `rd.database`, `rd.datos`, `rd.informe`, `rd.panel` imports pass; empty report gate passed |
| quote/plano and SVG validation | base; Pillow/matplotlib where used | `render` (`cairosvg`) only for pixel/raster path; no blanket install | prior quote/plano fixture passed; no live render in this phase |
| web hub read surface | base; stdlib HTTP server | `web` (`pywebview`) only for desktop mode | `hub` import and temporary GET server passed without pywebview |
| language/Tilde | Python stdlib plus local Research wrapper for correction | capable-model/provider dependencies only when explicitly invoking correction | 9 language/deploy files compile; isolated language imports pass |
| Research/Codex/Curatoria projections | local canonical `cultura/mak_*` plus per-tool imports | optional qwen/model/GPU paths remain runtime-gated | wrapper/import gates passed; no provider/model call |
| visual index | base plus MobileCLIP model/source path | GPU/backend packages are optional and not rebuilt | read-surface fixture passed; model present |
| deploy sync | Python stdlib, `git` executable, `fcntl`, filesystem permissions | none | deploy script compile passed; sync not executed |
| tests/QA | base | `[project.optional-dependencies].dev` (`pytest`, `pytest-cov`, `duckdb`, `Flask`, `vpype`, `pre-commit`, `pyflakes`) | no install; venv `pytest` availability remains a separate check |

## Decision

No dependency installation or upgrade is justified by this matrix. The MAK
venv is internally consistent for the validated slices. Optional packages
remain slice-specific and should not be promoted into the base runtime merely
because Windows had them installed globally.

## Next concrete action

Run the final static/foreground audit of the remaining active projections and
their entrypoints, then update the 13-objective closeout. Keep provider/GPU,
datadrop, field-ingest and live-mutator paths deferred.

