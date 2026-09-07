# Inventario estructurado de `_archive`

**Corte de medición:** 2026-09-03 · **alcance:** archivos regulares bajo `/home/mak/_archive` · **modo:** lectura solamente.

## 1. Magnitud y composición

| Agrupación física | Archivos | Peso |
|---|---:|---:|
| `orden-limpieza-20260828` | 20.179 | 2.427.983.845 B |
| `merge-20260831` | 11.473 | 2.191.382.846 B |
| `quarantine-20260806-20260809` | 4.086 | 181.491.943 B |
| `rollback-20260811-20260814` | 4.901 | 171.176.596 B |
| Otros 9 conjuntos | 204 | 95.896.426 B |
| **Total** | **40.843** | **5.067.657.656 B** |

La estructura describe estados/procedencias de conservación, no categorías de obra. `orden-limpieza` concentra dependencias, instaladores, salidas regenerables, evidencia de corrida y material sin consumidor; `merge` concentra orígenes de worktrees/repositorios, arqueología, pilotos y productos; `quarantine` conserva sesiones/worktrees; `rollback` conserva capturas y memoria histórica.

Los otros conjuntos medidos son: `root-preserve-20260902` (90 archivos, 93.832.119 B), `faro_sync_20260809` (5, 602.719 B), `shadow-copies-20260821` (7, 328.934 B), `external-tree-classification-20260902` (41, 285.833 B), `claude-job-python-20260902` (48, 204.242 B), `iris-editor-consolidation-20260902` (2, 206.773 B), `provider-retirement-20260820` (2, 81.424 B), `group4-reverted-20260821` (2, 39.262 B), `watsonx-retired-20260820` (6, 38.052 B) e `INDICE.md` (1, 3.068 B).

## 2. Formatos ordenados por peso

| Formato | Archivos | Peso |
|---|---:|---:|
| `.deb` | 3 | 1.230.377.016 B |
| `.json` | 3.022 | 804.127.158 B |
| `.svg` | 3.202 | 376.331.075 B |
| `.exe` | 32 | 299.702.296 B |
| `.sqlite` | 7 | 258.932.736 B |
| `.db` | 11 | 204.890.112 B |
| `.pdf` | 153 | 189.390.967 B |
| `.py` | 15.034 | 177.417.546 B |
| `.gz` | 21 | 164.967.552 B |
| `.so` | 82 | 159.977.010 B |
| `.png` | 189 | 155.901.452 B |
| `.duckdb` | 4 | 152.092.672 B |
| `.pack` | 6 | 134.276.369 B |
| `.jsonl` | 347 | 127.305.905 B |
| `.jpg` | 619 | 92.115.625 B |
| Sin extensión | 2.114 | 91.209.215 B |
| `.ai` | 3 | 90.136.491 B |
| `.zip` | 7 | 76.293.138 B |
| `.md` | 5.197 | 46.422.760 B |
| `.html` | 325 | 30.725.883 B |

El resto suma 5.641 archivos y 547.407.929 B. La extensión es solo una clasificación operacional; no valida contenido ni vigencia.

## 3. Concentración por subcolecciones

| Subcolección observable | Qué contiene | Evidencia de peso/tamaño |
|---|---|---:|
| `orden-limpieza/.../instalador-post-instalado` | instaladores de aplicaciones y paquetes | 1.657.802.617 B en los 5 mayores elementos; incluye `lm-studio.deb`, `chatgpt_amd64.deb`, `GoogleDriveSetup.exe`, `code_*.deb`, `Antigravity.tar.gz` |
| `merge/.../active-flujo/experiments/pilots/ARICA-FONDART-2027` | input, observación, unidades, práctica, proyección, plan y dossier de tres corridas | archivos repetidos entre `full-baseline`, `enriched` y `enriched-technical-surface-20260827` |
| `merge/.../out/archaeology` | bases y exportaciones de arqueología/conversaciones | incluye `claude-codex-mak-20260815.sqlite` (102.256.640 B), DuckDB y reportes |
| `merge/.../jobs/2026-07-05_contraportadas` | piezas AI/SVG de contraportadas y cambios | `FLYERS8.ai` (80.437.093 B), SVG individuales de ~5 MB |
| `merge/.../win-flujo/.git` y `runner-vibecodeine/.git` | objetos y packs Git conservados | packs de hasta 55.503.941 B; son datos internos de Git, no documentos de catálogo |
| `orden-limpieza/.../evidencia-de-corrida/drive` | renders PNG de issues/pruebas | varios renders de 16.618.0xx B |
| `rollback/.../research/memoria` | índice de memoria y material de recuperación | `index.jsonl` de 92.499.713 B |

