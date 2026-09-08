# Candidatos de revisión prioritaria de `_archive`

Este documento aplica el criterio **conectividad + irreemplazabilidad + costo**. Los candidatos no se consideran valiosos por el nombre: deben verificarse contra la evidencia externa y el contexto de su campaña.

## Prioridad 1 — alto rendimiento, revisión corta

| Candidato | Qué puede resolver | Señal observada |
|---|---|---|
| `_archive/merge-20260831/fused/projection3/MANIFEST.json` | Qué rutas fueron iguales, divergentes o variantes entre tres orígenes | 5.426 rutas; 813 divergentes; 2.366 variantes |
| `_archive/merge-20260831/fused/root-materialization.json` | Qué se materializó en `/home/mak` y qué conflictos se preservaron | 6.214 archivos enlazados; 22 symlinks; 3 conflictos especiales |
| `_archive/orden-limpieza-20260828/por-razon/mapa-inventario-superado/indexes/mak-consolidation-20260829/exact-duplicate-candidates.csv` | Qué archivos ya tenían decisión y cuáles quedaron en revisión | 2.167 grupos; 683 `review_live_alias`; 43 `review_evidence` |
| `_archive/rollback-20260811-20260814/faro-live-before-recovered-20260812/research/memoria/grafo_cache.json` | Qué archivos están relacionados por el sistema de memoria | 1.830 nodos y 5.856 relaciones |

## Prioridad 2 — alto valor documental

| Grupo | Por qué importa |
|---|---|
| `quarantine-20260806-20260809/.../turnos_flujo.jsonl` | Reconstruye actividad, sesiones, roles, fechas y archivos asociados; puede explicar por qué algo fue puesto en cuarentena |
| `rollback-20260811-20260814/.../eventos.jsonl` y `grafo_cache.json` | Permite reconstruir secuencia y relaciones previas a la recuperación; es evidencia de proceso, no necesariamente de autoría |
| `merge-20260831/fused/origins/*/docs/recovered/.../MANIFEST.json` | Conecta sesiones recuperadas y sus artefactos; las copias entre orígenes deben compararse como familias |
| `merge-20260831/fused/origins/*/context/code_structure_index.json` | Resume el código por impacto; el índice activo registra 1.028 Python, 261.767 líneas y 11.404 símbolos |

## Prioridad 3 — candidatos concretos de posible trabajo recuperable

- Los 43 registros `review_evidence` del CSV, especialmente `rd_universo_entidades`, `rd_grafo_relaciones`, `rd_indice_integracion_relaciones`, `rd_post_chemsex_*`, `Testeo 2025.source.xlsx` y `CARRUSEL CHEMSEX RevCO.pdf`.
- Los 683 `review_live_alias`: no son duplicados confirmados; son rutas que pueden tener un alias vivo o una relación externa que el nombre no resolvió. Deben cruzarse por contenido y contexto.
- `merge-20260831/fused/projection3` y sus orígenes: los archivos divergentes son más interesantes que los iguales, porque pueden contener decisiones o trabajo alternativo.
- Fuentes visuales que queden fuera de `duplicados exactos`: validar firma real, capas, texto y dimensiones antes de clasificarlas como preview o fuente.

## Prioridad 4 — baja prioridad salvo excepción

Los JSON de `venvs_oi/.../site-packages`, `.deb`, `.exe`, `.so`, `.gz`, `.pyi` y caches numéricos parecen dependencias o artefactos reproducibles. No se descartan automáticamente: una excepción sería una versión necesaria para reproducir una ejecución o una pieza que no pueda reinstalarse.

## Regla de decisión

Un archivo sube de prioridad si conecta muchos otros, documenta una decisión, es una fuente editable, no tiene equivalente externo o presenta una diferencia significativa. Baja de prioridad si es dependencia estándar, salida regenerable, copia exacta ya apartada o archivo vacío de estructura.

## Resultado de esta pasada

La investigación ya no debería recorrer los 24 mil pendientes por orden de extensión. Debe resolver primero los cuatro centros de prioridad 1, después la cola de revisión del CSV, y solo entonces abrir los grupos históricos, visuales o de código que permanezcan sin explicación.

## Análisis de la cola `review_evidence`

La cola contiene **43 filas**, pero no 43 hallazgos independientes: varias son dos rutas de recuperación para el mismo artefacto.

### Grupo recuperable de mayor valor

Los artefactos `rd_universo_entidades`, `rd_reactivos_*`, `rd_grafo_relaciones`, `rd_indice_integracion_relaciones`, `rd_post_chemsex_*`, `rd_testeos_eventos_2025_*`, `CARRUSEL CHEMSEX RevCO.pdf` y `Testeo 2025.source.xlsx` forman una cadena coherente: fuentes → entidades/reactivos → relaciones → prototipos → integración → evidencia de testeos. No deben evaluarse como archivos sueltos. El posible ahorro de trabajo está en reconstruir esa cadena y determinar qué salida ya existe fuera y cuál conserva contexto de recuperación.

