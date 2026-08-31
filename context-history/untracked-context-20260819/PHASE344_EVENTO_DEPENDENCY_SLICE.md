# Phase 344 — EVENTO dependency slice

Date: 2026-08-15 (America/Santiago)

## Consumer

`/home/mak/flujo/src/flujo/eventos/flyer_auto.py` is the consumer for the
EVENTO flyer handoff.

| Dependency | Role | Current state | Required for validated local path |
|---|---|---|---|
| Python stdlib (`json`, `pathlib`, `urllib`, `subprocess`, etc.) | parsing, temp paths, fallback/download/process boundary | present | yes |
| Pillow | palette/input image processing | present | yes |
| `parth_dl` | optional Instagram mirror/download route | missing | no, mocked/local fallback path works |
| `curl_cffi` | optional Chrome-like HTTP/embed route | missing | no, external route gated |
| `/home/mak/blender/blender` | optional render handoff | present 4.5.4 | no for non-render local path; required only for real render |
| Photoshop/droplet | Windows-specific handoff | not a Linux package contract | no for Linux validation |

Static AST parsing passed. Module discovery reported Pillow present and
`parth_dl`/`curl_cffi` missing. Phase 343's temporary fixture passed without
the missing modules and without network/process calls.

## Disposition

`BASE_EVENTO_PATH_VERIFIED; OPTIONAL_EXTERNAL_EDGES_GATED`.

Do not add the missing modules to base `requirements.txt`; doing so would
confuse an optional Windows/provider edge with the active Linux EVENTO
contract. If the user later requests real Instagram acquisition, create a
separate optional dependency slice with its own authority and rollback.

