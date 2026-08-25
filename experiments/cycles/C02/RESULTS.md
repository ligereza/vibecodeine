# C02 — resultado con archivos nativos reales

**Estado:** completado como experimento aislado
**Fecha:** 2026-08-25
**Gate:** PASS

## Qué se ejecutó

Dos endpoints independientes observaron archivos reales del mismo archivo
artístico, sin inferir autoría ni modificar producción:

- Blender leyó `/home/mak/curatoria_inbox/ARICA/RAYU.blend` en Blender 4.5.4
  LTS mediante `tools/blender_scene_probe.py`, en background, con factory
  startup y autoexec deshabilitado.
- After Effects se leyó lexicalmente mediante
  `flujo.substrate.aepfile.read_references` desde
  `/home/mak/curatoria_inbox/ARICA/ARICA.aep`; no se abrió After Effects.

## Evidencia reproducible

```text
PYTHONPATH=. .venv/bin/python experiments/cycles/C02/verify_cycle.py
EXIT 0 — hashes de ambas entradas, 18 pruebas, grafo y reportes pasan el gate

PYTHONPATH=/home/mak/flujo/src:/home/mak/flujo/experiments/cycles/C02/aep_endpoint \
  .venv/bin/python experiments/cycles/C02/aep_endpoint/run_observation.py \
  --output experiments/cycles/C02/aep_endpoint/observation.json
EXIT 0 — 5 referencias, 5 candidatos locales, join público unknown

PYTHONPATH=/home/mak/flujo/src .venv/bin/python \
  experiments/cycles/C02/blender_endpoint/run_c02_blender_endpoint.py \
  --snapshot experiments/cycles/C02/blender_endpoint/snapshot.json \
  --report experiments/cycles/C02/blender_endpoint/REPORT.md
EXIT 0 — probe Blender 0, estado observed
```

Los hashes antes y después fueron idénticos:

```text
RAYU.blend  acafc1db0088016139921b1ea2c9d7a5310247658117fa7021662e13e907ce86
ARICA.aep   99247d6506c6d1d9ce3023f4a1e044da47c806e3cd606d47b61e70fb32f5c460
```

Cada endpoint tiene seis pruebas `unittest`; el gate usa la biblioteca estándar
porque `pytest` no está instalado en el entorno del endpoint. Las pruebas
incluyen digest mismatch, dependencias sanitizadas, referencia inexistente,
basename ambiguo, carpeta declarada, output no demostrable y catálogo público
ausente. La integración materializa un grafo de `9` nodos, `7` aristas
`uses`, `1` unknown público y `5` unknowns de rol de output.

## Lo que realmente se observó

El `.blend` contiene una escena, siete objetos, cámara, Cycles, resolución
1920×1080, formato PNG, un filepath de render declarado y dos dependencias de
imagen marcadas como `packed=true` aunque su ruta externa no existe. El
filepath configurado es una capacidad/estado del documento, no prueba de que
se haya renderizado allí un archivo.

El `.aep` contiene cinco declaraciones `fullpath`: tres PNG, `tottem_ojo.mp4`
y la carpeta `C:\ARICA`. Los cinco tienen una comprobación local única por
basename, por eso quedan como `candidate`. Incluso `tottem_ojo.mp4`, que existe
y está declarado por el `.aep`, conserva `output_claim=unknown`: la declaración
prueba que el proyecto lo referencia, no que lo exportó.

## Qué cambia en el modelo

C02 aporta una primera observación real de capacidades y estado de authoring:

```text
documento nativo
  -> referencias declaradas / recursos / settings / destino configurado
  -> candidatos locales
  -> relación con producto público: unknown sin catálogo público
```

Esto confirma que el extremo correcto de entrada no es solamente el producto.
El estado nativo expone precondiciones, recursos, configuración y consumidores
potenciales. Pero tampoco basta para llamar “obra” o “entregable” a un archivo
que coexiste en la carpeta.

La integración en
[`materialize_graph.py`](materialize_graph.py) demuestra el contrato mínimo
entre ambos extractores: un documento nativo puede apuntar a un recurso como
`uses/candidate` o `uses/supported`, mientras que capacidad de render, rol de
output y join público viven separados como capability/unknown. El gate rechaza
si aparece una arista `generated` o `RENDERS_TO`.

## Límite decisivo

No existe un export social real local con posts, stories, reels y medios. Por
lo tanto, C02 no pudo medir el join público ni probar que el grafo completo
reconstruya un portafolio. No se usó C01 sintético para esconder esa ausencia.

El resultado arquitectónico es positivo y acotado: ya podemos extraer hechos
nativos reales y preservar unknowns, pero aún falta el segundo extremo de la
triangulación. Tampoco hay evidencia estadística para embeddings, aprendizaje
de relaciones ni promoción automática.

## Decisión y siguiente ciclo

Se conservan ambos endpoints aislados; no se integran al router ni a una base
de producción. El siguiente experimento útil necesita un catálogo público real
o un fixture ciego que no declare de antemano los enlaces, más un conjunto
pequeño de entregables con hashes, metadata técnica y evidencia de publicación.
La comparación debe medir enlaces correctos, falsos enlaces, abstenciones y
cobertura de caminos. Los embeddings congelados pueden entrar sólo como
recuperación de candidatos después de que hash/metadata/actividad estén
medidos como baselines.
