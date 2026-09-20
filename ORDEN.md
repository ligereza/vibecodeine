# ORDEN
state: DONE
cycle: supervisor-002
objective_met: true

summary: El Hub proyecta el último receipt sanitizado de Azure ML como lineage
read-only, sin llamadas Azure nuevas ni rutas locales en la respuesta.
Productor y consumer comparten `MAK_AZURE_ML_STAGING_ROOT`.
Ausencia, corrupción y selección del receipt quedan cubiertas.

changed:
  - cultura/mak_plataforma/azure_services.py
  - tools/azure_ml_learning_dataset.py
  - tests/test_azure_ml_lineage.py
tests:
  - python -m pytest -q -o addopts='' tests/test_azure_ml_lineage.py: 6 passed
  - python -m pytest -q -o addopts='' tests/test_mak_azure_search.py: 4 passed
  - python -m pytest -q --collect-only: exit 0
  - python -m compileall -q cultura/mak_plataforma tools tests: exit 0
next_blocker: none