## 4. Mayores archivos individuales

| Peso | Archivo relativo |
|---:|---|
| 666.783.888 B | `orden-limpieza-20260828/por-razon/instalador-post-instalado/lm-studio.deb` |
| 349.937.362 B | `orden-limpieza-20260828/por-razon/instalador-post-instalado/chatgpt_amd64.deb` |
| 262.878.360 B | `orden-limpieza-20260828/por-razon/instalador-post-instalado/GoogleDriveSetup.exe` |
| 213.655.766 B | `orden-limpieza-20260828/por-razon/instalador-post-instalado/code_1.129.0-1784074987_amd64.deb` |
| 190.283.776 B | `merge-20260831/fused/origins/active-flujo/data/mak_knowledge.db` |
| 164.580.201 B | `orden-limpieza-20260828/por-razon/instalador-post-instalado/Antigravity.tar.gz` |
| 102.256.640 B | `merge-20260831/fused/origins/active-flujo/out/archaeology/claude-codex-mak-20260815.sqlite` |
| 92.499.713 B | `rollback-20260811-20260814/faro-live-before-recovered-20260812/research/memoria/index.jsonl` |
| 80.437.093 B | `merge-20260831/fused/origins/active-flujo/jobs/2026-07-05_contraportadas/productos_cambios/FLYERS8.ai` |
| 78.385.152 B | `merge-20260831/fused/origins/win-flujo/out/archaeology/claude_code_web_codex.sqlite` |

## 5. Relaciones observables

Se calcularon SHA-256 para archivos de 100 KiB o más: **275 grupos de coincidencia exacta**, **858 archivos involucrados**. Esto evidencia duplicación física o réplicas; no prueba que todos los archivos con nombres parecidos sean iguales.

- `ARICA-FONDART-2027`: las corridas `full-baseline`, `enriched` y `enriched-technical-surface-20260827` comparten archivos exactos en `project-ir`, `projection`, `observation`, `units`, `practice` y `product-plan`; son variantes/capturas de una misma cadena de piloto.
- `rd_fuentes/testeo_eventos_2025_evidence.json` aparece idéntico en `active-flujo`, `runner-vibecodeine` y sesiones recuperadas; relación de fuente replicada.
- Los SVG de `suplementos_rd/09_contraportadas_dark` se repiten entre `active-flujo`, `runner-vibecodeine`, `win-flujo` y dos worktrees de quarantine; relación de producto/worktree, con variantes de bytes en algunos casos.
- `municipal-fondos-concursables-2026.pdf` aparece idéntico en tres orígenes del merge.
- `python_census_20260901.json` está duplicado entre `context` y `generated-context` dentro de `root-preserve`.

**Límite:** las relaciones anteriores son de ruta, nombre, ubicación de corrida o igualdad criptográfica. No se infiere identidad artística, autoría, publicación ni que una copia sea descartable.

## 6. Evaluación de valor (lectura de contenido)

