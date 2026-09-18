# STATUS

Estado medido de LIBELULA, director de moscas.

Corte: 2026-09-18T00:10:00-03:00
Máquina: MAK, Linux
Método: `.venv/bin/python tools/mak_status.py`, `tools/repo_audit.py`, `tools/gen_mapa_comandos.py --check`, `tools/test_lane_map.py`, `git`, `systemctl --user`, `ss`, smoke HTTP. Las suites completas de FLUJO y XIO no se re-corrieron en este corte (quedan marcadas como no re-medidas más abajo); la suite dirigida de MAK (`-m mak`) se intentó con tope de 180s y no alcanzó a imprimir un resultado antes de agotar el tiempo, así que tampoco se re-mide aquí.

Contexto mecánico para agentes: `tools/contexto_repo.py --json --root <checkout> [--query "texto"]` produce `mak-repo-context-v1` con Git + AST Python + consumidores estáticos; no escribe archivos.

Este archivo es una fotografía verificable del sistema. No es handoff, README ni bitácora: registra el estado y las decisiones vigentes, sin convertirlas en una lista de tareas.

## Resultado del corte

La integración de MAK, FLUJO y XIO queda cerrada por frontera física y contrato:

- MAK conserva la estación, el Hub y el portafolio/IRIS.
- FLUJO tiene un único checkout operativo autónomo.
- XIO tiene un único checkout operativo autónomo.
- RD e ISKVW/FOH son perfiles de consumo e integración; no son ramas.
- El Hub público usa `127.0.0.1:8900`; Research y Codex viven detrás de sockets Unix privados.
- El experimento `grammar` pertenece a MAK y ya no aparece como capacidad del CLI de FLUJO.
- El circuito visual de ISKVW tiene un formato único de portafolio; las pieles
  se pueden cambiar conservando la lectura actual.

## Autoridades Git

| Superficie | Checkout y remoto | Rama / HEAD | Estado medido |
|---|---|---|---|
| MAK / vibecodeine | `/home/mak` · `ligereza/vibecodeine` · `vibecodeine-legacy` | `rd/forense-y-vocabulario` · `d0126f92` publicado (2026-09-17) | sin cambios trackeados sucios; upstream 0/0; dos directorios sin trackear nuevos, ver abajo |
| FLUJO | `/home/mak/flujo` · `ligereza/flujo` · `origin` | `rd/ensayos-parallel-sets` · `06745df` publicado (2026-09-16) | limpio y publicado; upstream 0/0 |
| XIO | `/home/mak/XIO` · `ligereza/XIO` · `origin` | `integration/xio-field-20260911` · `d9d4c4b` publicado (2026-09-17) | limpio y publicado; upstream 0/0 |
| Histórico FLUJO dentro del padre | `/home/mak/flujo-vibecodeine-legacy-20260914` | `integration/flujo-canonical-20260911` | preservación histórica; no es fuente activa |

Las tres autoridades avanzaron a ramas de trabajo distintas de `main` desde el
corte anterior (2026-09-16T03:00); las tres siguen publicadas y sin
divergencia (`0/0`) frente a su remoto. Dos directorios nuevos sin trackear
aparecieron en `/home/mak` desde entonces: `mak/` (contiene `state/mak.db`,
propósito propio, no es RD) y `pastillas/` (repositorio Git independiente con
su propio dataset/modelos/src, sin relación declarada con VIBECODEINE). Ninguno
se tocó ni se clasificó como autoridad.

Este corte además deduplicó el árbol físico de copias de `rd.db`/`rd_datos.db`
repartidas fuera de las tres autoridades (worktrees, jobs, workspaces): 5
archivos vacíos borrados, 9 copias divergentes/superadas archivadas en
`/home/mak/_dedup_rd_20260917/` sin borrarlas, y 19 copias idénticas dentro de
worktrees convertidas a hardlinks. El canónico activo (`/home/mak/data/rd.db`)
y el linaje con capa de campo XIO (`work/respaldo-campo-xio-20260916/rd.db`,
pendiente de decisión `XIO_LAYER`) no se tocaron.

## Frontera física

- `/home/mak/flujo/src` es la fuente operativa de FLUJO. El host XIO se
  ejecuta desde `/home/mak/XIO/xio/new/server.py`; su motor de plugins vive
  en `xio/new/plugins` y la biblioteca desplegada en `xio/new-plugins`.
  `xio/actual` es histórico.
