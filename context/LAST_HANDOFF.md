Date: 2026-07-01
Version: 0.48.5 (pyproject.toml / src/flujo/version.py, matching)

Done:
- Resolume/Chataigne automator (src/flujo/resolume/automator.py) generates XML pre-flight, CSV OSC, README, and an experimental .noisette (v0.48.2 to v0.48.5, 4 rewrites, still unverified against a real file).
- SVG Studio, Plano/Rider, Cotizacion, Jobs, Intake, Commands stable in web/ (React/Vite single-file build into context/*.html).
- Web hub tools list is defined in web/src/components/AppShell.tsx (RD_NAV / STUDIO_NAV) plus a view case in web/src/App.tsx.

Doing (uncommitted local changes, not pushed):
- Added a new Studio tool "Mapping LED" (Event Rigging Master Console) wired via iframe: web/src/components/MappingTool.tsx, web/public/mapping.html, web/scripts/copy-context.mjs extended, AppShell.tsx / App.tsx updated.
- INDEX_FORMATOS.json cleanup: reconciled tools/piezas_vectoriales/plantillas/INDEX_FORMATOS.json with formats actually used in code (carrusel, etiqueta horizontal generica) and removed an unused duplicate at repo root.

Next:
- Get a real .noisette file exported from the user's Chataigne 1.10.3 and save it as a fixture under tests/ before touching build_chataigne_noisette_experimental again.
- Decide if/when to commit and push the Mapping LED tool changes above.
- Bring context/SESSION_STATE.json and context/AVANCES_BLOCK.txt current every session end (see AGENTS.md rule); they had drifted 6 versions behind real state before this handoff.

Blockers:
- build_chataigne_noisette_experimental has no real .noisette to validate against; do not guess the schema again, ask the user for the exported file.
