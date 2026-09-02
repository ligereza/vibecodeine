# LUNA-571 — Auditoría de DIMENSIONES DEL ORDEN

**Identidad:** `LUNA-571-DIMENSIONES-DEL-ORDEN`  
**Modelo:** LUNA  
**Fecha de auditoría:** 2026-08-18  
**Fuente principal:** `/home/mak/curatoria_inbox/DIMENSIONES DEL ORDEN`  
**Write set usado:** únicamente este archivo y `LUNA-571_DIMENSIONES_DEL_ORDEN_CROSSWALK.csv`.

## Resumen ejecutivo

DIMENSIONES DEL ORDEN es un subproyecto autónomo de análisis de archivos, no un runtime integrado de MAK. Su núcleo valioso es una capa de evidencia derivada que convierte un árbol creativo en inventario, proyectos, familias, procedencia, unidades de trabajo, dossiers y decisiones virtuales. No debe copiarse la carpeta completa al repositorio MAK.

La incorporación recomendada es selectiva:

1. **Conocimiento estructurado:** adoptar el contrato de fuente inmutable → evidencia derivada → decisión virtual → revisión humana → acción reversible futura; conservar las semánticas `project_id`, `asset_id`, `provenance`, `confidence`, `consumer`, `publico`, `source_or_derived` y la distinción entre fuente, derivado y evidencia.
2. **Herramienta funcional prioritaria:** adaptar `ia_work_units.py` + `ia_automated_curator.py` mediante un puente read-only para Curatoria. El primer slice debe producir planes de familia compatibles con `mak-family-triangulation-plan-v1`, sin mover archivos.
3. **Research:** mantener `ia_flujo_idea_projection.py` y `funding_os_projection.py` como adaptadores externos hasta que haya un proyecto canónico y un consumidor Research explícito. No hay matches ni aplicaciones verificadas en Funding OS.
4. **Fuera del runtime MAK:** `catalog.sqlite3` y `ia_web_system_v2.sqlite3` deben permanecer como catálogos derivados externos o como evidencia bajo una política de acceso read-only. El `.catalog-env`, `.git` anidado, `.pyc`, `.pyd`, `.dll`, `.exe`, previews y dashboards generados no deben entrar al repo.

La evidencia más importante es también el límite: el catálogo rico cubre 65.855 archivos y 908 proyectos, mientras el snapshot físico de origen que los documentos describen alcanza 1.439.409 archivos y 32.085.322.217 bytes. La cobertura no autoriza inferir que lo no indexado sea basura. El benchmark deja `physical_gate_open=false`; el sistema reporta cero acciones físicas y cero bytes recuperados.

## Arquitectura real

El árbol auditado no contiene el árbol original `C:\IA`; contiene scripts, documentación y proyecciones derivadas de ejecuciones históricas. La arquitectura efectiva es:

```text
documentación y scripts Python
        |
        +--> catalog.sqlite3              inventario mecánico antiguo
        +--> ia_web_system_v2.sqlite3     catálogo rico de 65.855 archivos / 908 proyectos
        +--> ia_*_report.json             reportes de análisis y seguridad
        +--> ia_*_board.html / previews   presentaciones derivadas
        +--> ia_flujo_idea_projection...  proyección de ideas y archivos
        +--> orden_learning.sqlite3      memoria metodológica
        +--> .catalog-env / .git          límites y residuos de transporte
```

El contrato arquitectónico canónico define una cadena de solo lectura:

```text
fuente inmutable
  -> snapshot / inventario
  -> evidencia derivada
  -> unidades de trabajo y dossiers
  -> índice virtual
  -> revisión humana
  -> acción futura reversible, por defecto cero
```

Esto es coherente con MAK: `/home/mak/*` es la autoridad física, `/home/mak/flujo` es el baseline de autoría e integración, y Git no decide por sí solo qué existe. El `.git` anidado se inspeccionó solo como límite físico; no se usó como inventario.

## Inventario físico y proveniencia

### Escala observada