| Nivel | Material | Por qué importa | Acción prudente |
|---|---|---|---|
| **Muy alto** | `entregado-a-cliente/` (6 propuestas PDF) y `merge/.../jobs/2026-07-05_contraportadas/` (AI, SVG, PDF, `reporte_job.md`, `estado.md`, `regen_deliverables.py`) | Son entregables y fuentes editables; los PDF preservan versiones de presentación y AI/SVG permiten reconstrucción o reimpresión. | Tratar como activos de trabajo/entrega. No deduplicar por nombre; revisar visualmente solo si se necesita recuperar una pieza. |
| **Muy alto** | `ARICA-FONDART-2027` completo | No es basura de build: contiene input, observación, unidades, práctica, proyección, plan y dossier. Es evidencia de un piloto y permite comparar qué cambió entre corridas. | Conservar la separación entre input, runs y outputs; la igualdad `observation.json`/input es un hallazgo que requiere explicación, no borrado. |
| **Alto** | `rollback/.../research/memoria`, `curatoria`, `plataforma` y `local-reconciliation` | Contiene memoria de decisiones, fallos, órdenes, corpus benchmark y estados de recuperación; puede explicar por qué se tomó una decisión histórica. | Usarlo como histórico, no como estado vigente. |
| **Alto** | `merge/.../out/archaeology` y `.git` de los orígenes | Bases SQLite/DuckDB, packs Git y reportes pueden recuperar contexto, historial y procedencia que no aparece en los archivos activos. | Conservar como evidencia técnica; consultar copias, no editar bases/WAL. |
| **Medio-alto** | `evidencia-de-corrida/` y `quarantine/faro-20260806` | Renders, logs, snapshots y lotes crudos prueban ejecuciones y estados de una época; útiles para reconstruir errores o decisiones. | Valiosos como evidencia, no necesariamente como productos utilizables. |
| **Medio** | `subsistema-retirado-20260814/`, `proveedor-retirado/`, venvs y scripts | El código puede contener lógica recuperable, pero fue retirado por falta de consumidor o dependencia; su valor es histórico y de reversión. | No reactivar automáticamente; leer dependencias antes de reutilizar. |
| **Bajo / prescindible como activo** | instaladores `.deb`, `.exe`, `.tar.gz`, `.so` y salidas regenerables | Ocupan gran parte del peso, pero son software ya instalado, binarios incompatibles o productos reproducibles. | Mantener solo si se necesita recuperación offline; no confundir peso con valor. |

**Conclusión analítica:** sí hay material valioso, pero está concentrado en tres núcleos: (1) originales y entregables visuales, (2) el piloto ARICA y sus artefactos derivados, y (3) memoria/arqueología que conserva decisiones y procedencia. El mayor riesgo es que los binarios y duplicados voluminosos oculten esos activos. La clasificación por extensión sola no los distingue.

## 7. Lectura forense: qué cuenta como evidencia y qué cuenta como valor

### Núcleo A — activos creativos y comerciales: valor alto, pérdida concreta

La cadena `2026-07-05_contraportadas` contiene `brief.yaml`, `estado.md`, `reporte_job.md`, un `.ai`, `cambios.svg/.pdf`, SVG por producto y PDF por producto, además de un script de regeneración. La presencia simultánea de brief + fuente editable + cambios + salidas permite reconstruir intención, iteración y resultado técnico. Pero los documentos de control dicen `pendiente_datos`: cliente, proyecto, medida, orientación, productos y texto aprobado están pendientes. Es una producción técnicamente avanzada pero semánticamente inconclusa, no una entrega confirmada. Los nombres de producto muestran una familia coherente, no aprobación.

Los seis PDF de `entregado-a-cliente` tienen valor como posibles versiones de presentación, pero la ruta no demuestra aceptación, pago ni uso. El `.ai` y los SVG son los elementos más irremplazables; los PDF prueban qué archivo fue preparado/preservado. La relación entre ambos debe conservarse aunque existan copias exactas en otros worktrees.

### Núcleo B — archivo de práctica/proyecto: valor alto, pero con una anomalía de derivación

`ARICA-FONDART-2027` contiene una secuencia reconocible: `input/archive_observation.json` → `observation.json` → `units.json` → `practice.json` → `projection.json` → `product-plan.json` → `portfolio-dossier.json`, repetida en tres corridas. Esto es más valioso que un resultado suelto porque permite auditar transformación y comparar versiones.

La anomalía forense crítica es que `runs/*/observation.json` es byte-identical a `input/archive_observation.json`: el supuesto “resultado de observación” parece ser una copia del insumo, no una observación nueva. Eso no invalida el piloto, pero impide atribuirle valor de medición independiente. Los archivos posteriores pueden ser derivados reales o pueden estar contaminados por esa copia; requieren revisión de sus campos y metadatos antes de usarlos como evidencia.

### Núcleo C — memoria y trazabilidad: valor probatorio alto, valor semántico desigual

`rollback` conserva más que backups: hay decisiones curatoriales, fallos, órdenes, benchmarks, snapshots de runtime, transcripciones y resultados de modelos. El documento `PRIMERA_RONDA_VISUAL.md`, por ejemplo, registra 40/40 reels con decisión humana y mantiene estados `borrador_no_promovido` o `requiere_revision_humana`; ese estado negativo es evidencia importante porque muestra qué no fue promovido. En cambio, los JSON de investigación que devuelven `unknown` o textos genéricos son evidencia de una búsqueda fallida, no evidencia del hecho investigado.