### Grupo que parece residuo técnico

Los tres `.sqlite-wal` de tamaño cero y los `.sqlite-shm` de 32 KB son componentes auxiliares de SQLite. Aislados no contienen la base principal; no deben interpretarse como evidencia perdida sin comprobar si la base y su journal correspondiente forman un conjunto consistente.

### Grupo visual/prototipo

`rd_post_cover_prototype` aparece como HTML, PNG y SVG en dos rutas de recuperación. La multiplicidad es una familia de exportación, no seis piezas independientes. Hay que verificar si el SVG conserva edición y si HTML/PNG son solo presentación.

### Lectura operativa

La revisión inmediata debe concentrarse en la cadena Chemsex/relaciones/testeos y en `CARRUSEL CHEMSEX RevCO.pdf`; después se puede cerrar la clasificación de los WAL/SHM como auxiliares. Esto ofrece más información por minuto que revisar los miles de archivos de entorno.

## Verificación contra el estado externo

La búsqueda actual encontró fuera de `_archive` varias piezas de esa misma cadena: `rd_post_chemsex_spec`, `rd_post_chemsex_visual_brief`, `rd_indice_integracion_relaciones`, `Testeo 2025.source.xlsx`, `CARRUSEL CHEMSEX RevCO.pdf`, `rd_testeos_eventos_2025_evidence`, `rd_reactivos_normalizados`, `rd_grafo_relaciones`, `rd_universo_entidades` y el SVG del prototipo. Por eso su valor no está, en principio, en ser copias únicas: está en la **ruta de recuperación, el contexto de sesión y la relación entre etapas**.

La excepción que merece conservar contexto es el conjunto de prototipos Chemsex: aunque el artefacto exista fuera, la copia recuperada puede documentar cómo se generó, qué fuente declaró y qué salida se pretendía integrar. En cambio, los WAL/SHM vacíos o pequeños no aportan por sí solos ese contexto y pueden bajar de prioridad después de comprobar su pareja SQLite.

**Conclusión de esta etapa:** la cola `review_evidence` no contiene principalmente “tesoros ocultos” aislados; contiene una reconstrucción de trabajo ya parcialmente materializado fuera. Su utilidad forense es probar continuidad, decisiones y trazabilidad. El siguiente salto de valor está en los 683 `review_live_alias` y en las rutas divergentes de `merge`, donde todavía puede haber diferencias no resueltas.

## Primer análisis de `review_live_alias`

La cola tiene 683 filas, pero solo **586 con contenido**, que suman aproximadamente **1,06 GB**. Esto cambia la prioridad: no es una cola de pequeños metadatos, sino una mezcla de alias creativos, variantes de proyecto y archivos estructurados.

### Candidatos de mayor valor

- `RD/suplementos/hongos adaptogenos copia.tif` (≈159 MB), `post fiesta.tif` (≈132 MB) e `impulso .tif` (≈83 MB): posibles fuentes raster de alta resolución. Aunque tengan alias externos propuestos, hay que verificar si son la misma imagen, una versión distinta o una fuente de impresión.
- `RD/AUTOMATIZACION/RD.blend1` y `RD/AUTOMATIZACION/RD.pre-glassfitwidth-20260818.blend` (≈126 MB cada uno): archivos Blender que podrían contener estados de trabajo, geometría o ajustes previos; no deben tratarse como simples renders.
- Las exportaciones `CREATINA`, `HONGOS`, `IMPULSO`, `PREFIESTA` y `POST FIESTA` en carpetas `6692`, `6699`, `PRUEBA` y `export/2`: forman familias de diseño. El alias puede ocultar una variante de cliente, no solo una copia.
- `flujo/.../runs/{full-baseline,enriched,enriched-technical-surface-20260827}` de ARICA: varios tamaños coinciden y apuntan a la misma entrada o salida. Deben compararse semánticamente; no son tres observaciones independientes por el mero hecho de estar en tres runs.
- `contraportada_cambios.svg` frente a la ruta del job de contraportadas: candidato de fuente editable y potencial ahorro directo de trabajo.

### Candidatos de baja prioridad dentro de la misma cola

Los `.gitkeep`, locks, logs vacíos y archivos auxiliares de SQLite no deberían ocupar la revisión inicial. Los aliases de corpus textual con el mismo hash aparente son menos urgentes que los TIFF, BLEND, SVG y PNG, porque el material creativo puede conservar estados editables o decisiones visuales.

### Límite de la evidencia

`review_live_alias` identifica coincidencia potencial por nombre/tamaño y una ruta canónica sugerida; no prueba igualdad de bytes ni equivalencia semántica. La siguiente acción correcta es calcular SHA-256 solo para estos candidatos no triviales y luego inspeccionar visualmente/estructuralmente los que difieran.