| Superficie | Evidencia física | Lectura |
|---|---:|---|
| `/home/mak` | `du -sh`: aproximadamente 2.2G en la corrida | superficie MAK inspeccionada primero |
| DIMENSIONES DEL ORDEN | 1.7G; 15.449 archivos; 1.190 directorios | árbol de auditoría, no destino de copia |
| `.git` anidado | 6.884 archivos; objetos sueltos de hasta 95.975.807 bytes | transporte/evidencia, no inventario único |
| `.catalog-env` | 8.332 archivos | entorno compilado de Windows, excluir del runtime |
| `ia_order_visual_previews` | 41 PNG, 491.602 bytes | previews generados |
| `ia_order_visual_previews_js` | 56 PNG, 694.573 bytes | previews generados por variante JS |
| `ia_web_previews` | 25 archivos, 696.041 bytes | previews HTML/PNG derivados |

La distribución física de extensiones está dominada por el entorno y dependencias compiladas: 3.317 `.py`, 3.308 `.pyc`, 195 `.pyd`, 34 `.dll`, 39 `.exe`, 6 SQLite, 36 JSON, 33 Markdown, 6 HTML, 30 CSV y 98 TXT. Los conteos de `.pyc`, `.pyd`, `.dll` y `.exe` no representan código fuente propio del subproyecto. La primera corrida dio 15.449 archivos y el recuento final dio 15.447; se trata como deriva física no explicada y no como prueba de borrado o estabilidad.

### Hashes y fechas representativos

La corrida `find ... | xargs sha256sum` terminó con código 0 para las fuentes documentales, Python, JSON, HTML y SQLite fuera de `.git` y `.catalog-env`. Se registran muestras para poder detectar deriva:

| Path | Bytes | Fecha observada | SHA-256 |
|---|---:|---|---|
| `catalog.sqlite3` | 651.309.056 | 2026-08-15 21:17:36 | `d7479c0d5045f267c0194878603145f4e50c86a439140aaa655b84d8380ccc5d` |
| `ia_web_system_v2.sqlite3` | 77.406.208 | 2026-08-17 05:43:12 | `70f7ea9ff4b8e104d7e4695954ad158abd039133eedf478e69c9486f2485fed0` |
| `ia_flujo_idea_projection.sqlite3` | 9.699.328 | 2026-08-17 06:21:14 | `00226dc08393d050d13aba94e9c8dcd45144f2b01ac40f84395d4c798b773625` |
| `orden_learning.sqlite3` | 200.704 | 2026-08-17 23:11:59 | `bd4afc0b9b75e232d4f7e6c735119e28bf876543408685fe0b59df50eb25e960` |
| `ia_web_system.py` | 12.889 | 2026-08-17 03:30:36 | `18c024265bad3ef7ded34aefcc7c5f266b61710458e820df4b27641a6fdf73cc` |
| `ia_work_units.py` | 11.080 | 2026-08-17 05:43:06 | `9794cd9cdfc12f7c2e3127f1c004412a0b8cff14bc39acb469ed64775efed18e` |
| `DIMENSIONES_DEL_ORDEN_ARCHITECTURE.md` | 6.493 | 2026-08-17 05:57:32 | `8c777c630b6e289d4beb7ec28a0f48f89a00b711549374cfbc4a165030b0feba` |

Los hashes completos de todos los candidatos auditados quedaron observados en stdout; el CSV concentra los hashes de los candidatos críticos.

## Mapa de familias