La memoria de sesiones es valiosa para reconstruir decisiones del operador, pero no debe tratarse como verdad de proyecto sin corroboración: mezcla turnos humanos, respuestas de asistentes, resultados de herramientas y compactaciones. Su valor principal es explicar el proceso y localizar fuentes primarias.

### Anomalías y riesgos concretos

- `MANIFEST.md` contiene contradicciones internas: habla de 25 entradas cuando el mapa tiene más, y declara que `checkpoints/` sobrevivió aunque material de checkpoints aparece archivado. El manifest no es una autoridad suficiente para reconstrucción.
- `mapa-de-retiro.csv` no cubre todo lo que físicamente existe bajo `por-razon/`; hay material cuya ruta original debe reconstruirse por Git o por contexto. Eso reduce la reversibilidad probada.
- La auditoría archivada documenta una afirmación falsa sobre ausencia de PostgreSQL y un entorno Python que no era subconjunto estricto del entorno vivo. Por tanto, las razones de retiro son pistas históricas, no conclusiones confiables.
- Hay archivos con aspecto sensible (`.env`, credenciales documentadas, bases de conocimiento, transcripciones). Su valor puede ser alto, pero también su riesgo de exposición. No deben publicarse ni copiarse a un catálogo de acceso abierto.

**Dictamen:** los activos de mayor prioridad son el job de contraportadas, las propuestas entregadas, el conjunto ARICA completo y el rollback de decisiones curatoriales. El archivo no contiene solo “sobrantes”: contiene fuentes, pruebas de proceso, fallos y memoria de decisiones. La distinción decisiva es entre evidencia primaria (fuentes editables, entregables, inputs, capturas humanas), derivado (runs, proyecciones, dossiers) y relato secundario (manifests, auditorías, logs). Solo la primera categoría puede sostener por sí sola una afirmación sobre lo ocurrido.

**Corrección:** el job de contraportadas debe clasificarse como `fuente creativa recuperable / estado pendiente`, no como `entrega cerrada`. Además, `projection3/MANIFEST.json` cuantifica el conflicto entre orígenes: 5.426 rutas, 3.087 iguales, 813 divergentes y 2.366 variantes. El merge es una colección de testimonios relacionados, no una autoridad única.

## 8. Triage de valor: basura real, ahorro de trabajo y piezas a proteger

Esta es una clasificación de pérdida: pregunta qué se perdería si el archivo desapareciera. No autoriza borrar ni mover.

### A. Basura real o casi-basura — **baja pérdida informacional**

| Grupo | Motivo del triage | Reserva |
|---|---|---|
| Logs de smoke, debug y ejecución (`hub_smoke_*`, `barrierc-xtest-debug.log`, `rclone.log`, `pytest_isolated_run.log`) | Son registros de una ejecución puntual; no son fuente de obra ni estado actual. | Conservar si se está investigando el fallo que registran. |
| Cachés y residuos de herramientas (`.playwright-mcp`, `.remember` terminado, archivos temporales de builds) | Regenerables y sin relación semántica con una pieza; su utilidad cae rápidamente. | Verificar primero que no sean la única copia de una decisión humana. |
| Paquetes de instalación ya consumidos (`chatgpt_amd64.deb`, `lm-studio.deb`, `code_*.deb`, `Antigravity.tar.gz`) y `.exe` incompatible | El software ya estaba instalado o el instalador no sirve para el sistema actual; no ahorran trabajo creativo. | El `.exe` solo tendría valor como instalador histórico/offline. |
| Bibliotecas compiladas dentro de `venvs_oi` (`.so`, binarios de site-packages) | Se regeneran reinstalando dependencias; son grandes pero no contienen decisiones del proyecto. | El venv completo puede servir para reproducibilidad; no confundir “regenerable” con “inútil” si falta lock/configuración. |
| Objetos internos `.git/objects` y packs repetidos | No son archivos de trabajo legibles y hay varios orígenes. | Un pack puede contener historia no presente en el checkout; solo es basura después de verificar cobertura histórica. |

### B. Valioso e irremplazable — **proteger primero**

