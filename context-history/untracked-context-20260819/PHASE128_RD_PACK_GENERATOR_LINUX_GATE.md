# Phase 128 - RD pack generator Linux gate

## Problem found

`jobs/2026-07-04_eventos-brief/flows/gen_packs.py` was not a safe MAK
entrypoint: it wrote files during import, depended on the current working
directory and hard-coded a Windows Claude scratch path. Its actual consumer is
the delivered RD job and the web SVG visualizer.

## Change

Edited only:

`/home/mak/flujo/jobs/2026-07-04_eventos-brief/flows/gen_packs.py`

The generator now derives the repository root from `__file__`, resolves logos
and the plano input from that root, exposes `main()`, writes only when invoked
as a command, and accepts `--out-job`, `--out-svg` and `--scratch` for bounded
foreground runs. The default scratch path is local to MAK under
`flujo/tmp/rd_packs_2026-07-04_eventos-brief`.

## Foreground validation

Command used a fresh temporary directory under `/tmp`:

```text
/home/mak/venvs/flujo/bin/python -m py_compile gen_packs.py
/home/mak/venvs/flujo/bin/python gen_packs.py \
  --out-job /tmp/phase128-rd-*/job \
  --out-svg /tmp/phase128-rd-*/svg \
  --scratch /tmp/phase128-rd-*/scratch
```

Results: compile exit 0, generator exit 0, fixture exit 0; 3 job files, 2
editable SVG files and 4 HTML scratch files were generated; JSON total was
`500000`; all SVGs contained an SVG root; no generated scratch file contained
the old `C:/Users` path. The live job and live SVG output were not modified.

## Dependency and consumer impact

The canonical venv's Pillow import was sufficient for this generator. The
generator remains a local RD writer and does not invoke providers, network,
Blender or PDF conversion in this gate. The existing PDF files remain outputs,
not regenerated products.

## Next action

Register the job source/output ownership in the RD asset matrix and run the
remaining read-only asset index checks. Do not regenerate live deliverables or
delete related RD copies without a human delivery decision.