| Familia | Fuente funcional | Datos/derivados | Presentación | Owner propuesto | Estado MAK |
|---|---|---|---|---|---|
| Inventario mecánico | `catalog_tool.py`, `catalog_report.py` | `catalog.sqlite3`, `catalog_scope.json` | `catalog_dashboard.*` | Curatoria | equivalente parcial en `src/flujo/index/` e `ingesta_archivo.py`; no fusionar a ciegas |
| Catálogo web | `ia_web_catalog.py`, `ia_web_system.py`, `ia_web_finalize.py`, `ia_web_relations.py` | `ia_web_system*.sqlite3`, `ia_web_report.json` | `ia_web_previews/` | Curatoria / Cultura | solo externo; fuente útil para adaptación read-only |
| Estructura de interfaz | `ia_interface_analysis.py`, `ia_interface_clusters.py`, `ia_package_classify.py` | análisis, clusters, clasificación | boards y colas | Curatoria | no hay consumidor directo |
| Origen e historia | `ia_project_origin.py`, `ia_repo_history.py` | tablas de origen y co-cambio | reportes JSON | Curatoria / Research | evidencia útil; Code Maat bloqueado por Java y Repowise escribe en raíz |
| Orden virtual | `ia_order_simulator.py`, `ia_automated_curator.py`, `ia_work_units.py` | `order_virtual_index`, dossiers, 24 unidades | `ia_order_review*`, `ia_family_board*` | Curatoria | candidato principal de adaptación |
| Feedback y aprendizaje | `orden_learning.py`, `ia_feedback_instrumentation.py`, `ia_system_audit.py` | 53 reglas, 29 eventos, 17 trials, 0 feedback humano | colas/reportes | Cultura/MAK + Curatoria | adaptar contrato, no copiar SQLite |
| Ideas → materiales | `ia_flujo_idea_projection.py` | 25 nodos materiales, 33.001 archivos, 1.176 ideas, 34 relaciones | reporte JSON | Research / Cultura | adaptador secundario; depende de fuentes externas y ONNX |
| Funding OS | `funding_os_projection.py` | 20 oportunidades, 143 requisitos, 140 tareas, 11 evidencias, 0 matches | reporte JSON | Research | externo; aún no está listo para postulación |
| Pilotos públicos | `ia_pilot_intelligence.py`, `ia_pilot_public_matches.py` | 2.187 metadata, 5 proyectos piloto, 0 matches públicos | reportes | Research | conservar evidencia; no promover claims |

## Separación fuente / derivado / evidencia

### Fuente funcional

Los `.py` son la parte más reutilizable, pero no todos son runtime portable. AST sobre los 29 scripts Python de la raíz: todos parsean; todos tienen guardia `__main__`; varios importan solo stdlib, mientras `ia_flujo_idea_projection.py` requiere `numpy`, `onnxruntime` y `tokenizers`, `ia_pilot_intelligence.py` requiere `PIL` y `cv2`, y los previews requieren Playwright.

La existencia de una guardia `__main__` no significa que una ejecución sea read-only: el AST detectó `sqlite3.connect`, `execute` y escrituras de JSON/HTML en la mayoría de los scripts. La adaptación debe abrir las bases de entrada con `file:...?mode=ro`, establecer `PRAGMA query_only=ON` y escribir solo una proyección fuera de la fuente.

### Datos

Las seis bases SQLite son snapshots o memorias derivadas. Ninguna es la fuente original del árbol creativo. `catalog.sqlite3` es un inventario mecánico; `ia_web_system_v2.sqlite3` es la proyección rica; `ia_flujo_idea_projection.sqlite3` es una relación candidata entre ideas y materiales; `orden_learning.sqlite3` es memoria de método. Los `-wal` y `-shm` existentes se consideran acompañantes de persistencia y no deben copiarse sin su base y un protocolo de consistencia.

### Presentación

Los HTML, JSON de boards, PNG y colas visuales son vistas derivadas. Un dashboard no prueba que una clasificación sea correcta; un preview negro o ausente es un estado de render; un PNG nunca debe presentarse como fuente original. Las dos familias `ia_order_visual_previews*` contienen duplicación de previews, no duplicación demostrada de proyectos.

### Residuos y límites

`.git` anidado, `.catalog-env`, `.pyc`, `.pyd`, `.dll`, `.exe`, `__pycache__`, `-wal`, `-shm`, caches, previews y temporales son límites operativos o artefactos generados. Deben conservarse como evidencia cuando su procedencia sea relevante, pero no deben entrar en el runtime MAK.

## Análisis de bases SQLite

Todas las consultas se ejecutaron con conexión URI `mode=ro` y `PRAGMA query_only=ON`. Las seis bases SQLite auditadas pasaron `PRAGMA integrity_check` con resultado `ok`.