- Fuentes editables AI/SVG y sus PDF asociados en `merge/.../jobs/2026-07-05_contraportadas/`. Ahorran rehacer diseño, aunque el brief esté incompleto.
- Las seis propuestas PDF bajo `por-razon/entregado-a-cliente/`: posible evidencia de versiones presentadas; no asumir aceptación.
- Inputs y artefactos de `ARICA-FONDART-2027`: conservan la materia observada y la cadena de transformación.
- `PRIMERA_RONDA_VISUAL.md`, decisiones humanas, rechazos y estados `borrador_no_promovido`: ahorran repetir curaduría y conservan negativas que no aparecen en el producto final.
- Bases de arqueología, snapshots de rollback y transcripciones: pueden recuperar decisiones, contexto y procedencia que no están en el código actual.

### C. Material que probablemente ahorra mucho trabajo — **alto retorno práctico**

1. `projection3/MANIFEST.json`: permite saber qué origen es igual, divergente o variante sin comparar manualmente los 5.426 paths.
2. `mapa-de-retiro.csv` y los `POR-QUE.txt`: aunque incompletos/contradictorios, reducen el trabajo de reconstruir por qué se apartó cada conjunto.
3. `reporte_job.md`, `estado.md`, `brief.yaml` y `regen_deliverables.py`: juntos permiten retomar el job de contraportadas desde el estado real, detectando de inmediato que faltan datos/aprobación.
4. `project-ir`, `observation`, `units`, `practice`, `projection`, `product-plan` y `portfolio-dossier` de ARICA: permiten comparar corridas y localizar dónde aparece una diferencia real.
5. `raw/MANIFEST.json` y los hashes de evidencia: permiten distinguir copia de evidencia preservada de copia operativa.

### D. Conservar, pero no tomar como verdad — **revisión obligatoria**

Manifests, auditorías, `POR-QUE.txt`, reportes de agentes y logs tienen valor de contexto, pero contienen errores demostrados. Son mapas de investigación, no autoridad. La decisión correcta es conservarlos junto a sus archivos para poder estudiar el error, no usarlos solos para clasificar o eliminar.

### Decisión de triage

La reducción segura de trabajo no consiste en borrar los archivos más grandes. Consiste en separar mentalmente (y, solo después de validación, físicamente) binarios/cachés/logs de los cuatro núcleos que evitan rehacer trabajo: fuentes gráficas, propuestas PDF, ARICA y memoria de decisiones. Los duplicados deben consolidarse únicamente cuando se conserve la relación entre origen, función y contexto.

## Investigación de los nuevos candidatos

`mak_knowledge.db` contiene 49 tablas: 42.355 artefactos, 8.273 elementos en `classification_queue`, 8.331 entidades, 6.058 relaciones, 98.223 eventos temporales, 30.985 imports Python, 124 enlaces de catálogo, 7 fuentes de catálogo y 44 registros de proyecto. Sus tablas `archive_memory_*` están vacías y no hay `project_transitions`; es conocimiento estructurado de inventario/clasificación, no una memoria completa ni autoridad del presente. Su tratamiento de DrefQuila distingue `human_attested`, `observed` y `candidate`, lo que sí es valioso metodológicamente.

`claude-codex-mak-20260815.sqlite` contiene 28 tablas: 1.028 commits, 9.054 archivos asociados a commits, 213 acciones Codex, 508 seguimientos de ideas, 1.548 seguimientos de propuestas, 3.702 enlaces pregunta-respuesta, 22.632 candidatos y 18.930 señales. `claude_actions`, `mak_activity` y `memories` están vacías. Es una reconstrucción del proceso de trabajo y Git, no una memoria textual completa.

`projection3/MANIFEST.json` reúne `win-flujo`, `runner-vibecodeine` y `active-flujo`, y registra 5.426 rutas: 3.087 iguales, 813 rutas con variantes preservadas, 2.366 archivos variante y 129 directorios generados excluidos. Es un índice de procedencia que ahorra comparar árboles completos, pero no resuelve la autoridad entre versiones.

### Veredicto de estos tres candidatos