## Resultado de la comprobación de los candidatos grandes

La búsqueda por rutas externas exactas no confirmó las rutas sugeridas para los principales TIFF, BLEND, PNG y varios JSON de ARICA. Esto es importante: **no deben llamarse duplicados externos**. En el CSV son aliases potenciales, no equivalencias probadas. La única ruta grande de esta muestra que sí se localizó externamente por coincidencia de ruta es `flujo/svg/suplementos_rd/_plantilla/contraportada_cambios.svg`.

Por tanto, los TIFF/BLEND y las exportaciones creativas suben a **alta prioridad**: pueden ser material que existe solo en `_archive`, o pueden estar fuera bajo otra raíz/nombre. El siguiente paso correcto es resolver la raíz física de cada candidato y comparar SHA-256; hasta entonces su estado es `unresolved`, no `duplicate` ni `unique`.

## Resultado de la búsqueda por nombre

La búsqueda de nombres exactos fuera de `_archive` no encontró los principales TIFF (`hongos adaptogenos copia.tif`, `post fiesta.tif`, `impulso .tif`), los BLEND (`RD.blend1`, `RD.pre-glassfitwidth-20260818.blend`) ni las exportaciones PNG grandes listadas arriba. Esto no prueba exclusividad si fueron renombrados o están en una raíz no indexada, pero sí elimina la hipótesis simple de “misma ruta disponible”.

Estado actual de esos candidatos: **referencia histórica no materializada / alias no resuelto**. La comprobación de existencia confirmó que, entre otros, `RD/AUTOMATIZACION/RD.blend1`, `RD/suplementos/hongos adaptogenos copia.tif`, `RD/suplementos/etiquetas/elegidos/export/6692/CREATINA.png` y la ruta literal de `ARICA/.../project-ir.json` no existen hoy con esa ruta dentro de `_archive`. El CSV describe un inventario o comparación anterior; no prueba que el archivo siga presente.

Esto corrige la interpretación anterior: la prioridad no es abrir esos objetos inmediatamente, sino rastrear si fueron materializados bajo otra ruta, si ya fueron apartados como duplicados o si solo quedaron documentados en el índice.

### Estado de materialización confirmado

- Los TIFF, BLEND y PNG grandes citados no tienen una materialización localizada por ese nombre dentro del `_archive` actual. Su presencia queda reducida, por ahora, a la referencia del CSV histórico; no es evidencia suficiente para afirmar que siguen disponibles.
- Los `project-ir.json` y `projection.json` de ARICA sí tienen materializaciones bajo `duplicados exactos/merge-active-flujo/...`, incluyendo las tres variantes principales. Por tanto, esos registros no representan trabajo perdido; representan familias ya apartadas y deben analizarse como variantes/duplicados contextualizados.
- `contraportada_cambios.svg` aparece en dos orígenes de `merge` y además en `duplicados exactos`; es un caso de materialización confirmada, no un candidato único.

Esta separación es el resultado útil del rastreo: **creativo grande = referencia no materializada; ARICA = familia materializada; contraportadas = duplicado contextualizado**.

## Medición del archivo actual pendiente

Sobre los **24.147 archivos** que permanecen fuera de `duplicados exactos` (≈2,81 GB), una clasificación por señales de ruta/formato arroja lo siguiente. Las categorías se superponen: un JSON puede ser simultáneamente un manifiesto, un log o evidencia histórica.

| Señal | Archivos | Peso aprox. | Interpretación |
|---|---:|---:|---|
| Entornos/dependencias (`venv`, `site-packages`, builds, caches) | 19.853 | 503,5 MB | Gran volumen, generalmente reproducible; revisar excepciones de versión |
| Recuperación/histórico (`recovered`, `rollback`, `quarantine`, `state`, logs históricos) | 184 | 35,3 MB | Pocos archivos, alta densidad contextual |
| Manifiestos/índices/censos/materializaciones | 231 | 122,2 MB | Centros de información; primera revisión recomendada |
| Logs/sesiones/eventos | 709 | 379,7 MB | Pueden reconstruir secuencias y decisiones |
| Visuales (`svg`, `png`, `jpg`, `tif`, `blend`, `pdf`) | 832 | 268,5 MB | Posibles fuentes/entregables; validar formato real |
| Datos (`json`, `jsonl`, `csv`, bases, `xlsx`) | 950 | 277,9 MB | Mayor potencial de relaciones y ahorro de trabajo |
| Código (`py`, `pyi`, `js`, `ts`, `c`, `html`) | 18.646 | 206,5 MB | Revisar por índices de símbolos e impacto, no linealmente |

La cifra decisiva es la densidad: los entornos concentran cantidad, mientras que 231 manifiestos/índices y 950 piezas de datos pueden explicar una fracción mucho mayor del archivo. Esto confirma que la estrategia correcta es **nodos primero, volumen después**.
