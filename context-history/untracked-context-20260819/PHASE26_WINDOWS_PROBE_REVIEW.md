Identity: LUNA principal

# Phase 26 — revisión de evidencia del probe Windows

## Veredicto

Los cuatro archivos recibidos son utilizables y contienen el resultado
principal del diagnóstico. El escaneo estático terminó correctamente aunque
faltan `command-results.json` y `README.txt`, por lo que no se dispone del
texto exacto del error final ni de cada salida individual.

Evidence received from `/home/mak/curatoria_inbox/flujo_windows_probe/`:

- `environment.json`: Windows 11 Home, host `ISKVW`, Python 3.11.8, root
  `C:\IA\flujo`, `python -m flujo --help` exit 0, `--version` exit 2.
- `imports.json`: 262 Python files scanned, 60 standard-library import names,
  7 local names, 21 mapped external distributions, 59 unresolved names, 16
  dynamic-import sites and 0 syntax/read errors.
- `requirements-candidates.txt`: 21 installed distributions mapped to
  explicit imports; this is evidence, not a final requirements file.
- `pip-freeze.txt`: complete environment snapshot; it contains considerably
  more packages than FLUJO needs and must not be copied wholesale.
- `pip check`: the Windows environment has conflicts spanning semgrep,
  Google AI, LangGraph/NiceGUI, MoviePy, OpenCV, OpenTelemetry,
  open-interpreter, open-webui and SceneDetect. This confirms that the global
  environment is not a clean requirements source.
- `py -3 -X importtime -c "import flujo.web.hub"`: completed successfully;
  the full hub import reached about 224 ms cumulative and loaded
  `flujo.serve.server`, RD database/report modules and export modules without
  a visible import failure.

## Correct interpretation

The probe scanned the migration surface broadly: `src/flujo`, `cultura`,
`iskvw`, `projects/cultura`, `tools/mak` and `tools/mak_ops`. Therefore the
21 distributions mix the full FLUJO core, optional visual/research features,
MAK departments and operational tools. The unresolved names are not proof of
missing PyPI packages: many are local flat-layout modules, optional Blender
names or dynamic/internal imports.

The Windows evidence is strong enough to begin dependency narrowing. It is not
strong enough to produce a final `requirements.txt` without route/consumer
classification.

## Execution plan

1. Filter `imports.json` to the real FLUJO APP path: CLI, full `web/hub.py`,
   hub HTML consumers and the RD/ISKVW/CULTURA route owners. Exclude unrelated
   MAK-only and artwork/Blender paths from the core list.
2. Classify every candidate as core, route-optional, local, dynamic or
   unresolved. Preserve the Spanish/English names and the file that consumes
   each import.
3. Compare the narrowed Windows set with the existing MAK venv and current
   project metadata. Do not install anything yet.
4. Produce separate provisional artifacts: a core dependency file and an
   optional route dependency file, each with evidence and versions.
5. Run bounded import/help smoke checks in MAK. Only after those pass decide
   whether a real requirements file or adapter change is authorized.

## Risks and next action

- `--version` exit 2 is recorded but cannot be interpreted exactly without the
  missing command-results file; `--help` and the AST scan are successful.
- `pip-freeze.txt` includes environment noise and possible dependencies for
  unrelated projects.
- Dynamic imports require targeted route checks; static imports alone cannot
  prove optional dependency use.
- The new `tools/probe_flujo_windows_metadata.ps1` adds bounded NTFS
  creation/modified timestamps, direct child counts and SHA-256 values for the
  anchors and key department directories. It is triangulation evidence, not a
  replacement for runtime checks.

Next concrete action: run the bounded metadata probe, then build the
route-scoped dependency matrix from all received reports and the Phase 25 hub
crosswalk. No package installation, hub startup or source edit is needed.
