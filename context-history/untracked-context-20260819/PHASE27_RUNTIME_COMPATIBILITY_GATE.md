Identity: LUNA-30

# Phase 27 runtime/dependency compatibility gate

## Scope and conclusion

This is a read-only gate for the Windows FLUJO APP migration into MAK. Sources
were `/home/mak/curatoria_inbox/flujo_windows_probe/` (`environment.json`,
`imports.json`, `requirements-candidates.txt`, `pip-freeze.txt`,
`anchors-metadata.json`), the declared manifests in `/home/mak/flujo`, and the
active `/home/mak/venvs/flujo` environment. Git, installation, uninstallation,
services, HTTP/API calls, workers, SSH and source/runtime/data/artwork changes
were not used.

The Windows probe reports Python 3.11.8 / pip 26.1.2, 262 scanned files, 21
external distributions, 59 unresolved external import names, 16 dynamic import
sites and zero syntax/read errors. MAK uses Python 3.11.2 / pip 23.0.1. The
actual MAK venv has 9 of the 21 probe distributions installed and imports
successfully (boto3, jsonschema, numpy, Pillow, pydantic, PyYAML, requests,
rich, and typer). The other 12 are absent from MAK; version drift is counted
below.
The package-level table and CSV contain the exact 21 records plus explicit
classification rows for MAK-local unresolved names, Windows-only Blender
names, globally-conflicted freeze-only packages, and unresolved/dynamic sites.

Gate decision: the core CLI and hub import surface is compatible for a bounded
MAK vertical slice. The full desktop branch and several optional route/tool
branches are not compatible until their declared or consumer-linked packages
are deliberately provisioned. The Windows candidate list must not replace the
current manifests.

## Classification rules

- `core`: imported by the CLI/hub or by the selected RD vertical slice and
  currently declared as a base dependency.
- `route-optional`: linked to desktop, rendering, intake/download, packaging,
  or another explicit optional branch; absent from MAK is not a core hub fail.
- `MAK-local`: local modules or distributions consumed by the later MAK
  genealogy under `cultura/` or `tools/`, not proven requirements of the WIN
  hub route.
- `Windows-only`: Blender/Windows adapter names or packaging/platform paths;
  not a Linux runtime requirement for the selected slice.
- `globally-conflicted`: present only in the broad Windows freeze or with a
  version/platform conflict and no direct hub/RD/ISKVW/CULTURA consumer link.
- `unresolved/dynamic`: the probe found a local/dynamic import name without a
  distribution mapping. It requires consumer-level review, not a guessed pip
  dependency.

`pip-freeze.txt` is evidence of the Windows environment, not a requirement
manifest. In particular, packages such as the large AI/web/toolchain set,
`torch`, `psycopg`, and unrelated providers are not promoted from freeze-only
presence without a consumer link.

## Compatibility matrix

The complete row-level gate is in
[`PHASE27_RUNTIME_COMPATIBILITY_GATE.csv`](/home/mak/flujo/context/PHASE27_RUNTIME_COMPATIBILITY_GATE.csv).
The following summarizes the decisions; Windows versions come from
`imports.json`, MAK versions from `importlib.metadata` in the active venv.

| Class | Package/import evidence | MAK result | Gate decision |
|---|---|---|---|
| core | boto3 1.42.62, jsonschema 4.26.0, pydantic 2.13.4, PyYAML 6.0.3, requests 2.34.2, rich 15.0.0, typer 0.27.0 | Installed; boto3 1.43.66 and typer 0.27.1 differ but satisfy current lower bounds; others match | PASS for hub/RD slice; boto3 is MAK-local provider support, not needed by hub slice |
| core/consumer-linked | Pillow 12.3.0, numpy 1.26.4 | Pillow 12.3.0; numpy 2.4.6 | Pillow PASS; numpy version drift is a risk for MAK-local visual_index/memory, not a hub blocker |
| route-optional | CairoSVG, Flask, PyInstaller, PyMuPDF, pypdf, pystray, pywebview, vtracer, curl_cffi, parth-dl, psycopg | Not installed | Keep optional or MAK-local; no promotion into base requirements |
| MAK-local | boto3/providers, psycopg migration tool, torch/visual_index, pypdf/source_pipeline, Flask staged XIO, numpy visual/project code | Mixed or absent | Review only with named MAK consumer; no claim for WIN hub |
| Windows-only | bpy, mathutils, blender_gpu, blender_nodes, blender_nodes_video* | Unresolved/not installed on Linux | Isolate Blender adapter; do not gate RD/ISKVW/CULTURA hub slice |
| globally-conflicted | freeze-only packages and unrelated transitive/toolchain packages | Broad freeze is not a FLUJO declaration | No requirement decision without consumer link |
| unresolved/dynamic | 59 unresolved names; 16 `__import__`/`find_spec` sites | Not mapped to distributions | Consumer review required; do not guess packages |

