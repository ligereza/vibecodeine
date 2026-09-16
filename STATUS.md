# STATUS

Estado medido de LIBELULA, director de moscas.

Corte: 2026-09-15T23:30:16-03:00
Máquina: MAK, Linux
Método: `.venv/bin/python tools/mak_status.py`, `git`, `systemctl --user`, smoke HTTP y suites de cada autoridad.

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
| MAK / vibecodeine | `/home/mak` · `ligereza/vibecodeine` · `vibecodeine-legacy` | `main` · HEAD publicado | limpio y publicado; el trabajo no mergeable de snapshots queda preservado en el stash local de auditoría; upstream 0/0 |
| FLUJO | `/home/mak/flujo` · `ligereza/flujo` · `origin` | `main` · HEAD publicado | limpio y publicado; upstream 0/0 |
| XIO | `/home/mak/XIO` · `ligereza/XIO` · `origin` | `integration/xio-field-20260911` · `061bcec0` | limpio; upstream 0/0 |
| Histórico FLUJO dentro del padre | `/home/mak/flujo-vibecodeine-legacy-20260914` | `integration/flujo-canonical-20260911` | preservación histórica; no es fuente activa |

El directorio MAK está limpio y alineado con su remoto. Los snapshots de compatibilidad y el enlace externo permanecen físicamente disponibles; el material auditado que no era seguro mergear quedó preservado localmente, no publicado como runtime.

## Frontera física

- `/home/mak/flujo/src` y `/home/mak/XIO/xio` son las fuentes operativas.
- `/home/mak/src/flujo` y `/home/mak/xio` son snapshots de compatibilidad del repositorio MAK; no se ejecutan como autoridades paralelas.
- La comparación FLUJO registró 232 rutas comunes: 191 idénticas, 41 divergentes, 1 ruta solo en el padre y 5 solo en el checkout autónomo.
- La comparación XIO registró 160 rutas canónicas presentes en el padre: 143 idénticas y 17 divergentes. No se mezclan por copia automática.
- El inventario conserva 13 worktrees físicos: MAK, 11 worktrees efímeros de `.claude` y el worktree histórico de FLUJO. Se eliminó únicamente el puntero prunable sin directorio; no se eliminó trabajo de usuario.

## Contrato Portfolio → IRIS → Micelio → XIO

La cadena vigente es:

`medio explícito del autor` → `contrato_archivo` → `archivo.json` + `portafolio.json` → `Hub/Copilot` → `XIO por perfil`

- La autoría es el punto común declarado por el artista; IRIS no la adivina ni la redefine.
- La identidad de medio se deduplica solo por el identificador explícito. Título, carpeta, parecido visual o autor no reemplazan ese identificador.
- La evidencia Micelio se adjunta a la tarjeta visual/textual existente; no crea una segunda tarjeta ni un segundo grafo.
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

`data/rd.db` mide 3.035.136 bytes, 34 tablas de dominio, 8.040 filas de dominio y `pragma integrity_check = ok`. Las tablas no se fusionan por nombres parecidos: cada una conserva su dominio, procedencia y consumidor declarado.

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

| Autoridad | Comprobación | Resultado |
|---|---|---|
| MAK / IRIS | suite dirigida de contrato, Copilot, archivo, puente y UI | 240 casos aprobados · 2 omitidos |
| ISKVW visual | smoke de `campo`, `terminal`; manifiesto y publicación local | aprobado; 0 piezas omitidas |
| FLUJO venue 3D | `venue_geometria_scd.py --check`, visor y secuencia | aprobado; SCD DEMO 2D→3D, polilíneas declarativas; Gaussian splat fuera del runtime |
| ISKVW costo | `iskvw_piel_medir.mjs` contra snapshot reproducible | 2.812 segmentos máximos; bajo techo 6.000 |
| MAK / grammar | `tests/test_mak_grammar_runner.py` | 3 casos aprobados |
| FLUJO autónomo | `.venv/bin/python -m pytest -q -o addopts='' -m flujo` | 1.572 aprobados · 59 omitidos · 202 no seleccionados |
| XIO autónomo | `.venv/bin/python -m pytest -q` | 37 casos aprobados |
| XIO showcontrol | 10 scripts directos | 69 comprobaciones aprobadas |
| CLI/documentación | `gen_mapa_comandos.py --check` y gates de manifiesto/inventario | aprobado |
| MAK completo | `.venv/bin/python -m pytest -q` | exit 0; solo advertencias deprecadas de Pillow |

## Estado global medido

`.venv/bin/python tools/mak_status.py` devuelve:

`status=attention` · `attention=4` · `blocked=0` · `policy_status=candidate` · `policy_reason=holdout_gate_passed` · `projects_review_required=6`

Es una señal de la política de aprendizaje y evidencia del sistema completo; no cambia las autoridades Git ni abre una segunda implementación de MAK, FLUJO o XIO.

## Decisiones cerradas

1. Una autoridad operativa por repositorio: `/home/mak`, `/home/mak/flujo` y `/home/mak/XIO`.
2. Los snapshots del padre quedan solo como compatibilidad; no se les agrega runtime nuevo.
3. RD e ISKVW/FOH son perfiles, no ramas.
4. El portafolio usa identidad explícita del medio y conserva evidencia semántica sin duplicar tarjetas.
5. El Hub mantiene una sola cara TCP en 8900; Research y Codex se conectan por Unix.
6. `grammar` es MAK-local con un único entrypoint y una única prueba de propiedad.
7. El deep learning actual es evidencia por canales; la fusión entrenada no se presenta como disponible.
