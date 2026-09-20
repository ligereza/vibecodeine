# ORDEN
state: DONE
cycle: supervisor-003
objective_met: true

summary: El lineage local de Azure ML ahora atraviesa MAK, FLUJO y MakPanel.
La consulta es read-only, no llama Azure durante el polling y filtra la
allowlist de metadata. La ausencia o caída del sub-endpoint no oculta la salud
general del box.

changed:
  - cultura/mak_plataforma/hub.py
  - src/flujo/web/hub.py
  - web/src/components/MakPanel.tsx
  - tests/test_azure_lineage_surface.py
tests:
  - python -m pytest -q -o addopts='' tests/test_azure_lineage_surface.py: 6 passed
  - python -m pytest -q -o addopts='' tests/test_web_hub_endpoints.py: 59 passed, 1 external failure
  - python -m pytest -q --collect-only: exit 0
  - python -m compileall -q cultura/mak_plataforma src/flujo tests: exit 0
  - npm run typecheck: external, js_dependencies_unavailable
failure_groups:
  - signature: test fixture research sin tabla job_sources
    count: 1
    relation: external
    example: tests/test_web_hub_endpoints.py::test_get_research_job_returns_the_full_record
  - signature: dependencias JavaScript no instaladas
    count: 1
    relation: external
    example: web/node_modules no existe; no se instalaron dependencias
next_blocker: none
