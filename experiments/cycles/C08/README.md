# C08 — evaluador relacional mínimo

Experimento aislado, stdlib-only, para comparar un baseline que deja toda
relación, fase y serie en `unknown/no relation` contra una lista de
predicciones candidatas ordenadas por `rank`.

Incluye siete fixtures adversariales: 2.048 frames de una obra, export sin
proyecto, proyecto sin export, post sin proyecto, una obra en cuatro formatos
y proporciones, asset de tercero parecido y nombres parecidos. La fixture
también contiene gold relations, memberships de fase y serie, y una intención
de portafolio.

Métricas:

- `precision_at_k`: hits entre `k * casos`; los falsos positivos penalizan.
- `recall`: recall al último k (5); `coverage`: proporción de casos con gold
  que obtienen al menos un hit al último k.
- Portafolio: cobertura de fases requeridas, diversidad de formatos/proporciones,
  cobertura cronológica y redundancia por `work_id`.

Ejecución desde `/home/mak/flujo`:

```text
python3 -m unittest discover -s experiments/cycles/C08/tests -p 'test_*.py'
python3 -m py_compile experiments/cycles/C08/evaluator.py experiments/cycles/C08/fixtures.py experiments/cycles/C08/runner.py experiments/cycles/C08/tests/test_evaluator.py
python3 experiments/cycles/C08/runner.py
python3 experiments/cycles/C08/integration_runner.py
```

`runner.py` escribe únicamente `experiments/cycles/C08/report.json` y emite
un resumen por sección. `candidate` no es verdad: las relaciones son una
recuperación para medirla contra el gold explícito. La selección de portafolio
se deriva mediante un planificador greedy mínimo (`greedy_phase_coverage`) que
prioriza fases requeridas y luego añade formatos, proporciones y cortes
cronológicos nuevos, penalizando repetir el mismo `work_id`.

`integration_runner.py` ejecuta C07 y evalúa su `graph.json` en los mismos cinco
casos contra el baseline vacío. La fixture obtuvo recall 1.000 al top-5, pero
precision 0.400 al top-1 y 0.240 al top-5; por eso los candidatos siguen siendo
propuestas revisables, no edges confirmados.

La hipótesis relacional quedaría falsada en este benchmark si, al sustituir
los candidatos por observaciones reales ciegas, no supera de forma consistente
al baseline en precisión/recall/cobertura, o si la mejora de cobertura solo
proviene de repetir miles de frames de una misma obra: en ese caso el
portafolio mostraría redundancia alta sin diversidad ni cobertura real.
