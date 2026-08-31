# Phase 62 — RD asset and dependency crosswalk

## Scope and method

The physical search started at `/home/mak/*`, then narrowed to `/home/mak/RD`
and the active FLUJO consumers. `/home/mak/WIN` remains historical evidence;
no tree was copied and no asset was deleted. Search covered Spanish and
English function names, file extensions, route names and consumer modules.

## Physical classification

| Surface | Observed size | Function | Consumer | Status | Decision |
|---|---:|---|---|---|---|
| `/home/mak/RD/AUTOMATIZACION` | 614 files | event flyer workflow, templates, renders, deliveries, bridge files | `src/flujo/eventos/flyer_auto.py`; optional Blender/Photoshop handoff | mixed Windows-origin operational and evidence surface | retain; resolve canonical path before consolidation |
| `/home/mak/RD/suplementos` | 470 files | product/label/commercial creative material | RD human production; route map; no single hub loader proven | asset/evidence surface | retain and classify by deliverable, source and output |
| `/home/mak/RD/flyernuevo` | 87 files | event flyer/reel history and variants | route map only; no direct active loader proven | historical creative surface | retain; no automatic promotion |
| `/home/mak/RD/assets` | 82 files | reusable images/materials | route map and human creative workflows | library candidate | retain; deduplicate only after consumer/format review |
| `/home/mak/RD/recursos` | 65 files | branding, textures and shared resources | route map; `src/flujo` uses selected project assets | shared library/evidence | retain; establish ownership before merge |
| `/home/mak/RD/CREAMFIELDS` | 62 files | event-specific source/output material | route map | historical event surface | retain as event archive |
| `/home/mak/RD/New Folder` | 59 files | unnamed working material | no proven consumer | unresolved working surface | classify contents before any cleanup |
| `/home/mak/RD/FEBRERO` | 48 files | event-specific material | route map | historical event surface | retain as event archive |
| `/home/mak/RD/FLYER` | 34 files | flyer variants | route map | historical creative surface | retain; compare exact/near duplicates |
| `/home/mak/RD/Almacenamiento automático de Adobe After Effects` | 27 files | Adobe autosave/recovery files | external Adobe workflow | generated/recovery evidence | quarantine classification; deletion requires exact confirmation |
| `/home/mak/RD/gotario` | 23 files | product/reactive material | route map | product asset surface | retain; map to RD deliverable owner |
| `/home/mak/RD/prep` | 20 files | preparation material | route map | preparation surface | retain; classify inputs versus outputs |
| `/home/mak/RD/desde_issues` | 6 files | issue-derived inputs/outputs | FLUJO issue automation evidence | provenance surface | retain; link to issue/job IDs |
| `/home/mak/RD/RESULTADOS_MANUAL` | 3 files | manually produced outcomes | human workflow | output evidence | retain; no automatic merge |

The complete `/home/mak/RD` bounded inventory contains approximately 1,743
files and 192 directories. Extension counts include 1,043 PNG, 138 JPG, 103
BLEND, 82 PDF, 53 AEP, 50 TIF, 40 PSD, 39 AI, 35 MP4, 30 SVG, 14 JPEG, 12
MOV, 8 PYC, 6 PY and 6 JSON files. Extensions such as BLEND, AEP, PSD and AI
are editable-tool artifacts, not Python runtime dependencies.

## Consumer and dependency findings

1. `src/flujo/eventos/flyer_auto.py` is the active Python consumer for the
   event automation slice. Its path contract is:
   `FLUJO_EVENTOS_AUTOMATIZACION_DIR`, then
   `FLUJO_RD_ROOT/AUTOMATIZACION`, then a platform default.
2. With both variables unset on Linux, `default_base_dir()` resolves to
   `/home/mak/flujo/eventos_automatizacion`; this directory was not created.
   With `FLUJO_RD_ROOT=/home/mak/RD`, it resolves to the existing
   `/home/mak/RD/AUTOMATIZACION`. An explicit directory override also passed.
3. The CLI help for `python3 -m flujo eventos flyer-auto --help` exited 0.
   No network download, Photoshop, Blender, render or external provider was
   invoked.
4. `src/flujo/eventos/blender_render.py` and
   `/home/mak/RD/AUTOMATIZACION/blender_render.py` parse successfully. Blender
   (`bpy`) and GPU support are external runtime dependencies; they are not
   installable Python dependencies inferred from the Windows environment.
5. `/home/mak/RD/AUTOMATIZACION` contains Windows executables, BAT installers,
   a Python GUI, a bridge and many generated outputs. These are not one
   mergeable tool. The Python bridge and the FLUJO consumer require separate
   contract tests; `.exe` and `.bat` remain Windows evidence until a Linux
   equivalent has a real consumer.
6. `src/flujo/route/rutas_rd.json` still describes `C:\rd` paths and marks
   itself `no_mover`. It is a provenance/route map, not a Linux path resolver.
   It must not be treated as proof that every listed asset is active.
7. `src/flujo/plano/packs.py` has a declared Python consumer and reads the
   canonical editable tariff at `data/rd_packs.json`; this is separate from
   the creative asset tree. Its dual web/Python source relationship remains a
   later tool-consolidation item, not an asset-copy operation.

## Safe verification evidence

Commands run in the foreground:

```text
AST parse: flyer_auto.py, flujo/eventos/blender_render.py, flujo/plano/packs.py,
           RD/AUTOMATIZACION/actualizar.py, blender_render.py, bridge/request.py
Result: all AST_OK; exit 0

default_base_dir() with variables unset
Result: /home/mak/flujo/eventos_automatizacion; no directory created

default_base_dir() with FLUJO_RD_ROOT=/home/mak/RD
Result: /home/mak/RD/AUTOMATIZACION

python3 -m flujo eventos flyer-auto --help
Result: exit 0; help rendered; no external action
```

## Migration decision

The smallest next vertical slice is the automation path contract, not a bulk
asset move: prove that a temporary `FLUJO_RD_ROOT` or explicit base directory
can execute only local, non-network preparation against a fixture. After that,
build a manifest separating source templates, generated outputs, deliveries,
recovery files and evidence. Only then can exact duplicates or equivalent
tools be merged safely.

No cleanup is authorized by this report. `WIN` remains the historical archive,
and `/home/mak/RD` remains preserved until each item has a consumer, owner,
replacement or explicit evidence disposition.
