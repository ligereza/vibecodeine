# Informe ejecutivo final — `_archive`

**Corte:** 2026-09-03 · inspección de solo lectura. Se movieron únicamente copias exactas dentro de `_archive/duplicados exactos`; no se alteró ningún archivo fuera del archivo.

`_archive` conserva estados históricos, worktrees, recuperaciones, fuentes creativas, bases y residuos técnicos. Tras apartar 16.675 copias con SHA-256 confirmado, quedan 24.147 archivos (≈2,81 GB) fuera de `duplicados exactos`.

## Qué tiene valor real

El valor no coincide con el peso. Los núcleos prioritarios son:

- **Fuentes gráficas:** la familia de contraportadas SVG es vectorial, 2000×2800, editable en principio y visualmente idéntica entre WIN y active al renderizarla. `FLYERS8.ai` debe tratarse como PDF de 19 páginas, no como AI nativo confirmado.
- **Evidencia de proyecto:** ARICA conserva input, corridas, práctica, plan, proyección y dossier. Sus observaciones principales son idénticas entre corridas y al input; no son tres mediciones independientes.
- **Memoria y procedencia:** `rollback`, `quarantine`, manifiestos, sesiones y grafos documentan decisiones, fallos, recuperaciones y estados no promovidos.
- **Datos estructurados:** `mak_knowledge.db`, `rd.db`, `archivo.json`, `MANIFEST.json` y `grafo_cache.json` conectan archivos y procesos. Son mejores puntos de entrada que revisar miles de archivos manualmente.

## Diferencias relevantes encontradas

`rd.db` de WIN conserva dos venues adicionales (`openklub`, `paralelo_89`), pero ambos están incompletos y no son datos operativos confirmados. El hub WIN es funcionalmente más antiguo: active/runner agrega `/api/project/learning`, `/api/project/probe`, `/api/rd/topics` y `/api/status`.

Los snapshots `archivo.json` son temporales: pasan de 446/479 piezas el 4 de agosto a 1.690 el 12 y 2.034 el 29; el último contiene los IDs del anterior y agrega 344. No son duplicación inútil.

El `MANIFEST.json` de sesiones separa material sanitizado WIN de material preservado active/runner. WIN es portable pero puede cambiar bytes; active conserva mejor la fuente original.

## Qué parece residuo

Los tres `.deb`, el `.exe`, el `.tar.gz`, librerías de entornos, caches y salidas regenerables concentran gran parte del peso y tienen bajo valor documental, salvo necesidad de reproducir una versión exacta. No deben confundirse con respaldos, manifiestos, renders, entregables ni fuentes editables.

## Dictamen

No corresponde tratar `_archive` como basura ni como duplicado masivo. La revisión eficiente es: **manifiestos y bases → evidencia histórica → variantes de `merge` → fuentes visuales → código → dependencias**. El mayor ahorro de trabajo proviene de los índices y bases; el mayor riesgo de pérdida está en las fuentes gráficas, los snapshots de proceso y las variantes preservadas.

El inventario detallado y la priorización analítica están en [candidatos_revision_archive.md](./candidatos_revision_archive.md) y [informe_comparacion_archive.md](./informe_comparacion_archive.md).
