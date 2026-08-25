# C01 — Resultado del ciclo

**Estado:** completado como experimento aislado
**Fecha:** 2026-08-24
**Conclusión:** evidencia arquitectónica positiva, no evidencia estadística de aprendizaje

## Qué se implementó

Se construyeron dos endpoints independientes sobre fixtures sintéticos de un
solo artista:

- `public_endpoint/`: publicación, media exportado, entregable local,
  coincidencia exacta/técnica, carrusel y estados sin pareja.
- `native_endpoint/`: documentos nativos, componentes, fuentes, actividades
  de edición/render/export, múltiples versiones, fuente compartida y export
  fallido.

El contrato común es `mak-cycle-c01-edge-v1`. Las dos superficies son
read-only respecto del archivo conceptual: no abren ni modifican archivos
artísticos, no usan la base real, no cambian producción y no descargan modelos.

## Evidencia reproducible

```text
PYTHONPATH=. .venv/bin/python experiments/cycles/C01/verify_cycle.py
EXIT 0 — endpoint público y endpoint nativo pasan el gate

.venv/bin/python experiments/cycles/C01/native_endpoint/run_experiment.py
EXIT 0 — JSON de los casos 6, 7 y 8

.venv/bin/python -m py_compile \
  experiments/cycles/C01/verify_cycle.py \
  experiments/cycles/C01/public_endpoint/public_endpoint.py \
  experiments/cycles/C01/native_endpoint/native_endpoint.py
EXIT 0

git diff --check
EXIT 0
```

El gate ejecutó `9` tests del extremo público y `6` del extremo nativo con
`pytest`; todos pasaron.

## Resultado observado

### Extremo público

- Un match SHA-256 único puede elevar una coincidencia a `confirmed`.
- Un re-encode con compatibilidad técnica permanece `candidate`.
- Una publicación sin entregable local queda como `unmatched`, no crea un
  proyecto ficticio.
- Un entregable local sin publicación queda visible como `unmatched`.
- Un carrusel conserva cardinalidad y orden de sus medios.
- Un vector precomputado solo recupera candidatos; nunca confirma procedencia.

### Extremo nativo

- Un documento puede generar varias versiones de entregable.
- Una fuente compartida puede aparecer en dos caminos de producción sin
  duplicarse.
- Una cadena puede conservar `uses`, `generated`, `derived_from` y
  `specializes`.
- Un export fallido conserva el evento y la imposibilidad, pero no inventa un
  output identificable.

## Comparación arquitectónica

El join directo puede expresar una pareja simple:

```text
authoring -> deliverable
publication -> deliverable
```

El modelo mediado puede expresar además:

```text
input -> edit -> render -> export -> deliverable version
source -> activity A -> output A
source -> activity B -> output B
version 2 -> specializes -> version 1
failed export -> no identifiable output
```

Por lo tanto, el modelo mediado tiene mayor expresividad para los casos
compuestos, las versiones, los recursos compartidos y las imposibilidades.

## Límite crítico de la evidencia

Los fixtures son contratos de benchmark. En particular, las actividades y
algunas relaciones declaradas sirven como oráculo para probar si el modelo
puede representarlas. El ciclo **no demuestra que un extractor real pueda
descubrirlas** desde un `.blend`, `.aep`, `.psd`, DaVinci o un export social.

El resultado correcto es, por tanto:

> el modelo de actividades justifica una próxima prueba de extracción y
> triangulación; todavía no justifica entrenamiento, promoción de políticas ni
> afirmaciones de linaje sobre archivos reales.

## Decisión del director

Se conserva el prototipo aislado como evidencia arquitectónica. No se integra
en producción ni se crea `active_policy`.

El siguiente ciclo debe eliminar el oráculo de las rutas de recuperación y
probar, sobre observaciones reales read-only o fixtures ciegos:

1. extracción de una actividad nativa real y sus outputs declarados;
2. unión con el catálogo público por el entregable, no por autoría;
3. casos negativos donde el nombre o la similitud contradicen la relación;
4. medición de falsos enlaces, abstenciones y cobertura de caminos;
5. embeddings congelados únicamente como recuperación de candidatos frente a
   hash/metadata/consumer graph.
