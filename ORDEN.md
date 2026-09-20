# ORDEN
state: DONE
cycle: supervisor-001
objective_met: true

summary: Se eliminó la dependencia del test hacia la herramienta retirada.
El contrato usa `ACTIVE_SKIP` y conserva los cuatro roots protegidos.
El registry ya no declara la herramienta eliminada.

changed:
  - tests/test_scan_roots_skip_cloud_mounts.py
  - data/tool_registry.json
tests:
  - python -m pytest -q tests/test_scan_roots_skip_cloud_mounts.py: 16 passed
  - python -m pytest -q --collect-only: exit 0
next_blocker: none