- `/home/mak/src/flujo` y `/home/mak/xio` son snapshots de compatibilidad del repositorio MAK; no se ejecutan como autoridades paralelas.
- La comparación FLUJO registró 232 rutas comunes: 191 idénticas, 41 divergentes, 1 ruta solo en el padre y 5 solo en el checkout autónomo.
- La comparación XIO registró 160 rutas canónicas presentes en el padre: 143 idénticas y 17 divergentes. No se mezclan por copia automática.
- El inventario conserva 13 worktrees físicos: MAK, 11 worktrees efímeros de `.claude` y el worktree histórico de FLUJO. Se eliminó únicamente el puntero prunable sin directorio; no se eliminó trabajo de usuario.

## Proyección del portafolio hacia superficies externas

La cadena vigente es:

`medio explícito del autor` → `contrato_archivo` → `archivo.json` + `portafolio.json` → `Hub/Copilot` → `XIO por perfil`

- La autoría es el punto común declarado por el artista; IRIS no la adivina ni la redefine.
- La identidad de medio se deduplica solo por el identificador explícito. Título, carpeta, parecido visual o autor no reemplazan ese identificador.
- La evidencia Micelio se adjunta a la tarjeta visual/textual existente; no crea una segunda tarjeta ni un segundo grafo.
- XIO no es el portafolio ni IRIS: solo consume proyecciones explícitas en sus perfiles RD o FOH cuando corresponde.
- MobileCLIP visual, Nomic/Micelio semántico y GTM estructural permanecen como canales de evidencia distinguibles. No se afirma una fusión entrenada que todavía no existe.
- RD y FOH/ISKVW usan contratos, `eventRef`/`eventKey` y consumidores; no ramas Git duplicadas.
- `iskvw.cl` público y el Hub IRIS interno son superficies distintas, conectadas por el archivo/contrato y no por una falsa identidad de servicio.

## Formato visual ISKVW

- `tools/gen_archivo_iskvw.py` genera `archivo.json` y su manifiesto compañero
  `portafolio.json` en una sola operación; ambos son artefactos regenerables y
  no versionados.
- El manifiesto contiene todos los ids de la proyección: 1.830 piezas, 219 con
  posición medida y 1.611 ubicadas de forma estable mientras no exista esa
  medición. `omitted_count=0`; ausencia de decisión o metadata no bloquea la
  creación del portafolio.
- `iskvw/piel/lib/skin_runtime.js` es el único runtime común de selector y de
  carga/orden del portafolio. `campo` y `terminal` consumen la misma proyección;
  el selector conserva query y hash. El visor SCD no es una piel: vive en
  FLUJO, bajo `tools/venue3d/`, y consume su registro técnico propio.
- El workflow de Pages verifica el hash de `archivo.json`, conteo, unicidad,
  cobertura completa y las dos pieles de portafolio antes de publicar.

## Archivo RD y deduplicación

Artefacto local medido: `iskvw/datos/archivo.json` regenerado con el grafo vivo
de MAK en el corte. La línea reproducible de CI, cuando no puede alcanzar el
Hub, usa el snapshot versionado y queda fijada por el medidor.

| Medición | Valor |
|---|---:|
| versión / fuente | 1 / todo |
| piezas | 1.830 |
| vínculos | 5.832 |
| clases | 1.607 obra · 223 código |
| vínculos por clase | 5.814 semánticos · 18 etiquetas |
| registros con evidencia Micelio | 219 |
| IDs duplicados | 0 |
| vínculos con endpoint inválido | 0 |
| auto-vínculos | 0 |
| vínculos duplicados | 0 |

Re-medido el 2026-09-17 con `tools/repo_audit.py`: `data/rd.db` tiene ahora 34
tablas de dominio y 8.040 filas (`integrity=ok`), dos tablas menos que el corte
anterior (36) — las dos tablas vacías del puente XIO (`xio_eventos`,
`xio_signal_events`) ya no están; el conteo de filas no cambió, así que la
diferencia es de esquema, no de datos perdidos. `data/mak_knowledge.db` mide 48
tablas y 407.133 filas (`integrity=ok`), subiendo desde 387.104 el 2026-08-28.
`data/flujo.db` sigue congelado en 1 tabla / 6 filas. Las tablas no se fusionan
por nombres parecidos: cada una conserva su dominio, procedencia y consumidor
declarado.

## Runtime consolidado

| Servicio | Autoridad | Estado / dirección |
|---|---|---|
| MAK Hub | `cultura/mak_plataforma/hub.py` | activo · TCP `127.0.0.1:8900` |
| Research | `cultura/mak_research/interfaz.py` | activo · Unix `/home/mak/.cache/mak/research.sock` |
| Codex | `cultura/mak_codex/interfaz_codex.py` | activo · Unix `/home/mak/.cache/mak/codex.sock` |
| Ollama | proveedor local | TCP `127.0.0.1:11434` |
| SearXNG | buscador local | TCP `127.0.0.1:8888` |

Smoke posterior al reinicio del Hub:

- `/health` → HTTP 200.
- `/api/archivo` → HTTP 200; fuente Micelio viva: 579 piezas y 1.286 vínculos.
- `/api/portfolio/copilot/suggestions?item_id=18089566880572882.jpg` → HTTP 200; 24 sugerencias, 24 grupos, 4 relaciones Micelio.
- `/api/portfolio/copilot/scene?item_id=18089566880572882.jpg` → HTTP 200; canal semántico Micelio disponible con 4 relaciones.

El 404 sin `item_id` es la respuesta de validación de un elemento inexistente, no una ruta rota; con un medio real ambas rutas responden 200.

## Experimento grammar

- Propietario: MAK.
- Implementación: `cultura/mak_research/grammar.py`.
- Entrada única: `tools/grammar_runner.py`.
- Corpus: `/home/mak/work/grammar-lab-20260912/corpus_manifest.json`.
- El módulo valida `semantic-icons-v1`, infiere la biblioteca desde `construction`, congela la biblioteca antes de evaluar las demás particiones y despacha por el Conductor de MAK.
- La prueba de checkpoint, composición y reanudación pasa en 3 casos.
- FLUJO no importa el módulo, no expone el subcomando y no recibe una copia funcional del runner.

## Validación por autoridad

Las filas marcadas **(2026-09-16, no re-medida)** son las que este corte no
volvió a correr; se conservan como último valor conocido, no como resultado de
hoy. Repetir la medición antes de citarlas como estado actual.

| Autoridad | Comprobación | Resultado |
|---|---|---|
| MAK / IRIS | suite dirigida de contrato, Copilot, archivo, puente y UI | 240 aprobados · 2 omitidos (2026-09-16, no re-medida) |
| ISKVW visual | smoke de `campo`, `terminal`; manifiesto y publicación local | aprobado; 0 piezas omitidas (2026-09-16, no re-medida) |
| FLUJO venue 3D | `venue_geometria_scd.py --check`, visor y secuencia | aprobado; SCD DEMO 2D→3D (2026-09-16, no re-medida) |
| ISKVW costo | `iskvw_piel_medir.mjs` contra snapshot reproducible | 2.812 segmentos; bajo techo 6.000 (2026-09-16, no re-medida) |
| MAK / grammar | `tests/test_mak_grammar_runner.py` | 3 casos aprobados (2026-09-16, no re-medida) |
| FLUJO autónomo | `.venv/bin/python -m pytest -q -o addopts='' -m flujo` | 1.572 aprobados · 59 omitidos · 202 no seleccionados (2026-09-16, no re-medida) |
| XIO autónomo | `.venv/bin/python -m pytest -q` | 37 casos aprobados (2026-09-16, no re-medida) |
| XIO showcontrol | 10 scripts directos | 69 comprobaciones aprobadas (2026-09-16, no re-medida) |
| CLI/documentación | `gen_mapa_comandos.py --check` | **aprobado, re-medido 2026-09-17**: `MAPA.md y context/comandos.json al dia con el CLI` |
| Contrato de lanes | `tools/test_lane_map.py --format text` | **re-medido 2026-09-17**: `contract_disagreements=0` pero `not_covered=tests/test_portfolio_iris_context_dispatch.py` — invariante rota, ver hallazgo abajo |
| MAK completo | `.venv/bin/python -m pytest -q` | exit 0; solo advertencias deprecadas de Pillow (2026-09-16, no re-medida; el intento de re-correr `-m mak` el 2026-09-17 no terminó dentro de 180s) |

### Hallazgo abierto: contrato de lanes desincronizado

`tests/test_portfolio_iris_context_dispatch.py` se agregó el 2026-09-14 con
`pytest.mark.mak`, pero `context/test_lane_map.json` se regeneró por última vez
el 2026-09-15 sin incluirlo — hoy aparece como `not_covered`, violando la
invariante que `CAPACIDADES_MAK.md` exige (`not_covered=` vacío). No se corrigió
con `--write` en este corte: el propio `test_lane_map.py --help` advierte que
esa bandera sobrescribe el schema de asignaciones por-test con el schema más
grueso de resumen por lane, rompiendo `_load_lane_contract()`. Corregirlo
requiere una edición manual del JSON que preserve su schema, no una
regeneración automática.

### Hallazgo abierto: dos vocabularios de dominio sin reconciliar

