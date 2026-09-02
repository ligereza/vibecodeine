# Phase 391 — dependency slices refreshed from current MAK runtime

Date: 2026-08-15 (America/Santiago)

## Source and method

Read-only comparison of `/home/mak/flujo/pyproject.toml`,
`/home/mak/flujo/requirements.txt`, `requirements-dev.txt` and the Windows
probe evidence against `/home/mak/venvs/flujo`. The probe used
`PYTHONDONTWRITEBYTECODE=1`; no package was installed, upgraded or removed.

## Base runtime

| Distribution | Module | Current venv | Slice |
|---|---|---|---|
| matplotlib | matplotlib | 3.11.1 | RD/visual read paths |
| PyYAML | yaml | 6.0.3 | config/intake/knowledge |
| Pillow | PIL | 12.3.0 | RD/assets/export |
| pydantic | pydantic | 2.13.4 | contracts/intake |
| typer | typer | 0.27.1 | CLI |
| rich | rich | 15.0.0 | CLI/output |
| jsonschema | jsonschema | 4.26.0 | JSON/intake contracts |
| requests | requests | 2.34.2 | bounded HTTP-capable code |
| boto3 | boto3 | 1.43.66 | provider slice; currently gated |

All base modules were discoverable and `pip check` returned exit 0.

## Optional and gated slices

| Slice | Declared/observed state | Decision |
|---|---|---|
| Render raster (`cairosvg`) | Declared `render` extra; absent in base venv | Keep optional; fixture/browser fallback remains separate |
| Desktop (`pywebview`, `pystray`) | Declared extras; absent in base venv | Do not promote to server/CLI base |
| Build (`pyinstaller`) | Declared build extra; absent in base venv | Install only for an explicit packaging task |
| Dev (`pytest`, `duckdb`, `vpype`) | Declared dev extras; absent in base venv | Keep out of runtime; use a dedicated test environment |
| Numpy | Available 2.4.6 but not base-declared | Lazy consumer only; do not declare until a named slice requires it |
| Torch, qwen_agent | Absent in this venv; separate environments/evidence exist | Provider/GPU/chat gates remain closed |
| Windows probe candidates | Evidence includes CUDA torch, psycopg, curl_cffi, PyMuPDF, vtracer and others | Never copy wholesale into MAK requirements |

## Decision

The current dependency contract is coherent for the verified local slices.
Optional packages are not failures merely because they are absent from the
base venv. The next dependency change must name a consumer, environment,
entrypoint, expected output and rollback; no requirements file was changed.

Disposition: `DEPENDENCY_SLICES_CURRENT; BASE_GREEN; OPTIONAL_GATED`.
