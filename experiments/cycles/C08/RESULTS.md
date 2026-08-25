# C08 — resultados

Resultado reproducible generado con stdlib, sin dependencias nuevas. El
runner produce además `report.json` con el reporte completo por caso.

Comandos y códigos de salida:

```text
python3 -m unittest discover -s experiments/cycles/C08/tests -p 'test_*.py'
EXIT 0

python3 -m py_compile experiments/cycles/C08/evaluator.py experiments/cycles/C08/fixtures.py experiments/cycles/C08/runner.py experiments/cycles/C08/tests/test_evaluator.py
EXIT 0

python3 experiments/cycles/C08/runner.py
EXIT 0
```

Lectura: el baseline tiene recall y cobertura cero por construcción. Las
predicciones candidatas son medibles en relaciones, fases y series. El
planificador mínimo deriva una selección que cubre las cuatro fases y los tres
cortes cronológicos sin repetir los 2.048 frames de `work-lumen`.
Los casos sin proyecto/export y los nombres/asset parecidos contienen falsos
positivos para impedir que similitud o nomenclatura se conviertan en relación.

Salida observada del runner:

```text
relations: p@1=0.286 recall=0.004 coverage=1.000
phases: p@1=0.714 recall=0.005 coverage=0.714
series: p@1=0.143 recall=0.750 coverage=1.000
portfolio: baseline_score=0.000 candidate_score=1.000 redundancy=0.000
```

El reporte por caso queda en `experiments/cycles/C08/report.json`.

Integración con C07 sobre los mismos cinco casos:

```text
python3 experiments/cycles/C08/integration_runner.py  # EXIT 0
candidate_count=13
gold_count=6
baseline_recall=0.000
candidate_recall=1.000
candidate_precision_at_1=0.400
candidate_precision_at_5=0.240
candidate_coverage=1.000
supported=0, pending_relation=6, unresolved_candidate=11
```

Lectura: el candidato recupera todas las relaciones de la fixture al top-5,
pero solo 40% de sus primeras sugerencias son correctas y 24% del top-5 es
correcto en promedio. Por eso el resultado justifica un ranking y revisión
curatorial, no auto-confirmación.