`cultura/mak_plataforma/tandas.py:191` define `AREAS` (claves como
`mak_quality`, `rd_evidence`, cada una con `purpose`/`default_paths`/
`evidence_paths`/`actions` — es la agenda de tandas para un agente) y
`cultura/mak_plataforma/ledger.py:23` define por separado
`DOMAINS = ("rd", "iskvw", "portfolio", "mak", "svg", "adobe", "repo",
"opportunities")` — el vocabulario de dominio del ledger. Nombran el mismo
concepto (a qué área/dominio pertenece un dato o una accion) con dos
listas independientes que no se referencian entre sí. Un intento de
consolidar referencias en `tandas.py` hacia sucesores reales
(`arqueologia.py`→`inferential_archaeology.py`,
`esfuerzo.py`→`compute_effort_residuals.py`) se revirtió en este ciclo
porque tocaba `AREAS` sin resolver primero esta duplicación de
vocabulario; queda sin decidir si `AREAS` debe expresarse en términos de
`DOMAINS` o si son legítimamente conceptos distintos (tandas de agente vs.
dominio de dato).

## Estado global medido

`.venv/bin/python tools/mak_status.py` devuelve:

`status=attention` · `attention=4` · `blocked=0` · `policy_status=candidate` · `policy_reason=holdout_gate_passed` · `projects_review_required=6`

Es una señal de la política de aprendizaje y evidencia del sistema completo; no cambia las autoridades Git ni abre una segunda implementación de MAK, FLUJO o XIO.

## Integración Azure y calibración DeepSeek

Servicios reales creados y verificados vía `az` CLI (cuenta de estudiante,
free/basic tier): `makmak-search` (AI Search Free, índice único
`mak-tools-v1` por el límite de 3 índices del tier gratis, más `mak-rd-v1`
y `mak-inbox-v1`), `makmak-ml-workspace`, `makmakmlstorage`,
`makmak-ml-kv`, `makmak-ml-insights`, `makmak-cpu-cluster`
(`min_instances=0`), `makmakmlregistry` (único costo recurrente, ~5 USD/mes).
`tools/consultar_mak_search.py` es el consumidor real y verificado del
índice de herramientas.

DeepSeek (deployment ISSVKK) se usó como "conejillo de indias" para generar
tests reales sobre funciones puras sin cobertura previa, siempre con hechos
completos entregados explícitamente y siempre ejecutados antes de aceptarse
— nunca se guardó un test generado sin correrlo primero. Áreas cubiertas
este ciclo: RD (`_norm_link_value`/`_venue_link_key`), curatoria
(`triangular.py`, escrito directamente por el agente porque el archivo está
excluido de delegación), plataforma (`_aplanar_llmcalls`, `_extraer_json`),
research (`_compact_search_query`), codex (`algebra.py:distancia`), XIO
(`test_cueengine_validators.py`, reescrito por el agente al formato real del
proyecto), WACHUMA (`plant-descriptor.test.ts`, primera prueba TypeScript
delegada), FLUJO (`venue_geometria_puntos.py`), ISKVW (`_riqueza`),
curatoria (`diagnostico_proyectos.py`) y research/opportunity_radar
(`mak_vigia.py:_titulo_util`/`plegar`).

Calibración real registrada en `data/mak_knowledge.db`
(`learning_evaluations`, `target_kind=azure_delegation_pattern`) y
publicada en MLflow (`makmak-ml-workspace`, experimento
`mak-azure-integration`) vía `tools/reportar_calibracion_deepseek.py`:
**10 aciertos, 4 fallos, 14 casos evaluados, accuracy=0.714**. Los 4
fallos reales quedan en la propia base: errores de redondeo no
considerados, framework de test equivocado, aserciones falsas sobre
dedup case-insensitive y mal juicio de un límite de bucle — cada uno
corregido a mano tras ejecutar y ver el `AssertionError` real, nunca
aceptado a ciegas.

Regla sostenida sin excepción en todo el ciclo: ningún contenido de RD ni
de curatoria se envió a Azure — solo código/arquitectura pura, y el
clasificador de modo automático de la plataforma bloqueó varios intentos
de subir contenido adyacente a RD/curatoria ("Data Exfiltration"); esos
bloqueos se respetaron siempre, sin reintentar con otro ángulo ni delegar
la misma acción a DeepSeek como bypass.

Dos directorios nuevos sin trackear en `/home/mak` (`mak/`, `pastillas/`,
`.docker/`) no se tocaron ni se clasificaron: no tienen relación declarada
con este ciclo de trabajo y no se agregaron al commit.

## Decisiones cerradas

1. Una autoridad operativa por repositorio: `/home/mak`, `/home/mak/flujo` y `/home/mak/XIO`.
2. Los snapshots del padre quedan solo como compatibilidad; no se les agrega runtime nuevo.
3. RD e ISKVW/FOH son perfiles, no ramas.
4. El portafolio usa identidad explícita del medio y conserva evidencia semántica sin duplicar tarjetas.
5. El Hub mantiene una sola cara TCP en 8900; Research y Codex se conectan por Unix.
6. `grammar` es MAK-local con un único entrypoint y una única prueba de propiedad.
7. El deep learning actual es evidencia por canales; la fusión entrenada no se presenta como disponible.
