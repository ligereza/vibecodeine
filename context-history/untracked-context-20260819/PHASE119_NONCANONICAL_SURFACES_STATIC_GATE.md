# Phase 119 - noncanonical MAK surfaces static gate

## Scope

This phase checked the remaining visible non-FLUJO surfaces starting at
`/home/mak/*`: `/home/mak/RD` and `/home/mak/src/ml-mobileclip`. XIO was not
included, per the current task boundary.

## Results

### RD creative automation

- Six Python files were found; five parsed with AST.
- `/home/mak/RD/py.py` has an `IndentationError` at line 2 because it is a
  pasted/documentary code block, not a runnable module. It remains evidence;
  it is not deleted or promoted.
- `AUTOMATIZACION/actualizar.py` contains Windows paths (`C:\\rd\\...`),
  Instagram download, copy/removal and Blender subprocess behavior.
- `AUTOMATIZACION/blender_render.py` opens Blender files and mutates a scene;
  `bridge/request.py` mutates Blender nodes. These are writers and external
  creative-tool consumers, not safe read-only migration candidates.
- Imports include `instaloader`, `bpy`, `google`, `matplotlib` and related
  optional dependencies. No import or execution was attempted.

Decision: `DEFERRED_MUTATING_EXTERNAL`. Preserve the source and outputs. The
existing FLUJO RD automation crosswalk remains the owner until a foreground
consumer, Linux path contract and rollback plan are explicitly selected.

### MobileCLIP source

- `/home/mak/src/ml-mobileclip` contains 26 Python files; all 26 pass AST
  parsing without execution.
- Its own `README.md`, `setup.py` and `requirements.txt` define an external
  research/library project with OpenCLIP, Torch, datasets and model downloads.
- No mutating calls were found by the bounded AST scan. Static references from
  MAK are model metadata/tests, not a confirmed active runtime consumer.

Decision: `OPTIONAL_EXTERNAL_SOURCE`. Keep isolated with its own dependency
boundary; do not copy it into FLUJO or install its requirements.

## Foreground command and result

The read-only AST scan used the canonical venv Python over both roots and
exited 0. It reported `RD: 5/6 AST_OK` and `ml-mobileclip: 26/26 AST_OK`.
No file, database, output, provider, Blender, network or persistent process
was touched.

## Next action

Continue with the remaining consumer-backed duplicate and folder-ownership
review. Do not classify these two surfaces as junk: RD is a protected external
writer, and MobileCLIP is an isolated optional library.