## Minimal complete vertical slice

The smallest evidenced slice is the RD hub navigation/read/render contract:

`flujo --help` -> `flujo app`/`flujo serve` dispatch -> `flujo.web.hub` ->
`context/flujo_hub.html` RD mode -> `/api/rd-packs` and `/api/rd-db` reads ->
`/api/plano/render` / cotización backend contract.

For this slice, the minimal runtime set is:

`typer`, `rich`, `Pillow`, `pydantic`, `PyYAML`, `jsonschema`, and `requests`,
with the project package itself. All seven are installed/importable in the
MAK venv. Six are declared in the base `pyproject.toml`/`requirements.txt`;
Pillow is already a direct import of the full hub but is currently declared
only in `render` and `desktop-extras`, which is the main gate finding.
`boto3` is not included because its evidenced consumer is
`cultura/mak_plataforma/providers.py`, not the selected hub route. `pystray`
and `pywebview` are excluded because they belong to the optional desktop branch.

This slice is a dependency/import contract, not a live server test: route calls
were prohibited. The bounded evidence is anchor compilation/import, CLI help,
and static route/consumer extraction.

## Verification record

All commands were foreground and read-only:

| Command | Exit | Result |
|---|---:|---|
| `sed` of `agents.md` and `LAST_HANDOFF.md` | 0 | Scope and write boundary read |
| `python3` JSON summary of five Windows evidence files | 0 | Evidence structure and counts read |
| `/home/mak/venvs/flujo/bin/python --version` and `-m pip --version` | 0 | Python 3.11.2, pip 23.0.1 |
| venv `importlib.metadata` plus import probe for 21 Windows distributions | 0 | 9 installed; 12 missing optional/local branches reported without mutation |
| AST import extraction for `cli.py`, `web/hub.py`, `serve/server.py` | 0 | Hub and CLI consumer imports recorded |
| `PYTHONPATH=/home/mak/flujo/src ... python -c 'from flujo.web.hub ...'` | 0 | Hub handler and launcher imports pass |
| `... python -c 'import flujo.cli'` and server import probe | 0 | CLI/server imports pass |
| `PYTHONPATH=/home/mak/flujo/src ... python -m flujo --help` | 0 | Full command surface displayed |
| `... python -m py_compile` on the three anchors | 0 | No syntax failure |
| stdlib CSV validation below | 0 | 25 rows, 12 columns, required fields non-empty |
| stdlib Markdown/CSV identity and count validation below | 0 | Both files begin exactly with `Identity: LUNA-30` |

Validation commands for the created artifacts:

```text
python3 -c "import csv; p='/home/mak/flujo/context/PHASE27_RUNTIME_COMPATIBILITY_GATE.csv'; f=open(p, newline=''); assert f.readline().rstrip()=='Identity: LUNA-30'; r=list(csv.DictReader(f)); assert len(r)==25 and len(r[0])==8 and all(x['package'] and x['import_name'] and x['decision'] for x in r); print(len(r), len(r[0]))"
python3 -c "from pathlib import Path; a=Path('/home/mak/flujo/context/PHASE27_RUNTIME_COMPATIBILITY_GATE.md').read_text(); b=Path('/home/mak/flujo/context/PHASE27_RUNTIME_COMPATIBILITY_GATE.csv').read_text(); assert a.startswith('Identity: LUNA-30\n') and b.startswith('Identity: LUNA-30\n'); print('identity-ok')"
```

Expected observed results: `25 8` and `identity-ok`, both exit 0.

## Risks and next action

- The base declaration omits Pillow even though `web/hub.py` imports it
  directly. This is a real declaration gap; route behavior was not executed.
- `numpy` is installed at 2.4.6 while Windows evidence is 1.26.4. It is linked
  mainly to MAK-local visual/index/project code; test that consumer before any
  pin or downgrade.
- `pystray` and `webview` are absent but used by the hub desktop branch. Treat
  desktop launch as blocked/optional until explicitly provisioned and tested.
- Nine other Windows candidates are absent. Their consumers are optional,
  MAK-local, packaging, download, staged XIO, or migration tooling; none is a
  justified base dependency from this gate.
- The 59 unresolved names and 16 dynamic sites include local genealogy and
  Blender names. Static evidence cannot prove all runtime branches; consumer
  review remains open.
- `pip-freeze.txt` contains many unrelated packages and does not establish
  provenance or necessity.

Next action: review and, if authorized in the next phase, close the Pillow
declaration gap for the selected RD slice, then run the same bounded import/
compile gate. Separately test desktop and MAK-local branches only when each has
a named consumer and an allowed foreground verification.
