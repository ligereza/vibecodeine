# Phase 107 — curatoria percepcion ownership merge

## Scope and evidence

The active MAK root and canonical `percepcion.py` were byte-identical. WIN was
a historical variant differing only in fallback comments and one user-facing
fallback message; the MAK version contains the newer local `research_lib`
resolution behavior. Real consumers include `ingesta_archivo.py`, the hub,
conductor handlers and the producer catalog.

## Action

Replaced only `/home/mak/curatoria/percepcion.py` with a compatibility
projection to the canonical MAK implementation. WIN was preserved untouched.
No OCR, vision provider, Ollama, Tesseract, ffprobe, fiche write or watchdog
ran.

## Foreground validation

- Root import and corrected pure contracts (`estado_medicion(False, "")`
  returns `no_intentado`, `estado_medicion(True, "")` returns `vacio`, and
  `id_ficha` returns a stable id): exit 0.
- `percepcion.py --help` follows the custom `correr|estado` usage contract and
  exits 2; this is expected because it does not use argparse help. No output
  directory or fiche was created.
- Root bridge and canonical source compile: exit 0.
- No perception, OCR, vision, worker, hub, Blender or Ollama process remained.

The initial fixture assertion expected `no_aplica`, a 16-character id and a
retained normalized technique; the actual contract is `no_intentado`, a
12-character id and empty input is filtered. The code was not changed in
response; the corrected fixture passed.

## Rollback and risk

Rollback is local from the pre-edit root file or WIN historical copy. External
vision and file-producing paths remain gated; only deterministic fixtures and
help were executed.

## Result

Curatoria perception now has one active MAK owner with its local fallback
resolution preserved; WIN remains historical evidence.