| Base | Tamaño | Tablas/filas relevantes | Lectura | Disposición |
|---|---:|---|---|---|
| `catalog.sqlite3` | 651 MB | `files` 1.077.162; `scan_runs` 2; 1.077.162 filas de una corrida con 49 errores | inventario mecánico; categorías incluyen cache/temp | mantener externa; evidencia y posible consulta acotada |
| `ia_web_system_v2.sqlite3` | 73.8 MB | `file` 65.855; `project` 908; `project_dossier` 908; `work_unit` 24; `project_dossier_evidence` 9.034; `web_ref` 27.096; `order_action` 0 | catálogo rico, derivado y trazable | conservar externo; entrada read-only del primer puente |
| `ia_web_system.sqlite3` | 1.8 MB | `file` 2.349; `web_analysis` 104; `project` 0 | snapshot parcial/antiguo | conservar como evidencia, no runtime |
| `ia_web_catalog.sqlite3` | 64 KB | esquema creado, `file`/`project`/análisis en 0 filas; `scan` 1 | scaffold vacío | cuarentenar como evidencia de diseño |
| `ia_flujo_idea_projection.sqlite3` | 9.2 MB | `file_node` 33.001; `material_node` 25; `idea_node` 1.176; `relation_candidate` 34; `idea_fanout` 417 | relaciones candidatas, no causalidad | mantener externo/adaptar a Research después |
| `orden_learning.sqlite3` | 196 KB | `learning_rule` 53; `run_event` 29; `strategy` 21; `strategy_trial` 17; `human_feedback` 0 | memoria metodológica sin aprendizaje validado | adaptar semántica, no copiar DB |

El `ia_web_system_v2.sqlite3` contiene cinco decisiones virtuales: `KEEP_CANONICAL` 3, `KEEP_DERIVATIVE` 270, `PRESERVE_ECOSYSTEM` 165, `QUARANTINE_COPY` 198 y `REVIEW_EXCEPTION` 272. Son etiquetas de dossier, no operaciones físicas. La simulación reporta 29 candidatos, 2.844.180 bytes potenciales y 0 bytes recuperados; la auditoría posterior enumera 58 candidatos históricos acumulados, por lo que los dos conteos no deben mezclarse.

El benchmark deja pasar integridad, cobertura de dossiers, cobertura de unidades, cero acciones y estabilidad del snapshot, pero falla `scope_alignment`: 65.855 no equivale a 1.439.409. La auditoría de deriva también deja `all_checks_pass=false` por `source_metadata_unchanged=false`. Esta combinación obliga a mantener el gate físico cerrado.

## Análisis del entorno Windows

`.catalog-env/pyvenv.cfg` declara Python 3.11.8 de `C:\Users\issvk\AppData\Local\Programs\Python\Python311`. `file` identifica `Scripts/python.exe`, `cv2.pyd` y `ctranslate2.dll` como PE de Windows x86-64. Entre los binarios grandes están `cv2.pyd` 86.3 MB, `ctranslate2.dll` 59.3 MB, FFmpeg/OpenCV 30.9 MB y ONNX Runtime 18.4 MB.

Conclusión de portabilidad: los scripts Python puros pueden ser portables con sus dependencias; el entorno no lo es. No se debe copiar `.catalog-env` a MAK ni asumir que sus wheels compilados funcionan en Debian. Para ONNX, OpenCV, PyAV o Playwright debe usarse una dependencia Linux explícita y reproducible, o clasificarse el candidato como externo.

