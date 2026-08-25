# C02 — observación nativa real y puente de evidencia

## Propósito

C02 reemplaza la demostración sintética de C01 por dos lecturas acotadas de
archivos reales del archivo artístico ARICA. El experimento no intenta ordenar
todo el archivo ni decidir todavía qué archivo es la obra final. Su pregunta
es más básica y falsable:

> ¿Qué hechos operativos puede observar MAK directamente desde un `.blend` y
> un `.aep`, y qué relaciones siguen siendo desconocidas aunque los archivos
> estén en la misma carpeta?

La autoría no se infiere. `archive-arica-001` es la raíz de procedencia fija
para este experimento: todos los hallazgos pertenecen al mismo archivo de un
artista. Eso no prueba que cada archivo sea una obra, una versión o un
entregable.

## Insumos congelados

| rol | ruta | SHA-256 | alcance |
|---|---|---|---|
| native authoring | `/home/mak/curatoria_inbox/ARICA/RAYU.blend` | `acafc1db0088016139921b1ea2c9d7a5310247658117fa7021662e13e907ce86` | snapshot Blender en background, sin abrir interfaz, guardar ni renderizar |
| native authoring | `/home/mak/curatoria_inbox/ARICA/ARICA.aep` | `99247d6506c6d1d9ce3023f4a1e044da47c806e3cd606d47b61e70fb32f5c460` | lectura lexical acotada de referencias `fullpath`, sin After Effects |

El archivo local contiene otros entregables y proyectos, pero C02 no los
promueve automáticamente a resultados ni los recorre masivamente. El `.aep`
fue elegido porque su lectura real declara `C:\ARICA\tottem_ojo.mp4`; esa
declaración es evidencia de referencia, no evidencia de exportación.

## Ausencia deliberada del endpoint público

No se encontró un export local de Instagram con posts, stories, reels o sus
medios. C02 registra esa ausencia como `public_catalog_status=unavailable`.
No se usan fixtures públicos de C01 para fingir un join real, y no se asigna
un post a ningún entregable por nombre, extensión, carpeta o proximidad.

Cuando exista un export real, se podrá conectarlo al contrato de aristas de
C01 (`mak-cycle-c01-edge-v1`) como una nueva observación; no hace falta
reconstruir este ciclo.

## Reglas de evidencia

- Un snapshot nativo es una observación del documento y de su estado interno.
- Una referencia `fullpath` es `authoring uses source` o una candidata a ese
  hecho, nunca `authoring generated deliverable` por sí sola.
- Una coincidencia técnica o de basename es `candidate`, no `confirmed`.
- Los archivos de entrada no se escriben, mueven, reparan, reempaquetan ni
  renderizan.
- Todo hecho no desconocido debe citar un artefacto de evidencia y la versión
  del extractor.
- La salida del ciclo debe separar `observed`, `candidate` y `unknown`.

## Salida esperada

Cada endpoint produce su propio `REPORT.md`, fixtures mínimos para los casos
que no puedan exponerse sin copiar datos reales, pruebas y JSON de observación
sanitizado. El resultado integrado debe responder:

1. qué se leyó efectivamente;
2. qué referencias o capacidades se observaron;
3. qué caminos locales pudieron resolverse sólo como candidatos;
4. qué vínculo con un producto público no puede comprobarse sin el catálogo;
5. qué datos o extractor deben venir después.

El ciclo no mide aprendizaje estadístico. Produce el sustrato real que permite
medirlo en un ciclo posterior sin confundir una declaración del archivo con
una verdad de portafolio.