- `FLYERS8.ai` tiene extensión engañosa: el identificador de archivo lo reconoce como **PDF de 19 páginas**, con imágenes embebidas. Es valioso como posible composición/render, pero no se puede afirmar que sea una fuente Illustrator editable sin inspección de apertura.
- `claude_code_web_codex.sqlite` contiene 58.879 turnos, 926 commits, 8.342 asociaciones archivo-commit, 4.405 enlaces pregunta-respuesta, 30.800 candidatos y 26.395 señales. Es memoria de proceso y Git; no contiene memoria consolidada porque sus tablas de memoria no son el núcleo poblado.
- `CAPACIDADES.md` describe el sistema y sus consumidores con mediciones fechadas al 2026-08-09. Es el mejor ahorrador de trabajo de los tres para orientación, pero pierde autoridad si contradice el repo o la máquina actuales.

### Existencia fuera de `_archive`

| Candidato | Resultado fuera de `_archive` | Lectura |
|---|---|---|
| `mak_knowledge.db` | `/home/mak/data/mak_knowledge.db`; SHA-256 idéntico a la copia archivada | No es único; el archivo conserva un snapshot de una base que también está viva fuera. |
| `claude-codex-mak-20260815.sqlite` | No encontrado fuera de `_archive` | Único ejemplar localizado; alta prioridad de preservación. |
| `projection3/MANIFEST.json` | No encontrado fuera de `_archive` | Único índice localizado; perderlo obliga a reconstruir la comparación del merge. |

La búsqueda se hizo por nombres exactos y equivalentes obvios en las raíces operativas (`data`, `context`, `state`, `labs`, `tools`, `flujo`). La igualdad de `mak_knowledge.db` se verificó por SHA-256 completo; para los otros dos no se afirma que no pueda existir una copia con nombre completamente distinto, solo que no fue localizada en el alcance medido.

## 11. Resultados de investigación de candidatos

En ARICA, `observation.json`, `units.json` y `projection.json` son idénticos entre las tres corridas grandes; `observation.json` coincide además con el input. `practice.json`, `product-plan.json` y `portfolio-dossier.json` sí divergen. Se reutilizó una observación común y cambiaron principalmente capas interpretativas/derivadas; esto ahorra reobservación, pero impide contar cada corrida como evidencia independiente.

El job de contraportadas está documentado como `pendiente_datos`: faltan cliente, proyecto, medidas, productos y aprobación textual. Tiene alto valor de recuperación técnica, pero no prueba cierre comercial.

La primera ronda visual registra 40/40 decisiones humanas, 106 historias candidatas, 155 carruseles y promoción pública bloqueada. `sin_episodio_confirmado` reúne 18 medios y 11 rechazos: su valor está en el criterio de selección y abstención.

En DREF, el `cue_map` archivado y el vivo difieren en bytes, pero tienen igual estructura JSON y 21 cues. `DREFGIRA/misionar` aparece en los JSON de reconstrucción; no hay prueba de videos originales físicamente almacenados en `_archive`. `Escarlata (Remix)` tiene evidencia pública, pero no identificación definitiva del archivo audiovisual local.

## 9. Dref Chocolate: comparación con la copia viva

El kit aparece en `_archive/merge-20260831/fused/origins/active-flujo/xio/show_kit/` y en `/home/mak/xio/show_kit/`. La comparación SHA-256 confirmó igualdad exacta para `dref_chocolate.noisette`, `map_dref.py`, `setlist_durations_dref.json`, `ANOTACIONES_SHOW_20260724.md`, `DIA_DEL_SHOW.md`, el README y los tres registros JSONL. La única divergencia es `cue_map_dref.json`: 4.340 bytes archivados frente a 4.548 bytes vivos.

Los registros del show no son únicos del archivo y pueden usarse desde `/home/mak/xio/show_kit/`. El `cue_map` archivado sí conserva una versión histórica capaz de explicar un cambio de operación.

## 10. Tres candidatos de seguimiento

| Candidato | Señal | Pregunta |
|---|---|---|
| `cue_map_dref.json` | única divergencia del kit DREF CHOCOLATE | ¿Qué cues fueron agregados, quitados o reordenados? |
| `DREFGIRA/misionar` | coincidencia directa con una canción verificable | ¿Qué archivos son obra/show y cuáles son assets? |
| `Escarlata (Remix)` | colaboración pública respaldada, binding físico aún candidato | ¿Qué archivo local corresponde, si alguno, a la publicación? |