`catalog_dashboard.py --help` terminó en código 1 porque intenta consultar `C:\` antes de mostrar ayuda. `ia_web_preview.py --help` terminó en código 1 por `ModuleNotFoundError: playwright`. Esto confirma límites concretos, no fallos generales del resto del sistema.

## Herramientas funcionales y relación con MAK

### Curatoria

MAK ya tiene una cadena real en `/home/mak/flujo/cultura/mak_curatoria/`: `ingesta_archivo.py` produce `archivo_index.sqlite`; `diagnostico_proyectos.py` agrupa proyectos y familias y emite `family_plan.jsonl` y `organism_plan.jsonl`; `triangular.py` convierte señales en preguntas verificables. Estas equivalencias son fuertes y hacen de Curatoria el owner primario del orden virtual.

La diferencia es contractual: DIMENSIONES DEL ORDEN usa `project_dossier`, `work_unit`, `order_virtual_index` y decisiones virtuales; Curatoria usa `assets`, `projects`, `families`, `family_coverage` y `mak-family-triangulation-plan-v1`. Debe crearse un adaptador tipado; no fusionar las SQLite por semejanza de columnas.

### Research

MAK Research ya separa discovery, captura, evidencia, claims, relaciones y productos. `source_pipeline.py`, `fondart_corpus.py`, `research_job_router.py` y `execute_research_job.py` son consumidores reales de esa semántica. DIMENSIONES DEL ORDEN aporta procedencia local, ideas candidatas y gaps. `funding_os_projection.py` encaja como radar externo, pero su reporte tiene 0 proyectos, 0 matches y 0 applications; no es un runtime de postulaciones.

### Cultura / MAK

`cultura/mak_plataforma/hub.py` es el owner de la interfaz agrupada en 8900 y ya distingue `research`, `portfolio`, `cultura`, oportunidades y contratos. Debe exponer el estado del puente como catálogo read-only o diagnóstico, no servir el árbol de 1.7 GB ni abrir una nueva base global.

### Portfolio

`tools/portfolio/catalog_contract.py` separa el catálogo público de proyectos de `iskvw/datos/obras.json`. Esto coincide con la regla de DIMENSIONES DEL ORDEN: un proyecto, un asset y una evidencia no se fusionan por nombre. Portfolio es consumidor secundario: solo recibe una relación explícita y revisada, nunca el catálogo completo ni un preview como obra.

## Propuesta de integración informacional

### Índice canónico propuesto

El índice de MAK debe ser una proyección pequeña y declarativa, no una copia de las bases:

```text
project_id
asset_id
family_id / work_unit_key
role: source | derivative | evidence | presentation | boundary
source_or_derived: original | derived | generated | external_evidence
provenance: physical_path + parent_snapshot + transform_chain
consumer: curatoria | research | cultura | portfolio
confidence: measured | high | medium | low | unknown
publico: true | false | review
status: candidate | reviewed | accepted | rejected | quarantine
```

El registro canónico debe enlazar por hash y path físico, conservar `source_hash_algo=sha256` cuando el hash exista, y registrar el alcance del snapshot. Las bases grandes quedan fuera; el repo guarda contrato, manifest, hashes seleccionados y proyecciones pequeñas.

### Semántica de relaciones

- **Ordenamiento:** `asset -> project -> family -> work_unit`; reduce superficie de revisión, no bytes.
- **Investigación:** `project/idea -> question -> source -> claim -> relation -> product`; una similitud es candidato, no causalidad.
- **Funding:** `project -> opportunity -> requirement -> evidence_gap -> candidate_match`; hard failures y términos desconocidos bloquean la promoción.
- **Curatoria:** `family -> representative -> branches -> review`; la salida es una pregunta o plan revisable.
- **Portfolio:** `project -> public_record -> asset`; solo se expone cuando `publico` y provenance están confirmados.

### Documentación mínima que debe leer un agente externo

1. `/home/mak/flujo/agents.md`.
2. `/home/mak/flujo/docs/MAK_CURRENT_STATE.md`.
3. `/home/mak/flujo/context/OWNER_MANIFEST.md`.
4. El contrato del consumidor (`mak_curatoria`, `mak_research`, `portfolio` o `mak_plataforma`).
5. Un packet acotado con `project_id`, input, output, dependencia, prueba y rollback.
6. La nota de procedencia de DIMENSIONES DEL ORDEN, sin abrir las bases pesadas salvo que el slice lo requiera.

Debe permanecer fuera del repo principal: el árbol fuente original, catálogos SQLite grandes, `.catalog-env`, `.git` anidado, cachés, previews, dashboards generados, credenciales y cualquier export que contenga material privado no necesario para el consumidor.

## Propuesta de integración de herramientas

La clasificación detallada por candidato está en `LUNA-571_DIMENSIONES_DEL_ORDEN_CROSSWALK.csv`. Reglas de síntesis:

- **Adoptar como conocimiento:** arquitectura, invariantes, taxonomía source/derived/evidence y contrato de decisión virtual.
- **Adaptar:** `ia_work_units.py`, `ia_automated_curator.py`, `ia_order_simulator.py`, `ia_project_origin.py`, `ia_system_audit.py`; todos deben leer una proyección y no modificar la fuente.
- **Envolver como CLI:** una futura `orden_bridge.py` en `cultura/mak_curatoria` con `--db`, `--scan-id`, `--out`, `--mode ro` y validación de schema.
- **Fusionar solo lógica, no bases:** partes de `ia_interface_analysis.py`, `ia_web_catalog.py` y `orden_learning.py` después de un contrato común y pruebas de consumidor.
- **Mantener externo:** SQLite grandes, visual boards, idea projection, Funding OS y toolchain Git hasta demostrar necesidad y consumer real.
- **Conservar como evidencia:** reportes, HTML, previews, hashes, snapshots y bases antiguas.
- **Cuarentenar:** `.catalog-env`, `.git`, `.pyc`, binarios Windows, DB scaffold vacía y temporales.

No recomiendo ejecutar `code-maat`, `repowise`, `code-forensics`, `git-filter-repo` ni `monorepo-split` en este slice. Code Maat requiere Java; Repowise escribe `.repowise/` en la raíz apuntada; los dos últimos son mutadores o herramientas de sincronización futura.

## Primer slice vertical único

### Puente read-only de familias para Curatoria

| Campo | Decisión |
|---|---|
| Herramienta | Adaptador futuro basado en `ia_work_units.py` + `ia_automated_curator.py`; nombre propuesto `orden_bridge.py` |
| Ubicación propuesta | `/home/mak/flujo/cultura/mak_curatoria/orden_bridge.py` |
| Owner | Curatoria, con contrato compartido de Cultura/MAK |
| Entrada | `/home/mak/curatoria_inbox/DIMENSIONES DEL ORDEN/ia_web_system_v2.sqlite3`, conexión URI `mode=ro`, `scan_id=1`; tablas mínimas `project`, `project_dossier`, `work_unit`, `work_unit_member`, `project_file` |
| Salida | Proyección pequeña `orden_family_plan.jsonl` fuera de la fuente, con registros `mak-family-triangulation-plan-v1`; no copiar SQLite ni paths completos innecesarios |
| Consumidor real | `/home/mak/flujo/cultura/mak_curatoria/diagnostico_proyectos.py` y la revisión humana de `family_plan.jsonl`/`organism_plan.jsonl` |
| Prueba mínima | importar el validador de `diagnostico_proyectos.py`; leer 908 dossiers, 24 unidades y 908 miembros en modo read-only; validar cada plan con `promotion=none`, branches obligatorias y evidencia de representative |
| Documentación mínima | README del bridge con semántica `source/derived/evidence`, mapping de columnas, alcance 65.855 vs 1.439.409, comandos y rollback |
| Criterio de aceptación | 0 escrituras en DIMENSIONES DEL ORDEN; 908/908 proyectos conservados; 24 unidades enlazadas; ningún plan sin evidencia; `PRAGMA integrity_check=ok`; Curatoria puede revisar una familia sin abrir cada ruta |
| Rollback | retirar solo el bridge y su proyección generada; dejar intacta la base externa; desactivar el consumidor sin migración ni limpieza física |

Este slice es único porque prueba entrada, transformación, salida y consumidor en una sola cadena. No incluye Research, Funding OS, Portfolio, previews ni acciones físicas. Si el contrato no valida una fila, se conserva como excepción y se cierra el slice sin promoción.

## Pruebas ejecutadas

### Comandos y códigos de salida

| Prueba | Comando resumido | Código | Resultado |
|---|---|---:|---|
| Inventario físico | `find . -xdev -type f -printf count`; `find . -xdev -type d -printf count` | 0 | 15.449 archivos; 1.190 directorios |
| Hashes | `sha256sum` sobre las fuentes seleccionadas fuera de `.git` y `.catalog-env` | 0 | hashes de fuentes seleccionadas observados |
| AST | `python3` con `ast.parse` y `compile` de los 29 `.py` | 0 | 29/29 parsean; no se creó `.pyc` |
| Imports aislados | `PYTHONDONTWRITEBYTECODE=1 python3 -c 'importlib.import_module(...)'` | 0 global; `ia_web_preview.py` 1 | módulos Python importan; preview falla por Playwright ausente |
| `--help` | `PYTHONDONTWRITEBYTECODE=1 timeout 12s python3 script.py --help` | 0 salvo dos | 27 de 29 scripts muestran ayuda; `catalog_dashboard.py` 1 por `C:\`; `ia_web_preview.py` 1 por Playwright |
| SQLite | script Python con URI `mode=ro`, `PRAGMA query_only=ON`, conteos y `integrity_check` | 0 | todas las DB auditadas: `ok`; ninguna mutación |
| JSON/HTML/CSV | `json.loads`, `HTMLParser`, `csv.reader` sobre árbol fuera de env/git | 0 | 30 JSON y 6 HTML válidos; 0 CSV en ese alcance |
| Binarios | `file` sobre `python.exe`, `.pyd`, `.dll`, SQLite | 0 | PE Windows confirmado; SQLite reconocido |
| Consumers | `grep -RInE` de nombres de familias en las rutas MAK acotadas | 1 | no hay consumidores directos de esos nombres |

No se ejecutaron mutadores, no se instaló ningún paquete, no se inició un servicio, no se usó SSH, no se usó el Git anidado como inventario, no se copiaron árboles y no se ejecutó `py_compile` porque habría creado `.pyc` dentro del write set prohibido. La validación AST ofrece el mismo gate de sintaxis sin modificar la fuente.

## Riesgos

| Riesgo | Evidencia | Mitigación |
|---|---|---|
| Cobertura incompleta | 65.855 vs 1.439.409 archivos; `scope_alignment=false` | declarar alcance en todo output y no inferir descarte |
| Deriva del snapshot | `all_checks_pass=false` por metadata drift | nuevo snapshot estable antes de cualquier decisión física |
| Derivados tratados como fuente | dashboards, previews y SQLite | `source_or_derived` obligatorio y provenance por transformación |
| Duplicación semántica | Curatoria y Orden tienen schemas parecidos | puente tipado, no merge de bases |
| Portabilidad | `.catalog-env` Windows; Playwright ausente | dependencias Linux explícitas o mantener externo |
| Falsa certeza de similitud | 20 familias exact clone y 165 scaffold ecosystem | similitud solo genera revisión, nunca borrado |
| Aprendizaje no demostrado | 17 trials, 0 reward real, 0 feedback humano | no promover `orden_learning` como ML cerrado |
| Historia Git desigual | algunos repos históricos sin profundidad suficiente | usar historia solo como señal de confianza |
| Coste operativo | 1.7 GB, 636 MB de catálogo y múltiples outputs | servir manifest/proyección pequeña, no DB completa |
| Privacidad/procedencia | paths Windows y posibles fuentes privadas | hash/path mínimo, nada de credenciales o uploads |

## Exclusiones

- No copiar la carpeta completa al repo MAK.
- No incorporar `catalog.sqlite3`, `ia_web_system_v2.sqlite3` ni sus WAL/SHM como datos versionados.
- No incorporar `.catalog-env` ni ningún binario Windows.
- No incorporar `.git` anidado, `.pyc`, caches, previews, HTML dashboards ni JSON de ejecución como runtime.
- No presentar `ia_web_report.json`, boards, PNG o bases como fuente original.
- No activar Code Maat, Repowise, code-forensics, git-filter-repo o monorepo-split en esta auditoría.
- No integrar Funding OS con postulaciones: el reporte no contiene proyectos, matches ni aplicaciones.
- No conectar todavía la proyección de ideas a Research: requiere calibración humana y confirmar el checkpoint ONNX.
- No asignar Portfolio como owner: no existe consumidor directo de DIMENSIONES DEL ORDEN allí.
- No modificar DIMENSIONES DEL ORDEN, MAK, bases, servicios ni Git.

## Siguiente acción concreta

Implementar, en una tarea separada y con write set propio, el puente `orden_bridge.py` para el slice de Curatoria. Antes de escribirlo, fijar el mapping exacto hacia `mak-family-triangulation-plan-v1`; después ejecutar una prueba read-only sobre `ia_web_system_v2.sqlite3` con salida pequeña y validación de 908 dossiers/24 unidades. Si el contrato falla o la evidencia es insuficiente, conservar la fila como excepción y rollback únicamente del bridge/proyección.

## Estado final de esta auditoría

- Entregables permitidos: este Markdown y `LUNA-571_DIMENSIONES_DEL_ORDEN_CROSSWALK.csv`.
- Mutadores sobre DIMENSIONES DEL ORDEN: ninguno; los cuatro hashes principales revalidados permanecen iguales. El recuento físico varió en dos archivos entre corridas y los acompañantes WAL/SHM se reportan como superficie volátil; no se hizo borrar, mover ni renombrar.
- Cambios en MAK fuera de los dos entregables: ninguno.
- Commit/push: no realizados.
