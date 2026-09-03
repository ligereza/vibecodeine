# CAPACIDADES.md

> Current entry point: read `agents.md`, `docs/MAK_CURRENT_STATE.md` and
> `context/LAST_HANDOFF.md` first. The current-state document is the compact
> synthesis of the historical phase work; this file is a capability index.
>
> **Cómo se escribe una fila aquí** (regla del 2026-08-28, ver
> `docs/AUTORIDAD.md`): toda referencia a un archivo lleva su ruta desde la raíz
> del repo, y todo estado (`VIVO`, `activo`, `integridad OK`) declara al lado
> cómo se comprobó. Medido el 2026-08-28, este documento tenía 253 referencias a
> archivos de las cuales **143 eran nombres pelados sin ruta** y 116 estados en
> prosa sin método. Por eso la auditoría de `auditar_capacidades_mak` terminó
> apuntando a números de línea de este archivo, y por eso su lista de candidatos
> a retiro ya no resuelve. No es un problema de contenido: es de direccionamiento.
> This inventory describes reusable machinery; it is not a task queue.

Inventario de arranque rapido. Objetivo: empezar un proyecto nuevo (dentro o
fuera de este repo) sin tener que leer/buscar por todo `flujo`. Verificado
contra el repo real; the capability and database baseline was refreshed on
2026-08-27 (commands executed, not memory). If something
de aca no calza con lo que ves, el repo cambio despues -- confia en el repo,
no en este doc, y actualizalo en el mismo PR que lo detecte.

## 0. Distributed system authority (physical scope measured 2026-08-27)

This repository is the authoring projection of a distributed organism. The
complete physical scope outside `WIN` is now measured in
`docs/system_learning/master/inventory.json:physical_organism_registry`; the
repo remains the source of versioned contracts, tests and documentation, not a
reason to pretend that external runtimes are inside Git. The measured
authority order is:

1. Windows and MAK Linux local surfaces: files, databases, memories, mounts,
   services, and generated outputs determine what physically exists.
2. The transversal catalog at
   `/home/mak/indexes/mak-reality-20260813/full-organism/` indexes those
   surfaces by path, hash, provenance, owner, status, and transport
   eligibility. It stores references; it does not merge sovereign data.
3. Git `main` is a reviewed reproducibility and publication checkpoint. Git
   history is transport evidence, not runtime authority.

The sovereign organisms are MAK (computational producer and curator), RD /
Reduciendo Dano (NGO), and Portfolio / ISKVW (artist archive). Windows and
MAK Linux are physical nodes; either node may host material belonging to any
organism. For every result keep producer, owner, subject domain, final
authority, evidence, status, visibility, and destination independent.

The target is one logical knowledge database with bounded schemas: `core`
(identity/context/provenance), `mak` (operations/research/curation), `rd`
(scientific/field/safety), `portfolio` (works/records/authorial curation),
`relations` (typed cross-domain links), `products` (publication projections),
and `audit`. Assertions and relationships carry source/evidence, producer,
owner, confidence/status, visibility, and timestamp/version. Raw and binary
material stays on Windows, MAK, or mounted storage; the database stores URI
and hash. RD and Portfolio remain sovereign organisms and gates even though
their knowledge may share this logical database.

Current physical state is not yet that target. The Windows enriched RD SQLite
is a read-only `CANDIDATE_AUTHORITY` migration input; the MAK reduced RD
SQLite is a read-only `LEGACY_PROJECTION`. Neither is an established logical
system of record. Portfolio DB remains `NOT_CONFIGURED` as a separate DB
because Portfolio is a target schema, not an independent database. Local
SQLite files are migration inputs, caches, or projections; bidirectional
writes are prohibited. The intended end state has one primary writer and an
explicit versioned sync direction. Search and vector indexes are derived and
rebuildable, not truth.

Runtime memory and mounted/private state stay on their owning physical node;
credentials, `.env`, private exports, and runtime memory are not eligible for
Git transport. A transport manifest with source, hash, physical node,
organism owner, database/memory authority, Git eligibility, and promotion gate
is required before any selected material is projected into Git. There is no
mass folder migration implied by this architecture.

### Reconciliación física de bases — 2026-08-27

El registro completo está en
`docs/system_learning/master/inventory.json:physical_organism_registry` y su
catálogo de bases en `database_registry`. La regla
operativa es una autoridad por dominio y conexiones por contratos, hashes y
refs; “consolidar” no significa copiar tablas ni borrar snapshots.

**Metodo de medicion** (regla del 2026-08-28: todo estado declara como se
comprobo): la autoridad es `tools/repo_audit.py`, que corre en `ci.yml`. Cuenta
tablas con `select name from sqlite_master where type='table' and name not like
'sqlite_%'` -- o sea **excluye las tablas internas de SQLite** -- suma `count(*)`
por tabla y cierra con `pragma integrity_check`. Reproducir:
`.venv/bin/python tools/repo_audit.py`.

Este metodo importa. Una primera correccion de esta tabla, el 2026-08-28, conto
`sqlite_sequence` y reporto 49 tablas y 387.108 filas para `mak_knowledge.db`;
`repo_audit.py` dice 48 y 387.104. La diferencia es exactamente esa tabla
interna y sus 4 filas. Dos mediciones honestas del mismo archivo dan numeros
distintos si no declaran su metodo, y entonces ninguna se puede verificar.

| Superficie | Autoridad/uso | Medido por `tools/repo_audit.py` el 2026-08-28 |
|---|---|---|
| `data/mak_knowledge.db` | memoria MAK, Project IR, contexto, episodios y aprendizaje | activa, 48 tablas, 387.104 filas, integridad OK |
| `data/rd.db` | proyeccion regenerable del catalogo RD | activa, 20 tablas, 7.585 filas, integridad OK |
| `data/rd_datos.db` | frontera privada de datos de campo RD | activa, 3 tablas, 0 filas, integridad OK |
| `data/flujo.db` | indice operativo de flyers | activa, 1 tabla, 6 filas, integridad OK; congelada el 2026-06-30 y con rutas `C:\IA\flujo\`. Consumida por `tools/repo_audit.py` (CI) y `tests/test_portfolio_gen.py`, asi que no se retira |
| `experiments/pilots/ARICA-FONDART-2027/source_corpus/sources.sqlite` | evidencia acotada por piloto | presente, alcance de caso |
| `experiments/pilots/DREFQUILA/runs/cross-archive-escarlata-20260826/research-capture/sources.sqlite` | evidencia acotada por piloto | presente, alcance de caso |
| `out/archaeology/claude-codex-mak-20260815.sqlite` | arqueologia historica de sesiones/repositorio | evidencia historica, no runtime |

### Las otras cuatro filas viven fuera del repo, en `/home/mak/`

Estas cuatro superficies **existen y estaban bien medidas**. Lo unico que les
faltaba era la raiz: se citaban en relativo, y en relativo desde `flujo/` no
resuelven. Reverificadas el 2026-08-28 con el metodo de CI:

| Superficie | Lo que afirmaba | Medicion 2026-08-28 |
|---|---|---|
| `/home/mak/research/jardines_interpretativos/jardines_interpretativos.sqlite` | "activo, 23 tablas, 276 filas, integridad OK" | **exacto: 23 tablas, 276 filas, integridad OK** |
| `/home/mak/research/corpus/**/sources.sqlite` | "14 snapshots, todos integros" | **12 snapshots** (unica deriva real de esta tabla) |
| `/home/mak/research/intake/**/intake.sqlite` | "2 snapshots, uno vacio y uno poblado" | **exacto: 2** |
| `/home/mak/labs/**/archivo_index.sqlite` | "6 snapshots integros, no runtime unico" | **exacto: 6**, en 7 directorios de laboratorio |

**Correccion de una correccion.** Una primera pasada de esta sesion declaro que
`research/` y `labs/` "no existen" y retiro las cuatro filas. Era falso: se
busco solo dentro de `/home/mak/flujo` y estos arboles cuelgan de `/home/mak`.
`agents.md` advierte exactamente contra ese error -- *"The absence of a file in
`/home/mak/flujo` does not prove that it is absent from MAK"* -- y la pasada lo
cometio igual.

El defecto real no era la ausencia sino **la raiz ambigua**: una ruta relativa
en un documento que vive en `flujo/` se lee como relativa a `flujo/`. Por eso
las cuatro filas de arriba llevan ahora ruta absoluta desde `/home/mak`.

MAK es la maquina, no el repositorio. `/home/mak/flujo` es la base de autoria
dentro del organismo `/home/mak`; `research/`, `labs/`, `curatoria/`,
`plataforma/` y `WIN/` son superficies hermanas, no ausencias.

La fila que sobrevivio con cifra corregida: `mak_knowledge.db` decia 35 tablas y
387.089 filas; `repo_audit.py` mide 48 y 387.104. `rd_datos.db` decia 3 tablas y
3 es correcto por el metodo de CI.

Todas las rutas anteriores tienen hash SHA-256 y conexiones declaradas en el
master. La medicion completa fuera de `WIN` encontro 270 archivos con
extensiones SQLite: 85 pertenecen a superficies MAK y 185 son caches del
host/aplicaciones. Los 85 pasaron `integrity_check`; los 185 estan registrados
como contexto fisico, pero no son memoria MAK ni fuente semantica.

La clasificacion completa y reproducible es:

| Clase fisica | Archivos | Regla |
|---|---:|---|
| memoria, Research, labs, indices, pilotos, Curatoria y outputs | 46 | stores de dominio o snapshots; autoridad declarada por ruta |
| arqueologia, runner, agentes y caches de crawler | 39 | evidencia/soporte no autoritativo; no se fusionan con MAK memory |
| cache host/aplicaciones | 185 | detectados, excluidos del conocimiento MAK |

No hay una "base duplicada" que deba eliminarse: los nombres parecidos
representan snapshots, privacidad, dominios, replicas u outputs distintos.
`WIN`, media, artwork, credenciales y bases no listadas no se tocan
automaticamente. El inventario usa `/home/mak` como raiz, excluye
`/home/mak/WIN` y no recorre los montajes `GoogleDrive`/`OneDrive`.

### Organismo fisico MAK fuera de WIN -- 2026-08-27

La autoridad operativa no termina en `flujo`. El registro maestro enumera las
114 entradas de primer nivel y las clasifica sin moverlas:

| Superficie | Funcion | Estado |
|---|---|---|
| `flujo` | autoria, contratos, tests, docs, CLI | baseline activo |
| `plataforma` | runtime proyectado del Hub | proceso observado |
| `research`, `vigia` | corpus, jobs, capturas, vigencia y triangulacion | activos |
| `curatoria`, `curatoria_inbox`, `RD` | organos, inputs artisticos y fuente RD | protegidos/separados |
| `portfolio_media`, `indexes` | media y catalogos transversales | referencias derivadas |
| `labs`, `experiments`, `state`, `out` | pruebas, pilotos, arqueologia | no autoritativos |
| `actions-runner`, `tools`, `src`, `apps` | transporte y herramientas auxiliares | fuera de autoridad de producto |
| `models`, `model-config`, `blender*` | proveedores y runtimes creativos | capacidad condicionada |
| `xio_puente`, `n8n-local`, `searxng` | puentes/runtimes especificos | aislados; no core |

Runtimes observados (medición 2026-09-02): Hub `127.0.0.1:8900`, Research `127.0.0.1:8890`, Codex
`127.0.0.1:8891`, Ollama `127.0.0.1:11434`, Open WebUI `:8080` y el runner de
Actions. La escucha prueba presencia del proceso, no salud del servicio,
capacidad del proveedor ni validez de sus datos. `GoogleDrive` y `OneDrive`
son montajes externos no escaneados; `WIN` es historico protegido y queda
fuera de este mapa.

## 1. Mapa index del repo

CLI real (`py -m flujo --help`, v0.56.1), comandos principales:

- `app` / `serve` -- hub local (workspace pro). `hub` -- servidor + index/route del arbol de material ($FLUJO_RD_ROOT).
- `job`, `brief`, `intake` -- gestion de jobs y briefs (JSON 1.0).
- `cotizaciones`, `plano` -- cotizacion dual y plano SVG/rider/costos de stands.
- `suplementos` -- contraportadas RD (`svg/suplementos_rd/`).
- `rd-db`, `rd-datos` -- DB consultable RD (reactivos/packs/productoras/venues) + ingesta privacy-first.
- `eventos` -- automatizaciones. The active event path uses the MAK/Linux
  workflow and `render_*_mak.py`; the historical `flyer-auto` command remains
  available as legacy/manual-only compatibility.
- `resolume` -- automatizacion de shows Resolume/Chataigne por SMPTE/OSC (`.noisette`, schema validado contra fixtures reales).
- `laser` -- estetica vectorial para laser/plotter via vpype (externo, opcional): `hatched` (relleno->rayado), `flow` (imagen->campo de flujo, semilla determinista), `lote` (carpeta de material -> svgs + manifiesto que entra al archivo iskvw). Presupuesto de puntos 600-1000/frame integrado; restricciones duras y rig del usuario en `docs/laser/TOOLKIT_INDICE.md`.
- `render`, `analyze`, `export` -- render/validacion de piezas vectoriales, analisis de color/OCR, export ZIP.
- `tapiz` -- pipeline generativo Tapiz<->Psicosis<->Fungi (`tools/compete_engine.py`).
- `datadrop`, `index`, `flyer-import`, `flyer-list`, `ig-redownload` -- ingesta y catalogo de material real.
- `daily`, `handoff`, `portal`, `doctor`, `health`, `verify`, `version` -- operacion y diagnostico del repo.
- `github-sync` -- sync simple con GitHub. (`airdrop` se retiro el 2026-08-28; la cadena estaba muerta desde el 2026-08-14, ver `docs/SCRIPTS_INVENTORY.md`.)
- `delegate`, `ai-prompt`, `privacy`, `knowledge`, `package`, `init`, `clean`, `brand` (legacy) -- utilidades de soporte.

### 1-bis. Hubs y servicios del organismo (medición operativa 2026-09-02)

Esta tabla separa la capacidad declarada del estado vivo. El puerto y el
listener se vuelven a comprobar en `docs/MAK_CURRENT_STATE.md` o mediante
`GET /api/status`; no se debe interpretar una fila histórica como un proceso
activo.

| Superficie | Fuente canónica / unidad | Entrada y puerto | Alcance y estado observado |
|---|---|---|---|
| MAK Hub | `cultura/mak_plataforma/hub.py` / `/home/mak/.config/systemd/user/mak-hub.service` | `127.0.0.1:8900`; `GET /health` y `GET /api/status` | Interfaz agrupada de MAK, Portfolio/ISKVW, departamentos y Copilot; listener activo, HTTP 200 |
| FLUJO App | `src/flujo/web/hub.py`; `python -m flujo app` | Default `8765`; auto-puerto observado `8766` el 2026-09-02 | Workspace portátil/manual; no es un servicio permanente ni el Hub MAK |
| FLUJO `serve` | `src/flujo/serve/server.py`; `python -m flujo serve` | Default `8777`; no escuchaba en la medición | Servidor liviano/legado; su parser no sustituye al backend completo de `flujo app` |
| Research | `cultura/mak_research/interfaz.py` / `/home/mak/.config/systemd/user/mak-research.service` | `127.0.0.1:8890` | Servicio interno de Research para el Hub; listener y proceso activos |
| Codex bridge | `cultura/mak_codex/interfaz_codex.py` / `/home/mak/.config/systemd/user/mak-codex.service` | `127.0.0.1:8891` | Puente interno de Codex para MAK; listener y proceso activos |
| Copilot curatorial | `cultura/mak_plataforma/copilot.py`; consumido por `hub.py` | Endpoints bajo `:8900/api/portfolio/copilot/*`; sin proceso propio | Ranking, atlas y sugerencias candidatas; no decide ni se ejecuta como daemon independiente |
| Mesa de montaje (pestana portafolio) | `iskvw/editor.html` + `iskvw/mesa_montaje.js`, servidos por `hub.py` desde `PORTFOLIO_ROOT` | `127.0.0.1:8900/portafolio/`; tambien `/static/iskvw/editor` | La aplicacion de orden y relacion con copiloto; el par de archivos es la superficie, no solo el HTML. Medido 2026-09-02: HTTP 200 y hash servido igual al fisico |
| SearXNG | `searxng/settings.yml` / runtime externo | `127.0.0.1:8888` | Dependencia de búsqueda de Research, no un Hub de MAK |
| Cola ntfy | `/home/mak/.config/systemd/user/mak-research-queue.service` | Sin puerto; unidad opcional | Inactiva deliberadamente hasta configurar un topic; no confundirla con Research |

#### La mesa de montaje: identidad fisica y consumidores (medido 2026-09-02)

La pestana portafolio del Hub es la aplicacion para ordenar registros,
relacionarlos y sostener un copiloto que aprende. El portafolio del artista es
el PRODUCTO que sale de ahi, no la aplicacion. `iskvw.cl` es una tercera cosa:
el sitio publicado, dormido, que consume `iskvw/datos/archivo.json` y una piel
reemplazable. Las tres comparten el prefijo `iskvw/` por un empalme historico y
NO son la misma superficie.

`IRIS` es el nombre de la POSTULACION con que este sistema se presenta a
Fondart. No es el nombre de un componente y no renombra nada del arbol: la
superficie sigue siendo la pestana portafolio y su par de archivos.

Causa de esta entrada: dos agentes seguidos se confundieron aqui. Buscar las
cadenas visibles de la interfaz ("campo de orden", ATLAS VIVO, incertidumbre,
siguiente frontera, EVIDENCIA EXTERNA) solo en `editor.html` devuelve CERO y
parece que corre una version antigua; viven en el JS que ese shell carga. La
superficie es un PAR y hay que medir los dos.

| Que | Donde | Medicion 2026-09-02 |
|---|---|---|
| Shell | `iskvw/editor.html` (253.564 B) | `sha256 ed7e3bf2...f331`, igual al servido |
| Interfaz | `iskvw/mesa_montaje.js` (113.121 B) | `sha256 d7a50d27...ecb2`, igual al servido; `<script src="mesa_montaje.js?v=20260811-atlas-context-map">` |
| Raiz servida | `PORTFOLIO_ROOT`, por defecto `/home/mak/iskvw` (checkout MAK) | `hub.py:92-99` explica por que se retiro la grafia `HOME/flujo/iskvw` |

Consumidores medidos, no supuestos:

| Consumidor | Vinculo |
|---|---|
| `cultura/mak_plataforma/hub.py` | sirve `/portafolio/` y `/static/iskvw/editor`; monta la pestana en el iframe `ifr-portafolio` |
| `cultura/mak_plataforma/copilot.py` | via `/api/portfolio/copilot/scene|learning|xio-link`; la escena responde `provider=local_hypothesis_engine` y `map.schema=faro-gtm-map-v1` (`copilot.GTM_SCHEMA`) |
| `flujo/src/flujo/departments.py:57,61` | declara `iskvw`, `iskvw/editor.html` y expone `/static/iskvw/editor` en el Hub de FLUJO, sobre SU propia copia |
| `tests/test_iskvw_editor_contract.py` | contrato del par (carril `repo_hygiene`) |
| `tests/test_curaduria_roundtrip.py`, `tools/validar_curaduria.py` | curaduria sobre `iskvw/datos/curaduria.json` |
| `iskvw/datos/tablero.json`, `iskvw/MAPA.md` | material y mapa de la superficie |

Rutas que la interfaz llama (10, medidas desde el propio JS): `inbox`, `audit`,
`draft`, `undo`, `commit`, `external-candidates`, `external-candidates/review`,
`copilot/scene`, `copilot/learning`, `copilot/xio-link`. Las que mutan son POST
(`hub.py:5288-5299`): probarlas con GET devuelve `ruta_api_no_encontrada`, que
es la respuesta correcta y no un defecto.

Riesgo abierto, sin decidir aqui: el par esta trackeado en LOS DOS checkouts
(`/home/mak/iskvw` y `/home/mak/flujo/iskvw`) y hoy es identico byte a byte.
Editar una copia y no la otra las separa en silencio, y el Hub MAK solo lee la
suya. Quien decide si FLUJO debe seguir cargando esta superficie es el contrato
de propiedad, no este documento.

Retiro de esta entrada: cuando exista una sola copia autoritativa del par y el
Hub la resuelva por contrato en vez de por ruta por defecto.

`tools/` (ejecutables sueltos, 1 linea cada uno):

| Tool | Proposito |
|---|---|
| `becas_calendario.py` | Informes research FOSIS -> calendario de postulaciones (fechas/montos, "no-especificado" si falta). |
| `compete_engine.py` | Pipeline monolitico del ecosistema Tapiz<->Psicosis<->Fungi. |
| `comparar_cobertura_fichas.py` | Dos pasadas de percepcion comparadas campo a campo sobre los MISMOS archivos, filtrando por motor. |
| `consolidar_fichas.py` | Trae una pasada nueva al archivo vivo fusionando CAMPO A CAMPO (lo que la nueva no lleno lo hereda de la vieja); ensayo por defecto. |
| `ig_metadatos.py` | Saca del export de Instagram la FECHA exacta y el TEXTO que el artista escribio sobre cada obra, reparando el encoding. |
| `drenar_material.py` | Vacia la cola de trabajo de MAK en paralelo y cuenta lo que salio; se detiene solo si el buscador queda ciego. |
| `gen_vinculos_iskvw.py` | Vinculos entre obras desde los conceptos de las fichas, con los conceptos compartidos como motivo. |
| `gen_mapa_comandos.py` | Genera la tabla de comandos de `MAPA.md` desde el `--help` real del CLI (`--check` falla si quedo desfasado). |
| `render_video_rd.py` | LEGACY/MANUAL-ONLY: ruta H264 sobre `RD.paravideo.blend`; no es el renderer productivo de MAK. |
| `render_flyer_mak.py` | ACTIVO: imagen/poster -> grafo Blender Linux de `RD.blend`, con validación y salida PNG. |
| `render_video_sequence_mak.py` | ACTIVO: reel -> secuencia PNG en MAK; calcula frames reales, usa `RD.blend`, Cycles 128 samples, GPU verificada y deja `render_manifest.json`. |
| `system_map.py` | Blueprint de arquitectura del ecosistema Tapiz/Psicosis/Fungi (schema API_CONTRACT). |
| `tapiz_telemetry.py` | Construye el autorretrato en vivo del ecosistema (`system_status.json`). |
| `gen_animadas_obras.py` | Cada obra curada -> su pieza animada por el motor semantico, determinista desde el id (misma obra = misma pieza); escribe `iskvw/piel/animadas/*.svg` + `iskvw/datos/animadas.json`, que `contrato_archivo.desde_animadas` mete al archivo vinculada a su obra. `tests/test_gen_animadas_obras.py`. |
| `audit_blend_scene.py` | Auditoria AST/read-only de escenas Blender para el consumidor de render; si falta Blender queda `needs_evidence`. |
| `bake_static_materials.py` | Preparacion acotada de bakes de materiales estaticos para el render RD; requiere Blender y no se ejecuta sin autoridad de mutacion. |
| `build_application_intake.py` | Convierte un paquete de proyecto en entrada Project IR; consumidor `tools/project_gate.py` y los Hubs. |
| `reconstruction_adapter.py` / `import_project_reconstruction.py` | Convierte una reconstruccion persistida en registros `mak-project-ir-v1`, enruta Curatoria/Portfolio con abstencion por evidencia y, solo con `--db`, persiste referencias indexadas en el LearningStore; nunca publica ni crea postulaciones. |
| `project_context.py` / `triangulate_project_context.py` | Reutiliza `entities` del LearningStore para enlazar operador VJ, artista, album, proyecto visual, gira candidata, shows y venues con fuentes, grupos de independencia y estados verificables; actualiza Project IR sin promover `review_required` ni crear postulaciones. El grafo se consulta read-only en ambos hubs por `/api/project/context?context_id=...` o `project_id=...`. |
| `build_effort_consumer_crosswalk.py` | Cruza esfuerzo, consumidor y procedencia para priorizar slices de MAK Research y Curatoria. |
| `build_mak_knowledge_db.py` | Inicializa o migra el ledger SQLite de conocimiento MAK; conserva contratos y evidencia sin copiar arboles. |
| `build_mak_canonical_map.py` | Construye el único mapa físico actual de MAK con rutas, metadatos y SHA-256; registra explícitamente las zonas fuera de alcance. |
| `compute_effort_residuals.py` | Calcula residuales de esfuerzo para el backlog y la trazabilidad de entregas. |
| `optimize_blend_scene.py` | Diagnostico/preparacion de optimizacion de escenas Blender; queda gated si no hay runtime Blender. |
| `profile_blender_animation.py` | Perfil read-only de animacion Blender para el consumidor de secuencia/render. |
| `project_gate.py` | Gate CLI de Project IR: route/probe read-only y registro explicito de episodios; consumidor Hub/Research. |
| `project_learning.py` | Compila episodios con resultado verificado, separa holdout por proyecto y prepara una politica candidata con abstencion; `--record-result` recibe paquetes de validadores; no convierte desconocidos en etiquetas ni entrena pesos de deep learning. |
| `mak_status.py` | Estado operacional unificado y read-only de MAK: ledger, consumidores físicos, listeners, procesos, Blender/RD, portafolio, runtimes, configuración de proveedores y registro transversal de lanes; mismo contrato que `GET /api/status`. |
| `project_lanes.py` | Registro read-only de 19 lineas de MAK bajo la primera capa cultural-investigativa: P=NP, tenis, scraping, deep learning, simulacion, eventos, transpilacion, geometria y propuestas; cada lane conserva dialectos, evidencia, consumidor, guardrails y siguiente gate. |
| `research_source_capture.py` | Planifica o registra una sola captura pública con backend explícito, hash, licencia/procedencia y almacén local; el modo por defecto no hace red. |
| `reconcile_garden_knowledge.py` | Reconcilia conocimiento de jardines con el Research/Funding Lab, preservando desconocidos y fuentes. |
| `venue_geometria_scd.py` | Sala DEMO en polilineas 3D (bloque `geometria` del esquema) derivada del modelo radial del teatro SCD Plaza Egana -> `data/venues/scd-plaza-egana.json`, material por defecto del visor `iskvw/piel/venue/`. |
| `venue3d_smoke.mjs` | Corre el JS del visor de salas en node con stubs de DOM: geometria cargada, aristas realmente trazadas, la proyeccion se mueve al orbitar, el recorte por presupuesto se reporta en pantalla, la camara por URL llega, y la orbita de ejemplo (`data/orbitas/`, `schemas/orbita.schema.json`) reproduce la vuelta por defecto cuadro por cuadro. `tests/test_venue3d_smoke.py`. |
| `venue_secuencia.mjs` | Exporta la orbita de una sala como N SVGs de puras lineas desde la MISMA proyeccion del visor; `--orbita <archivo.json>` toma el recorrido de camara como dato (keyframes giro/alto/dist, validados numericamente antes de cortar un solo cuadro). |

`xio/` (server telefono + show kit): server Flask (`xio/actual/server.py`,
`xio/new/server.py`) corre ON-DEVICE en Termux (Shizuku/rish) en el Xiaomi,
puerto 5000 (`XIO_PORT`), 63 archivos de plugins (controlador Xiaomi, hotspot
router activo con auto-heal, FOH monitor). Documentación en este árbol:
`xio/RUNBOOK.md` (23 KB, operación completa), `xio/HOTSPOT_SHOW_RUNBOOK.md`,
`xio/XIO_CAPABILITIES.md`, `xio/PLAN_SERVICIOS_SIN_ROOT.md`, `xio/FACES.md` (Face A
hogar vs Face B show telefono-solo), `xio/show_kit/DIA_DEL_SHOW.md` y
`xio/show_kit/ANOTACIONES_SHOW_20260724.md`.

**Restaurados el 2026-08-28.** Los cuatro primeros faltaban en
`/home/mak/flujo` y sólo estaban en `/home/mak/WIN/flujo/xio/`, mientras cuatro
documentos activos los citaban — nueve referencias colgando, incluido el runbook
del día de show. No estaban obsoletos, estaban ausentes: `xio/FACES.md` es
byte-idéntico en ambos árboles, o sea que WIN no divergió. Se copiaron con
`cp -p` desde el árbol legado, que no se modificó.

Los scripts que estos runbooks nombran (`run_server.sh`, `hotspot_watch.sh`,
`reboot_recover.sh`, `server_supervisor.sh`, `flujo_ondevice.sh`) viven todos en
`xio/new/`; los runbooks los citan sin prefijo.

`cultura/mak_plataforma/` (organismo MAK, corre en el runner self-hosted
`mak`, Linux): `capataz.py` (capataz LOCAL-first con escalada por riesgo),
`hub.py`, `junta.py` (gobierno/expulsion), `entregar.py` / `guardia.py` /
`calidad_loop.py` / `mineria_rd.py` (loop generar->entregar->vetear->merge),
`backlog.py` / `backlog_codex.py` (autorelleno), `energia.py` / `cuotas.py`
(consumo), `descargar.py`, `red_watch.py`, `GENESIS.md` (doctrina). Hermanos:
`cultura/mak_codex/` (agente libre, sandbox, token), `cultura/mak_research/`
(research multi-modelo, `research_lib.py`), `cultura/mak_lenguaje/`
(diccionario 55k, senal tilde), `cultura/mak_curatoria/`,
`cultura/mak_vigia/` (vigilancia de convocatorias: descarga -> normaliza ->
hashea -> difea -> notifica; sin modelo y sin GPU).

`knowledge/` -- knowledge base local: `productoras/`, `venues/`, `logos/`,
`templates/`, `examples/`, `dossiers/` (referencia para cotizaciones/briefs).

`data/` -- `productoras/`, `rd_datos_demo/` (datos reales gitignored fuera de
demo; DB proyectada en `data/rd.db`, no versionada).

`docs/rd/` -- `SINTESIS_DIRECTIVA.md` + `informes/` (research FOSIS/becas y
sintesis ejecutiva para directiva).

`projects/` -- workspaces de produccion: `cotizaciones/`, `cultura/`,
`flujo/`, `flyer_eventos/`, `logo_clean_lab/`, `piezas_vectoriales/`,
`plano/`, `tapiz/` (instrumento `vibecode_spaces.py`), `tilde/`.

`.claude/skills/` (playbooks de agente, nombre + 5 palabras):

| Skill | Resumen |
|---|---|
| `cavecrew` | Decide cuando delegar a subagente caveman. |
| `caveman` | Modo de comunicacion ultra-comprimido. |
| `caveman-commit` | Genera mensajes de commit comprimidos. |
| `caveman-compress` | Comprime archivos de memoria en formato caveman. |
| `caveman-help` | Tarjeta de referencia rapida de modos caveman. |
| `caveman-review` | Comentarios de PR ultra-comprimidos, accionables. |
| `caveman-stats` | Muestra uso real de tokens de la sesion. |
| `director-de-arte` | Marco de ingenieria estetica para piezas culturales. |
| `entregas-rd` | Playbook para cotizaciones/flyers/planos comerciales RD. |
| `godspeed` | Orquestador que delega todo a subagentes baratos. |
| `motor-omega` | Dos reglas Omega11 para exponer piezas nuevas. |
| `orquestacion-gemini-claude` | Patron voz barata -> delega caro a Claude. |
| `relevo-web` | Reader/Web/Coder por chat web gratis, sin API. |
| `revivir-subagentes` | Recupera subagentes muertos o detenidos. |
| `ruteo-eficiencia` | Traduce pedido a comando/skill ya instalado barato. |
| `taller-svg-rd` | Produce piezas SVG->PDF de Reduciendo Dano. |
| `teleport-sesion-web` | Trae sesion web de claude.ai al CLI local. |
| `toma-de-decisiones` | Marco para decidir modelo/agente/riesgo por tarea. |
| `verificar-antes-de-negar` | Verificar antes de negar existencia de algo. |

### 1-ter. Carriles de test y compuertas de CI (medición 2026-09-02)

Medido con un solo entorno, `/home/mak/.venv`, cuyo `.pth` resuelve el motor en
`/home/mak/flujo/src`. El veredicto aislado lo sigue dando CI.

| carril | checkout | archivos | tests | resultado |
|---|---|---:|---:|---|
| `mak` | MAK | 173 | 2175 | verde |
| `integration` | MAK | 32 | 371 | verde |
| `repo_hygiene` | MAK | 14 | 87 | verde |
| `flujo` | FLUJO | 161 | 1611 | verde, 44 skip |
| `repo_hygiene` | FLUJO | 9 | 55 | verde, 1 skip |

`tests/` de MAK lleva físicamente 2633 tests: 2175 + 371 + 87.

**Cómo selecciona el carril, y por qué importa.**
`tests/conftest.py::pytest_ignore_collect` consulta el mapa persistido ANTES de
coleccionar, pero **sólo si `-m` es exactamente un nombre de carril**. Entonces
no importa los módulos ajenos: `-m mak` colecciona 2175 y no toca el resto.
Cualquier expresión compuesta cae en la semántica normal de pytest e importa
todo: `-m "mak and not integration"` colecciona 2633 y deselecciona 458 -- la
misma selección, todos los módulos importados. Por eso un módulo ajeno con
import roto es invisible bajo `-m mak` y se vuelve error de colección con
cualquier expresión más rica, y por eso un test sin mapear no queda
deseleccionado sino que su módulo se saltea entero.

La autoridad del carril es `context/test_lane_map.json`.
`tools/test_lane_map.py` es el clasificador y el respaldo de arranque, nunca la
autoridad.

**Compuertas de CI, una por carril.** `ci-mak.yml` (`-m mak`),
`ci-integration.yml` (`-m integration`, dispara en MAK y FLUJO porque el
carril es la composición) y `ci-flujo.yml` (`-m flujo`). El monolítico `ci.yml`
se retiró el 2026-09-02.

**El carril `repo_hygiene` no corría en ninguna compuerta hasta el 2026-09-02.**
La separación lo creó y CI recibió un job por carril OPERATIVO, así que 14
archivos en MAK y 9 en FLUJO quedaron sin gatear -- y por eso cuatro ratchets
de MAK y tres de FLUJO estuvieron rojos sin que nadie se enterara. Los ratchets
que detectan que la documentación miente eran justo los que no tenían
compuerta. Sólo `seguridad.yml` en FLUJO corría uno, por ruta. Ya está gateado
en las dos ramas, verificado verde antes de poner la compuerta.

**Dos punteros medidos como obsoletos, sin resolver.**

- `context/code_structure_index.json` declara 932 archivos Python e incluye
  `src` en su alcance. De los 226 que indexa bajo `src/`, **200 ya no existen**:
  se generó el 2026-09-02 05:08 UTC, antes de que el motor terminara de
  moverse a `flujo/src`. Se regenera con `py -m flujo code-index`.
- `context/test_lane_map.json` fija `source.code_index_sha256` en
  `3d82ee64...`, y el sha real del índice hoy es `e8f49ec6...`. El contrato de
  carriles apunta a una versión del índice que no está en disco.

**Residuo físico sin limpiar:** `/home/mak/src/flujo` son 5,3 MB de
`__pycache__` huérfano -- 200 `.pyc` y **0 `.py`**. No es importable (un
`__pycache__` sin su `.py` no se importa en Python 3), Git no lo ve porque sólo
contiene rutas ignoradas, y `tools/release_gate.py` no lo bloquea porque su
regla mira el *tracking*, no la presencia física. Efecto lateral real:
`tests/conftest.py` inserta `/home/mak/src` en `sys.path` porque `is_dir()` da
verdadero por esos directorios; `import flujo` resuelve bien sólo porque
`flujo/src` quedó antes en el orden.

## 2. Modelos, APIs e integraciones disponibles (sin llaves)

### 2.1 Conteo medido de la superficie API

El conteo usa una regla conservadora: una API/integracion = un proveedor o
servicio con un adaptador reconocible en el codigo. No cuenta cada endpoint,
cada modelo, cada sitio web fuente ni cada variable de entorno. Las claves y
sus valores nunca se imprimen ni se registran aqui.

Conteo verificado el 2026-08-17:

Nota de retiro: cualquier mención restante de `watsonx`, AWS o Azure en esta
matriz describe una corrida histórica o un campo de evidencia; no representa
un proveedor disponible. La ruta LLM activa es Groq -> Gemini -> Ollama.
Cerebras queda como adaptador opt-in, pero su cuenta respondió HTTP 402 por
falta de crédito. La visión local usa Ollama.

| Grupo | Cantidad | Integraciones reconocidas | Estado resumido |
|---|---:|---|---|
| Proveedores LLM cableados | 4 | `groq`, `gemini`, `cerebras`, `ollama` | Ruta por defecto Groq -> Gemini -> Ollama; Cerebras opt-in observado con HTTP 402 |
| Busqueda/captura | 3 | `tavily`, `searxng`, `firecrawl` | `tavily` y SearXNG pasaron sonda; Firecrawl requiere clave |
| Notificacion | 1 | `ntfy` | Adaptador en `research_lib.py`; requiere topic para publicar |
| Produccion/operacion | 4 | `canva`, `github`, `instagram`, `google_drive` | Canva/GitHub/Instagram estan cableados; Drive opera por `rclone` |
| **Total de integraciones API/servicio cableadas** | **12** | | |

Hay ademas **1 backend opcional de captura**, `crawl4ai`: esta instalado en el
extra reproducible `.[research]` y paso captura real con Chromium local. El
total es **13 backends** contando esa capacidad opcional.

La aplicacion expone **1 superficie HTTP interna activa** verificada en primer
plano: hub MAK en `127.0.0.1:8900` con `GET /health` HTTP 200. Los puertos
8890 y 8891 no se usan como interfaz publica. SearXNG queda como backend local
en `127.0.0.1:8888`, con contenedor `searxng` y politica `unless-stopped`.
El catalogo suma **14 superficies** contando las 13 integraciones/backends y
el hub; la matriz de verificacion de cada una esta abajo.

No entran en el conteo: Anthropic/Claude Code y Arena (herramientas externas al
runtime del repo), `DASHSCOPE_API_KEY`, `QWEN_API_KEY`, `NVIDIA_*` y
`OPENROUTER_API_KEY` (declarados, pero sin adaptador activo en el roster),
los sitios web monitoreados por Vigia y XIO (superficie
historica fuera de la operacion actual).

### 2.2 Estado de credenciales medido sin exponer valores

Probe de autenticacion ejecutado el 2026-08-15. `valid` significa que el
servicio acepto una solicitud de lectura o token; no significa que todos los
modelos, permisos o limites de cuenta esten disponibles.

| Variable | Resultado | Fuente/alcance |
|---|---|---|
| `WATSONX_API_KEY` | `retired` | Eliminada de los env activos; copia protegida solo en `_archive/watsonx-retired-20260820/` |
| `NVIDIA_API_KEY` | `valid` | `GET /v1/models` HTTP 200 desde `.env` de flujo |
| `NVIDIA_NIM_API_KEY` | `valid` | `GET /v1/models` HTTP 200 desde `.env` de flujo |
| `TAVILY_API_KEY` | `valid` | Busqueda basica HTTP 200; solo aparece en `n8n-local/research.env`, que no es runtime activo |
| Resto de las variables listadas | `absent` | Sin valor en las configuraciones MAK revisadas; no se probo ninguna llamada |

La prueba no ejecuto inferencias LLM, scrapes de Firecrawl, cargas de Canva ni
mutaciones de GitHub. La primera sonda de Tavily devolvio 400 por la forma de
la consulta; la segunda uso el contrato exacto del adaptador y devolvio 200.

### 2.3 Sonda del entorno Research seleccionado (2026-08-17)

`/home/mak/research/research.env` fue revisado sin imprimir valores: modo 600,
propietario `mak`, formato `KEY=VALUE`, sin claves duplicadas ni lineas
malformadas. El conjunto seleccionado contiene Groq, Gemini, Cerebras, Firecrawl y
Ollama.

| Integracion | Sonda foreground | Resultado |
|---|---|---|
| Groq | `LLM._groq(..., max_tok=8)` | OK; respuesta de 2 caracteres |
| Gemini | `LLM._gemini(..., max_tok=8)` | OK; `gemini-3.6-flash`, respuesta no vacía |
| Cerebras | `LLM._cerebras(..., max_tok=8)` con `gpt-oss-120b` y `gemma-4-31b` | Ambos HTTP 402 `Payment Required`; cuenta sin credito disponible, no es un nombre de modelo invalido |
| Firecrawl | `capture_url(example.com, backend=firecrawl)` | Captura HTTP 200; 167 caracteres |
| Ollama | `LLM._ollama(..., max_tok=8)` | OK; respuesta de 3 caracteres |

El 402 de Cerebras es un limite de cuenta, no un fallo de instalacion o
formato. Azure no participa del runtime y no tiene adaptador activo. Canva y
ntfy no estan en el entorno seleccionado y no se consideran activos.

`GITHUB_TOKEN` no es necesario en el runtime local: `gh auth status` devolvio
exit 0 y la sesion local de `gh` esta autenticada. El puente
`tools/gmail_to_github_issues.gs` usa su propia Script Property externa para
crear Issues desde correos; esa propiedad requiere Issues Read/Write. Las
Actions usan el token efimero incorporado de GitHub, no el `.env` de MAK.

Solo existencia + donde se configura. Nunca el valor de una llave.

| Integracion | Que es | Donde vive la config |
|---|---|---|
| Claude / Anthropic | Director (Fable/Opus) + subagentes Sonnet/Haiku; tiers en tabla de `CLAUDE.md` | `ANTHROPIC_API_KEY` en `.env` (ver `.env.example`); ejecutado via Claude Code CLI, no en runtime del repo |
| ollama LOCAL en MAK | Proveedor local de inferencia: `completion` (`gemma3:4b`, `deepseek-coder:6.7b`) y `embedding` (`nomic-embed-text`) | Servicio `ollama.service` (`/usr/local/bin/ollama serve`) activo en `127.0.0.1:11434` (v0.32.0), con `OLLAMA_HOST=127.0.0.1`, paralelismo 1 y contexto 8192, revalidado 2026-09-02. Consumidores de código confirmados: fallback LLM de Research (`cultura/mak_research/research_lib.py`), fallback coder de MAK Codex (`cultura/mak_codex/codex_lib.py`), juez local del Conductor (`cultura/mak_plataforma/discernment.py`), visión de minería RD (`cultura/mak_plataforma/mineria_rd.py`), revisión por tandas (`cultura/mak_plataforma/tandas.py`) y chat local (`cultura/mak_plataforma/chat_agente.py`, default `gemma3:4b`). No se encontró consumidor local confirmado para `nomic-embed-text`; su disponibilidad no prueba uso. |
| IBM watsonx | Retirado; evidencia histórica preservada fuera del runtime | Sin claves activas; herramientas exclusivas archivadas en `_archive/watsonx-retired-20260820/` |
| Groq | Proveedor rapido para roles `razonar`/`bulk` | `GROQ_API_KEY`, `GROQ_MODEL` en `cultura/mak_research/research_lib.py` (defaults linea 32) y `.env` |
| Gemini | Reemplazo cloud probado para sintesis y razonamiento cuando Cerebras no tiene crédito | `GEMINI_API_KEY`, `GEMINI_MODEL` en `research_lib.py`; usa `gemini-3.6-flash` |
| Cerebras | Proveedor rapido, `CEREBRAS_MODEL=gpt-oss-120b` | `CEREBRAS_API_KEY`, `CEREBRAS_MODEL` en `research_lib.py` (linea 33) y `.env` |
| Azure AI | Retirado por decisión del usuario; no se carga ni se ofrece como fallback | Solo referencias históricas preservadas fuera de la ruta activa |
| DashScope / Qwen | Coder barato de volumen (gate, nunca directo a Claude) | `DASHSCOPE_API_KEY` / `QWEN_API_KEY` en `.env.example` |
| NVIDIA NIM | Alternativa barata (Qwen/DeepSeek/Nemotron) | `NVIDIA_API_KEY` / `NVIDIA_NIM_API_KEY` en `.env.example` |
| OpenRouter | Router/fallback de modelos | `OPENROUTER_API_KEY` en `.env.example` |
| SearXNG (LAN, en la caja) | La busqueda de research. Sin llave, sin tope de creditos | `SEARXNG_BASE_URL` (default `http://127.0.0.1:8888`) y `SEARXNG_ENGINES`; contenedor local activo, `GET /search?format=json` HTTP 200 el 2026-08-17 |
| Tavily | Respaldo de busqueda cuando SearXNG no devuelve nada | `TAVILY_API_KEY`; sonda basica HTTP 200 el 2026-08-17 cuando se carga el archivo protegido de Research |
| Firecrawl | Captura web estructurada para Research-to-Project | `FIRECRAWL_API_KEY`; adaptador `cultura/mak_research/source_pipeline.py`; opcional y no habilitado sin clave |
| Crawl4AI | Backend local alternativo de captura web | `.[research]` instala `crawl4ai>=0.9.2,<1.0`; Chromium de usuario instalado; `example.com` capturado HTTP 200 el 2026-08-17 |
| ntfy | Notificacion movil de resultados y alertas | `NTFY_TOPIC_IN` / `NTFY_TOPIC_OUT`; transporte en `research_lib.py`; no se publica sin topic |
| Canva | Carga de assets producidos por el pipeline | `CANVA_API_TOKEN`; adaptador en `src/flujo/export/canva.py`; no se probo una carga real en esta medicion |
| Instagram / parth-dl | Ingesta primaria de posts y reels para eventos y curatoria | `parth-dl` instalado; usado por `src/flujo/eventos/flyer_auto.py` y `src/flujo/ig/download.py`; no es una API oficial autenticada |
| Arena (LMArena) | Frontier gratis on-demand para arquitectura dura, sin API | manual, sin config en repo; ver skill `toma-de-decisiones` |
| parth-dl (IG) | Descarga real de posts/reels de Instagram (via primaria desde 2026-07-22) | `pip install parth-dl`; usado en `src/flujo/eventos/flyer_auto.py` y `src/flujo/ig/download.py`; imginn.com solo fallback (403 Cloudflare), instaloader NO funciona (IG exige login), NO yt-dlp |
| Blender 4.5 | Render headless (flyer video, Chataigne prep) | MAK: `~/blender/` tarball portable 4.5.3 LTS (CUDA, GTX 1650); la ruta WIN queda como referencia historica |
| Chataigne builder | Genera `.noisette` para Resolume/Chataigne | `src/flujo/resolume/automator.py::build_chataigne_noisette_experimental`; schema validado contra fixtures reales (`tests/fixtures/chataigne_1103_real*.noisette`, `tests/test_noisette_real_fixture.py`) -- nunca especular, la fixture manda |
| rclone / OneDrive en MAK | Entrega de renders (Drive de Google via `gdrive:` remote) | systemd `onedrive-rclone.service` en MAK; detalle en `context/LAST_HANDOFF.md` y `src/flujo/version.py` (changelog) |
| GitHub (gh CLI + runner self-hosted + workflows) | CI, gate de PRs, ordenes de curatoria, publicacion catalogo/portfolio y build diferido de XIO | `gh` CLI local; runner self-hosted `mak` (online, labels `self-hosted,Linux,X64,mak,eventos`); workflows activos de MAK en `.github/workflows/`; `build-xio-apk.yml` es manual y queda diferido para Chataigne/OSC/VJ |

Vtracer / curl_cffi / imageio_ffmpeg: usados puntualmente en pipelines de
render/vectorizacion cuando hace falta, instalados ad-hoc (`pip install
<paquete>`) -- no son dependencias fijas de `pyproject.toml`/`requirements.txt`
(esas listan solo el core: matplotlib, pyyaml, pydantic, typer, rich,
jsonschema, requests).

## 3. Infraestructura

| Nodo | Rol | Detalle |
|---|---|---|
| MAK (Debian 12, host actual) | Organismo autonomo, GPU GTX 1650 (CUDA), runner self-hosted GitHub y hub local | `~/plataforma/` = proyección de compatibilidad para `cultura/mak_plataforma/` (la implementación canónica); Blender 4.5.3 LTS portable en `~/blender/`; snapshot histórico 2026-08-16: Hub activo en 8900 y 8890/8891 sin listener. El estado actual se consulta en la tabla 1-bis y `docs/MAK_CURRENT_STATE.md` |
| WIN (archivo historico) | Evidencia y origen de la migracion | `/home/mak/WIN` es read-only para la operacion; no es runtime ni consumidor de APIs actuales |
| OneDrive / Google Drive | Storage de entrega de renders | rclone en MAK (`onedrive-rclone.service`), remote `gdrive:` |

XIO no forma parte de la superficie operacional actual ni del conteo de APIs;
su material queda como referencia historica separada.

## 4. Como arrancar proyecto nuevo (receta)

1. Read `agents.md` + `context/LAST_HANDOFF.md` + this inventory. Nothing else before starting.
2. Clasificar la ruta destino: nucleo vivo / operacion diaria / historico / generado (ver mapa de `CLAUDE.md`) antes de tocar nada.
3. Elegir dominio: `mak/`, `rd/`, `portfolio/`, `data/`, `capabilities/`,
   `products/`, `operations/` o `tests/`; estos no son ramas permanentes.
4. Si toca producción aislada: worktree propio (`EnterWorktree`/`git worktree
   add`) y rama temporal `codex/*` desde `origin/main`.
5. Elegir el modelo mas barato que resuelva la tarea (tabla seccion 2 + `CLAUDE.md` "Regulacion de gasto"); escala solo si aplica un trigger.
6. Si es pieza cultural nueva: aplicar motor-omega (Omega11 declarada + fracaso no se reinterpreta) antes de exponer.
7. Cambios minimos, completos, verificables -- nada a medias, nada de TODO/placeholder.
8. Verificacion minima segun area tocada (Python: compileall+pytest+`flujo verify`; Web: typecheck+build:context; 
9. Entregables (datos/docs/piezas) en espanol correcto UTF-8; `CLAUDE.md`/`context/*.md` operativos en ASCII.
10. PR siempre contra `main`, CI verde obligatorio; el director hace la
    promoción curada al dominio o superficie correspondiente.

Actualizar este doc en el mismo PR si algo listado aca cambia (tool
eliminada, skill nueva, IP/puerto distinto): el doc miente si lista algo que
ya no existe.

## 5. Registro VIVO/MUERTO (tools/ top-level)

Regla 2026-07-25 (causa: sesiones gastadas arreglando herramientas sin
consumidor; retiro: cuando exista chequeo automatico de consumidores):
toda herramienta en `tools/` (top-level, no subdirs) declara aca su
consumidor medido o entra en REVISAR. `tests/test_higiene_repo.py`
(`test_tools_en_registro`) exige que el nombre de archivo aparezca en esta
tabla; archivo sin entrada = ratchet rojo.

| archivo | estado | consumidor/evidencia | ultima senal |
|---|---|---|---|
| `release_gate.py` | VIVO | gate local de coherencia de rama ANTES de push, corrido por el operador. No es paso de CI y no puede serlo: resuelve `/home/mak` y `/home/mak/flujo` como checkouts fisicos en su rama, y sale con codigo 5 aun con cero blockers porque READY_TO_PUSH exige evidencia de que las suites corrieron verdes. Se quito de `ci-mak.yml` y `ci-flujo.yml` el 2026-09-02, en su primera ejecucion | 2026-09-02 |
| `runtime_preflight.py` | VIVO | prueba que codigo ejecuta cada servicio; consumido por `tools/release_gate.py` (comprobacion de runtime) y por el operador | 2026-09-02 |
| `bridge_issue_render.py` | REVISAR | utilidad operativa conservada al fusionar la caja; consumidor manual, sin caller de produccion medido | 2026-08-31 |
| `build_duplicate_decision_report.py` | REVISAR | informe manual de duplicados; se conserva como herramienta de operador, sin caller automatico medido | 2026-08-31 |
| `consolidate_static_duplicates.py` | REVISAR | consolidacion manual de artefactos estaticos; sin caller automatico medido | 2026-08-31 |
| `enviar_a_mak.py` | REVISAR | puente manual de entrega; conservado durante la fusion, sin caller automatico medido | 2026-08-31 |
| `instalar_enviar_a_mak.py` | REVISAR | instalacion/envio manual; conservado durante la fusion, sin caller automatico medido | 2026-08-31 |
| `mak_materialize_fused_root.py` | VIVO | materializa una sola raiz fisica en `/home/mak` sin sobrescribir ni borrar; consumidor: operador, a mano | 2026-08-31 |
| `mak_fuse_roots.py` | VIVO | construye la proyeccion lossless de las tres raices y registra igualdad/divergencia sin elegir fuente; consumidor: `mak_materialize_fused_root.py` y operador | 2026-08-31 |
| `watsonx_coder_bench.py` | REVISAR | benchmark manual preservado como evidencia; sin caller automatico medido | 2026-08-31 |
| `watsonx_smoke.py` | REVISAR | smoke manual preservado como evidencia; sin caller automatico medido | 2026-08-31 |
| `watsonx_vision_bench.py` | REVISAR | benchmark manual preservado como evidencia; sin caller automatico medido | 2026-08-31 |
| `watsonx_vision_smoke.py` | REVISAR | smoke manual preservado como evidencia; sin caller automatico medido | 2026-08-31 |
| `compile_contracurator.py` | VIVO | compila la exposicion falsable del Contracurador sobre la vista de archivo ya proyectada; consumidor `tests/test_contracurator.py` y el Hub en `/api/portfolio/archive-view` | 2026-08-28 |
| `medir_organismo.py` | VIVO | mide el organismo MAK y lo imprime: lineas de cron activas/pausadas, cuales de los cinco organos de `/home/mak/GENESIS.md` responden, si `main` tiene proteccion de rama (hay un cron que mergea), cuantas lineas arrancarian al reanudar, y los entornos Python. Solo lectura: no toca crontab, servicios ni archivos. Existe para que `docs/MAK_ORGANISMO.md` no vuelva a cargar esas cifras en prosa -- la regla 3 de `docs/AUTORIDAD.md` dice que lo medido se mide, no se escribe. Consumidor: una persona, a mano | 2026-08-28 |
| `capabilities.py` | VIVO | contrasta nueve superficies declaradas de MAK/FLUJO con sus fuentes, unidades systemd, listeners/endpoints locales, modelos Ollama y rutas consumidoras; emite `mak-capabilities-runtime-v1` en texto/JSON/Markdown y falla con `--check` si falta una fila, fuente, modelo, consumidor o servicio requerido. `--check-branch` contrasta además `branch_profile.json` con el checkout y el selector pytest (excepto perfiles históricos). No reescribe `CAPACIDADES.md`; consumidor: operador y CI acotado | 2026-09-02 |
| `medir_tests.py` | VIVO | mapea la suite por el commit que agrego cada archivo de test: separa las areas que llegaron enteras en un commit (un diseno) de las que crecieron en commits sueltos a lo largo de semanas (acrecion, donde una propiedad puede quedar verificada dos veces). El proposito de cada test ya esta escrito en el mensaje de su commit de alta, asi que no abre ningun test para saberlo: corre un solo `git log` y solo cuenta lineas `def test_`. `--cronologia` lista los 164 commits de alta del mas viejo al mas nuevo. Solo lectura. Consumidor: una persona, a mano | 2026-08-29 |
| `medir_test_overlap.py` | VIVO | medidor read-only de solapamiento estructural: agrupa funciones test por forma AST normalizada, conserva nombres/operaciones y produce candidatos de revision; consumidor: una persona, a mano | 2026-08-31 |
| `mak_merge_roots.py` | VIVO | planifica y ejecuta la fusión física reversible de raíces `flujo`/`vibecodeine`: compara hashes, conserva variantes y registra cada copia o redirección; consumidor: operador, a mano | 2026-08-31 |
| `mak_triangulate_roots.py` | VIVO | cruza fechas de inode, hashes y primera/última aparición en Git para distinguir antecesores, continuaciones y snapshots sin interpretar su contenido; consumidor: operador, a mano | 2026-08-31 |
| `test_lane_map.py` | VIVO | clasifica los tests por imports AST y aplica los carriles `flujo`, `mak`, `integration`, `repo_hygiene` o `review`; consumidor: `tests/conftest.py` y operador mediante `--select-changed` | 2026-08-31 |
| `mak_heartbeat.py` | VIVO | compara el estado medido de MAK contra `data/mak_expected_state.json` (cron activas, organos, unidades systemd de usuario Y de sistema -- ollama, postgresql, docker, el runner de Actions --, frenos de archivo y contenedores docker) y solo habla cuando difieren, en cualquiera de las dos direcciones (algo que debia responder y no responde, o algo que debia estar apagado y arranco). Sale 0 en silencio si todo calza. Si hay deriva, la imprime y avisa por ntfy reutilizando `ntfy_publish`/`load_env` de `cultura/mak_research/research_lib.py`; sin tema configurado, o si el envio falla, degrada a log y lo dice (nunca falla en silencio). `--capture` mide el estado actual y lo guarda como nueva linea base, para fijarla despues de reanudar. Solo lectura sobre MAK: no toca crontab, servicios ni contenedores. Existe porque el crontab estuvo pausado dos semanas sin que nadie se enterara mientras la suite y el hub seguian verdes. Consumidor: linea de cron `MAK-HEARTBEAT` en `cultura/mak_plataforma/crontab.mak` (pausada, la reanudacion es decision del operador) y `tests/test_mak_heartbeat.py`; a mano: `python3 tools/mak_heartbeat.py` | 2026-08-30 |
| `compile_opportunity_constraints.py` | VIVO | compiles local opportunity evidence into fail-closed constraints; consumed by Piso 1 tests | 2026-08-25 |
| `compile_portfolio_dossier.py` | VIVO | compiles the evidence-governed internal portfolio dossier; consumed by Piso 4 tests | 2026-08-25 |
| `compile_product_plan.py` | VIVO | compiles the shared portfolio/application/research plan; consumed by Piso 4 tests | 2026-08-25 |
| `capture_opportunity_validity.py` | VIVO | captures a bounded local opportunity source with hash and validity state; consumed by opportunity validity tests | 2026-08-27 |
| `compile_opportunity_delta.py` | VIVO | computes an additive opportunity delta from versioned evidence returns; consumed by opportunity-delta tests | 2026-08-27 |
| `compile_selective_recompute_receipt.py` | VIVO | compiles bounded recomputation receipts without mutating source evidence; consumed by selective-recompute tests | 2026-08-27 |
| `compile_vigia_capture_plans.py` | VIVO | compiles read-only Vigia capture plans from declared source candidates; consumed by Vigia bridge tests | 2026-08-27 |
| `inspect_operational_memberships.py` | VIVO | inspects archive-scoped operational membership projections without executing capabilities; consumed by membership tests | 2026-08-27 |
| `render_product_view.py` | VIVO | renders the common product view or the general ISKVW archive portfolio view as JSON/Markdown; consumed by product-view tests | 2026-08-27 |
| `compile_research_frontier.py` | VIVO | compiles non-dispatched research jobs from prioritized gaps; consumed by Piso 3 tests | 2026-08-25 |
| `generate_artistic_program_hypotheses.py` | VIVO | generates provisional artistic-program hypotheses without truth promotion; consumed by Piso 2 tests | 2026-08-25 |
| `triangulate_research_evidence.py` | VIVO | triangulates captured claims across independent source groups; consumed by Piso 3 tests | 2026-08-25 |
| `cultura/mak_vigia/vigia.py` | LIVE | Measured 2026-08-05: the box crontab has `MAK-VIGIA`, `MAK-REPO-SYNC` copies `cultura/mak_vigia` -> `/home/mak/vigia`, and `/home/mak/vigia/estado/` exists. First live seed was run with `--sin-notificar` to avoid initial phone spam: 425 items observed. After the first seed absorbed late `fondos_de_cultura` items, three immediate follow-up runs returned `fondos_de_cultura nuevos=0`. It notifies through ntfy to `VIGIA_NTFY_TOPIC` and, for `tipo: enfermeria` sources, to `VIGIA_NTFY_TOPIC_ENFERMERIA`. It is a DIFF, not an LLM: download -> normalize -> sha256 -> compare against `cultura/mak_vigia/estado/vistos.jsonl` -> notify only new items; zero tokens, zero GPU, no model. Golden rule: a source that starts parsing ZERO items, or has 4 days with nothing new, sends a high-priority ERROR notification; silence must not look like "it works". `tests/test_vigia.py` | 2026-08-05 |
| `order_projection.py` | VIVO | proyecta la identidad certificada a un orden accionable SIN mover un archivo. Existe porque dos consumidores que ya existian se habian detenido en el mismo hecho faltante y ambos lo decian con sus propias palabras: `cross_root_relations` pedia 'compute full_sha256 for the overlapping assets' y `show_asset_usage` declaraba en sus limites que 'la verificacion por contenido no esta disponible para el 99,75 %'. Tres tiers y solo uno es seguro: T1 copia suelta en la raiz del disco (24 clases, 6.44 GB, no requiere decision porque cual de las dos es la extraviada es un hecho del filesystem), T2 cruza raices (458 clases, 30.09 GB, bytes identicos tienen DOS lecturas -- una obra archivada dos veces, o un output reusado en otro encargo -- y el contenido no puede elegir), T3 dentro de un proyecto (865 clases, 24.51 GB, se deja en paz). Cada propuesta T1 se prueba contra los `.usage.json` de Resolume y **3 de 24 quedaron en HOLD** porque la composicion `sampier` nombra `2.mov`, `3.mov` y `4.mov`: el chequeo por basename puede dar un HOLD falso pero nunca un SAFE falso, y esa es la direccion en que la asimetria tiene que apuntar. La puerta corta por palanca: 50 preguntas -> **6 que cubren el 93,2%** de los bytes en disputa, y las 44 diferidas llevan `reopen_when` observable sin conocer la respuesta. `tests/test_certified_identity.py` | 2026-08-24 |
| `resolve_identity_ties.py` | VIVO | resuelve los empates de identidad que el indice se NIEGA a decidir por diseno. `archivo_index.sqlite` trae `hash_state='pending'` en 45424 de 45536 assets y un `full_sha256` real en 112 (0.25%), y `project_reconstruction` lo declara en su propio docstring: 'a shared sample hash never decides project identity here; it produces an explicit tie'. Habia 1348 empates sobre 4104 assets, y el mismo codigo nombra el remedio: 'compute full_sha256 for the overlapping assets'. Resultado: 1347 de 1348 grupos resueltos, 4097 CERTIFIED_SAME, 7 CERTIFIED_DISTINCT, **0 sin resolver**, 56.85 GiB de duplicacion exacta probada. Los 7 distintos son frames consecutivos de un cache de fluidos (`LYON/3/123_flip_fluid_cache`): mismo tamano, mismo prefijo, contenido distinto -- exactamente donde un sample hash miente. La escalada tiene DOS etapas, no tres: una tercera etapa intermedia (cola de 64 KiB) se midio sobre estos mismos 4104 assets, resolvio CERO distinciones y costo 197 MB leidos para nada -- se BORRO, y la razon es general, no un ajuste de parametro: un test sublineal solo puede RECHAZAR (hallar un byte distinto), nunca CERTIFICAR coincidencia sobre contenido no acotado, y un sample hash selecciona justo los casi-duplicados que ese test esta construido para no poder ver. Quedan tamano (gratis, resolvio 0 aqui) y lectura completa (la unica etapa que paga). Nunca escribe en el indice: sale a un sidecar por `asset_id`. `tests/test_identity_ties.py` | 2026-08-24 |
| `substrate_experiment.py` | VIVO | el experimento adversarial PRE-REGISTRADO: las siete predicciones estan en el docstring, se enuncian antes de correr y no se editan despues. La cadena no es sintetica y el renombre no es mio -- `ICLODU5` es una carpeta de export donde una herramienta ya reemplazo cada nombre por uno aleatorio (`SUERTE/Comp 17.mp4` -> `ICLODU5/ROQX6471.MP4`, y 'Comp 17' es a su vez el nombre por defecto de After Effects, o sea ninguno de los dos lados carga significado autorado). La perturbacion destruye directorios, basenames, extensiones y mtimes, y mueve la mitad a un ZIP. Resultado: Content y Lineage sobreviven, **State NO** -- 4 se vuelven 8 porque la ruta del ZIP no lee XMP, asi que el mismo byte produce dos state_id segun el contenedor. Y la admision mayor: mis cadenas **no son source->export, son el mismo archivo en dos lugares**, porque 0 de 120 grupos con DocumentID compartido cruzan extension -- con XMP como autoridad esa cadena NO EXISTE en este corpus. El experimento que MAT-SI pidio no se puede correr aqui, y eso es el resultado. | 2026-08-23 |
| `substrate_scan.py` | VIVO | escanea un corpus al sustrato de identidad y se NIEGA a producir un resultado sin registro de corrida. Existe porque la medicion anterior de este disco no se podia repetir: faltaban cinco de las nueve cosas que una repeticion necesita (commit, version del extractor, manifest, errores con su ruta, hash del output) y peor, la tabla reportada **empalmaba dos corridas con dos versiones del extractor**, asi que los totales no correspondian a ninguna ejecucion que hubiera existido. Ahora cada corrida guarda: commit y si el arbol estaba sucio, argv verbatim, la ruta raiz con su device y fstype, un **digest de las fuentes del extractor realmente importadas** (una version que alguien deba acordarse de subir es una version que deja de ser verdad), el manifest completo con tamano/mtime/sha256, cada error CON su ruta y su etapa, y un hash del resultado que excluye el wall time para que dos corridas se puedan comparar byte a byte. `--reuse-manifest` escanea exactamente los archivos que otra corrida registro, que es la unica forma de separar 'cambio el codigo' de 'cambio el disco'. `--manifest-only` produce la linea base sin extraer. `tests/test_substrate.py` | 2026-08-23 |
| `png_xmp_witness.py` | VIVO | pasada adversarial read-only sobre el corpus PNG: valida firma, tabla de chunks, CRC e `IEND`, hashea cada archivo y busca marcadores XMP fuera de los chunks `iTXt`/`tEXt` con clave `XML:com.adobe.xmp`; devuelve `eligible_for_witness=false` si hay corrupción, sidecars inválidos o hits fuera del vocabulario. No escribe el SSD; el reporte va a `--out`. `tests/test_png_xmp_witness.py` | 2026-08-24 |
| `reconcile_iskvw_media.py` | VIVO | une el indice curado de iskvw con los archivos reales de IG por el ID numerico del medio, solo lectura. Existe porque `iskvw/datos/archivo.json` declara `medio.estado_fuente: "ausente"` en 219 piezas y no trae `medio.src` en 1807, mientras los archivos SI estan en `/home/mak/portfolio_media/media`: el vinculo existia en disco y el indice no lo sabia, porque los dos ordenes nunca se unieron. Medido sobre las 2034 piezas: 1818 registros traen ID numerico y dan **1599 IDs distintos** -- o sea 219 registros comparten ID con otro, que es duplicacion en el archivo y no en el disco; 1591 IDs resuelven a UNA superficie, **8 colisionan** y las 8 son el original junto a su contact sheet (verificado uno por uno), 0 huerfanos y 0 duplicados dentro de la misma superficie. Reparto por superficie: posts 775, other 329, stories 240, archived_posts 154, reels 88, igtv 5. Los 216 registros SIN ID numerico se abstienen a proposito: son justamente los nombrados a mano, los unicos que traen titulo humano, fecha y frase del autor, asi que adivinarles un ID pegaria los registros mas fuertes al archivo equivocado. La precedencia `medio.src` antes que el ID compuesto esta fijada por test, porque el primer intento devolvio cero al leer `piezas[].id` directo. `--output` escribe SOLO el reporte, nunca ninguna de las dos fuentes. `tests/test_reconcile_iskvw_media.py` | 2026-08-23 |
| `env_baseline.py` | VIVO | mide las variables de entorno que el codigo lee FUERA de `src/flujo` y que `MAPA.md` no documenta. La puerta `test_toda_variable_de_entorno_esta_documentada` escaneaba solo `src/flujo`, asi que `cultura/` y `tools/` -- donde viven Hub, Research y Codex -- escapaban a la regla: 82 variables medidas al ensanchar. Como documentar 82 de golpe no es verificar, las zonas anchas quedan con un pin que solo puede bajar (`tests/fixtures/env_documentado_baseline.txt`), el mismo patron que el ratchet de idioma. `--write` lo reescribe a proposito. Consumidor: `tests/test_mapa_completo.py` | 2026-08-21 |
| `update_readme_svg.py` | VIVO | deterministic README -> `arte-ascii-readme.svg` text-layer refresh; preserves the artwork shell, exposes `--check` for stale-cover detection, and is consumed by `tests/test_readme_svg.py` | 2026-08-06 |
| `becas_calendario.py` | VIVO | RD becas, area operativa | 2026-07 |
| (las 33 utilidades del buzon `mak`) | LEIDAS 2026-08-01, NO ENTRAN | Llevaban dias en la rama `mak` sin que nadie las abriera, porque el muro que las describia decia que main ya las habia rechazado y era falso (ver `context/LAST_HANDOFF.md`). Leidas una por una: **9 invocan `subprocess`** para ejecutar `backlog_codex`, tocar `/etc` o instalar cron jobs -- son ORDENES OPERATIVAS disfrazadas de utilidad, justo lo que el clasificador de rutas de #406 salio a frenar. **~10 son de sandbox** por debajo de 1 KB ("Script de ejemplo para el sandbox", 406 bytes). **3 traen surrogates invalidos** (\udc81, \udc8f): no son UTF-8 y revientan al leerlas, pero PASARON el gate de MAK porque `revisor.gate_compila` compila el texto ya decodificado en la caja -- ese gate es ciego al encoding, y ese es el hallazgo que deja la lectura. Y **4 sirven** (OSC 1.0 con `struct`, verificador de puertos TCP, estadistica de columna CSV, validador JSON), probadas corriendo. Se trajeron al repo y se devolvieron el mismo dia: renombrarlas rompio `test_capataz_enrutamiento`, que usa los NOMBRES de esa carpeta como fixture de los pedidos reales que causaron el defecto, y sus comentarios en castellano encienden el ratchet de idioma. Sin consumidor no compensaban ninguna de las dos cosas. Lo que valia era saber que hay adentro, y eso queda escrito aca | 2026-08-01 |
| `idioma.py` | VIVO | measures the language of comments/docstrings in every tracked `*.py` (es/en/mixed/none, transparent stdlib heuristic, `git ls-files` only, archive and vendorized zones excluded); measured consumer: `tests/test_idioma_ratchet.py`, the ratchet that pins `tests/fixtures/idioma_baseline.txt` so no NEW file adds Spanish comments while renames are never demanded; real run 2026-07-31: 581 files = 388 es + 96 en + 38 mixed + 59 none; also prints a soft FYI of widespread Spanish identifiers missing from `docs/GLOSSARY.md` | 2026-07-31 |
| `render_flyer_mak.py` | VIVO | workflow MAK image/poster -> `RD.blend` -> PNG | 2026-08-18 |
| `render_video_sequence_mak.py` | VIVO | workflow MAK video -> `RD.blend` -> PNG sequence + manifest | 2026-08-18 |
| `aep_reference_scan.py` | VIVO | read-only RIFX/After Effects reference inventory; project -> declared footage paths, never `RENDERS_TO`; consumed by `tests/test_aepfile.py` | 2026-08-24 |
| `blender_scene_probe.py` | VIVO | read-only Blender background fallback for `.blend` decoder limits; scene -> declared render paths, never renders/saves/`RENDERS_TO`; consumed by `tests/test_blender_scene_probe.py` | 2026-08-24 |
| `compete_engine.py` | VIVO | proyecto tapiz (cultura) | 2026-07 |
| `comparar_cobertura_fichas.py` | VIVO | compara dos pasadas de `percepcion.py` campo a campo SOBRE LOS MISMOS ids (lo que no esta en ambas no se cuenta) y filtra por `medicion.vision.motor`, para que una pasada con fallback no le acredite a watsonx lo que respondio ollama; corrida real 2026-08-01 sobre 923 fichas ig, v1 gemma3 vs v4 watsonx: `tipo_obra` 51.9%->100%, `materiales` 68.7%->99.6%, `colores` 95%->100%, y la unica caida real `oportunidad_codigo` 99.1%->75.9% (watsonx omite la clave en 225 imagenes; ninguna de las dos pasadas era plantilla: 1258 y 640 valores distintos) | 2026-08-01 |
| `consolidar_fichas.py` | VIVO | mete una pasada nueva de `percepcion.py` en el `fichas.jsonl` vivo sin perder lo que la vieja sabia: la fusion es CAMPO A CAMPO porque el reemplazo por fila destruye datos medidos -- la pasada de watsonx llena `tipo_obra` del 67% al 100% pero deja `oportunidad_codigo` vacio en 225 imagenes donde el modelo chico habia escrito una. La mezcla se DECLARA en `medicion.vision.heredado` + `motor_heredado`: una ficha con campos de dos motores y sin registro de cual vino de cual es peor que cualquiera de las dos pasadas sola. Ensayo por defecto; `--aplicar` respalda con sello de tiempo, escribe a un temporal y lo valida ANTES de pisar el vivo. Ensayo real 2026-08-01 sobre 3.138 fichas: 1.354 fichas reemplazadas, 1.482 campos mejorados, 397 heredados, **9.348 pisados (4.595 de ellos quedando MAS CHICOS)** y 0 que queden vacios habiendo tenido valor. Ese cuarto numero es el que faltaba: la primera version contaba tres casos sobre un test de PRESENCIA y cubria 1.879 de 17.602 decisiones, imprimiendo `campos perdidos: 0` como compuerta -- un cero que solo podia dar cero. Lo encontro una revision adversarial midiendo el archivo real, no un fixture. La atribucion es POR CAMPO (`heredado: {campo: motor}`) porque un motor por ficha pierde el rastro en la segunda fusion, y `comparar_cobertura_fichas.py` ya no cuenta como llenos los campos heredados: sin eso, medir el archivo fusionado le acreditaba a watsonx el 100% de `oportunidad_codigo` cuando lo real es 77,9%. Escribir exige que NO haya percepcion corriendo (`pgrep`) y toma `flock`: una ficha apendeada en la ventana desaparece del vivo y queda marcada en `procesados.txt`, que es lo unico irreversible de la operacion | 2026-08-01 |
| `ig_metadatos.py` | VIVO | consumidor medido: `percepcion.py correr --meta-ig`, que mete el texto del artista en el prompt de vision. Saca del export de Instagram el mapa archivo -> {fecha, texto}. Medido sobre el export real 2026-08-01: 1.125 archivos mapeados, 1.014 con texto propio (90%), 1.125 con fecha exacta, rango 2018-11-29 a 2026-06-16; casan 1.124 de las 1.401 fichas ig (80%). Repara el mojibake del export (Instagram escribe UTF-8 y el export lo decodifica como latin-1: `coleccion` llega como `colecciA3n`) quedandose con la version de MENOS marcas, y lo que no pudo recuperar lo marca en vez de entregarlo como si estuviera bien. Lee SOLO `your_instagram_activity/media/`: al lado viven mensajes privados, likes e interacciones de historias, y toda ruta que pase por ahi se rechaza por nombre; `tests/test_ig_metadatos.py` | 2026-08-01 |
| `conversacion.py` | VIVO | tercer hermano de `arqueologia.py` (historial de git) y `esfuerzo.py` (costo de un informe): lee las transcripciones de `~/.claude/projects/` como corpus. Nadie las escribio para eso, y contienen lo unico que el repo no tiene -- lo que el usuario decidio, ordeno y tuvo que repetir. Consumidor medido: `clasificar` usa la cadena activa Groq/Gemini/Ollama y `citar` recupera la cita TEXTUAL por indice, porque una decision parafraseada deja de ser la decision. Corrida real 2026-08-01 sobre 126 sesiones: 17.629 turnos con texto, de los cuales **3.094 escritos por un humano** (0,7 MB) contra 12.197 del asistente (5,6 MB); 39,2 MB del corpus son `tool_result` y no entran. Dos defectos propios encontrados MIDIENDO, no leyendo: (1) la primera version decidia por una lista de prefijos escrita a mano quien era humano, la lista dejo de coincidir con la realidad y los resumenes de compactacion se comieron los 30 primeros puestos -- ahora lo dice `origin.kind`, que el registro ya trae; (2) los lotes se dimensionaban por la ventana de ENTRADA (95k) y los 3 primeros lotes agotaron los 8.000 tokens de SALIDA devolviendo JSON cortado, asi que el tope real es la salida. Un lote sin JSON legible se cuenta como FALLO y nunca como lista vacia. El hallazgo que no cuesta un token es la repeticion entre sesiones DISTINTAS: `users issvk downloads` en 13, `claude teleport session` en 9, `compileall src flujo`/`pytest tests`/`flujo verify` en 6, `api key nvidia` en 6 -- constantes que hay que re-pegar cada sesion porque no estan escritas | 2026-08-01 |
| `inferential_archaeology.py` | VIVO | read-only cross-source index for authorship, proposals, direct mutation evidence, Git path history, hotspots, and possibility lanes; consumed by the archaeology focused tests and ignored evidence packet under `out/archaeology/` | 2026-08-13 |
| `drenar_material.py` | VIVO | vacia `~/plataforma/material.jsonl` en paralelo mientras dure la ventana pagada -- `trabajo.py` saca UNA tarea por invocacion y corre por cron, o sea meses para 2.730 tareas. Escribe a su propio directorio y NO a la base de RD: una productora identificada por un modelo es un candidato, no un cliente. Lo pausado o fallido VUELVE a pendiente (una cola que se vacia sin haber trabajado es la peor forma de decir que termino) y aborta el lote entero si se acumulan pausas por ceguera. Informa la DISTRIBUCION, no un total: "412 hechas" no dice nada, "412 hechas, 180 con productora y fuente, 190 NO SE ENCONTRO, 42 pausadas ciegas" si. Corrida real 2026-08-01: 8 tareas, 7,6 s cada una con 4 hilos | 2026-08-01 |
| `gen_archivo_iskvw.py` | VIVO | genera `iskvw/datos/archivo.json`, el contrato piezas+vinculos; consumidor confirmado via `.github/workflows/publicar_iskvw.yml`. Desde 2026-08-05 `--fuente todo` es el sustrato publico limpio: 446 piezas y 237 vinculos en medicion local, sin mezclar los ensayos de research; `--fuente ensayos` o `--fuente todo --incluir-ensayos` trae deliberadamente la vista de research ilustrado (33 piezas y 32 vinculos adicionales: informe, conceptos e iconos). La conversion micelio->contrato vive en `cultura/mak_plataforma/contrato_archivo.py` desde 2026-07-29, compartida con `GET /api/archivo` del hub de MAK. Ese workflow corre en `ubuntu-latest` y nunca alcanza la caja (LAN privada), asi que los vinculos de micelio llegan solo por snapshot `iskvw/datos/micelio.json`, empujado por `cultura/mak_plataforma/entregar_micelio.py` corriendo EN la caja; hard-falla (exit 1, nada escrito, ningun PR) si el micelio no responde o devuelve 0 vinculos -- una ausencia nunca se vuelve un cero plausible. `tests/test_contrato_archivo.py`, `tests/test_gen_archivo_iskvw.py`, `tests/test_entregar_micelio.py` | 2026-08-05 |
| `gen_propuestas_rd.py` | VIVO | el ultimo salto a la base RD: alimenta el escritor de borradores de `mineria_rd.py` desde `docs/rd/candidatos_curatoria/candidatos_db.jsonl` (ya digerido por `extraccion_db`), sin OCR ni GPU; re-matchea contra los catalogos ACTUALES, reporta dudosos sin proponerlos y exige evidencia >= 2; los borradores salen a una carpeta aparte y entran solo por PR humano; `tests/test_gen_propuestas_rd.py` | 2026-07-29 |
| `repo_audit.py` | VIVO | gate read-only de grafo web, referencias activas obsoletas y contratos de las SQLite locales; consumidor `.github/workflows/ci.yml`, `Makefile audit` y `tests/test_repo_audit.py` | 2026-08-21 |
| `verify_learning_hashmaps.py` | VIVO | verifica en solo lectura los mapas hash de aprendizaje contra el arbol MAK completo; distingue referencias con hash de referencias solo por ruta y nunca reescribe mapas ni fuentes. Consumidor: operador y validacion de continuidad | 2026-09-02 |
| `gen_dashboard_productoras.py` | VIVO | genera `db_productoras.html`; documentado en `docs/rd/DB_PRODUCTORAS_ESTADO.md`; consume la salida de `triangular_fichas.py` | 2026-07-25 (llega a main con la promocion de `rd`, PR #303) |
| `gen_presentacion_db.py` | VIVO | genera `docs/rd/presentacion_db.html`, la pieza formal para la directiva RD; documentado en `docs/rd/DB_PRODUCTORAS_ESTADO.md` | 2026-07-25 (llega a main con la promocion de `rd`, PR #303) |
| `gen_propuesta_directiva.py` | VIVO | genera `docs/rd/propuesta_directiva.html`, la propuesta a la directiva (que ofrece RD, con que cuenta, como protege los datos y que necesita aprobar); lee `data/rd.db`, asi que ninguna cifra se escribe a mano | 2026-07-26 |
| `vendorizar_iskvw.py` | VIVO | empaqueta librerias npm como modulos ESM autocontenidos + su README al lado, para paginas estaticas que no pueden depender de un CDN ni de un build. DOS manifiestos: `data/iskvw_librerias.json` -> `iskvw/piel/lib/` (4 de thi.ng) y `data/motor_librerias.json` -> `docs/cultura/lib/` (hiccup, hiccup-svg, color, para el compilador de navegador del motor semantico). `tests/test_iskvw_librerias.py` las importa en node y les pide trabajo; `tests/test_thing_registro.py` cruza los manifiestos con la seccion 6. Dos arreglos 2026-07-30: `--destino` se resuelve absoluto (esbuild corre en un temporal y perdia el bundle) y el chequeo de huerfanos solo mira bundles vendorizados (los `.js` escritos a mano en el destino se reportaban como sobrantes) | 2026-07-30 |
| `iskvw_piel_smoke.mjs` | VIVO | ejecuta el JS real de la piel del campo en node con stubs de DOM, recorre el campo para que el codigo por-nodo corra de verdad, y sale distinto de cero ante cualquier error (incluidos los async); existe porque #403 dejo `destino`/`dy` fuera de scope y todo pytest siguio verde con el portafolio muerto en el primer frame; consumido por `tests/test_iskvw_piel_smoke.py`. Desde el patch de efectos tambien lo MIDE: arranca la piel tres veces -- sin `iskvw/datos/tablero.json`, con el tablero publicado (llave maestra apagada) y con la llave encendida -- y exige que las dos primeras dibujen marca por marca lo mismo y que la tercera deforme de verdad (posiciones desplazadas, colores corridos, la lectura arrastrada por la gravedad). Ademas corre cada llave por-efecto A SOLAS y exige la firma que solo ese efecto deja, y verifica que la capa de sala (`mejoras.venue3d`, mismo fetch del tablero) aparezca exactamente cuando la llave lo dice. Una llave que se publica apagada es codigo que nadie mira: por eso se mide en CI y no se declara | 2026-07-31 |
| `validar_curaduria.py` | VIVO | valida `iskvw/datos/curaduria.json` (y `tablero.json`) contra el esquema que lee `aplicar_curaduria()` y contra el archivo real en disco: ids desconocidos o duplicados, campos invalidos, svg firmado ausente, diacriticos mutilados (la clase de defecto "reduciendo ano") -- todo lo que el consumidor traga en silencio, dicho en voz alta antes de commitear. Salida medida (ERROR/AVISO), exit 1 con errores: sirve en CI. Consumido por `tests/test_validar_curaduria.py` (que ademas corre el CLI sobre los archivos reales del repo) y `tests/test_curaduria_roundtrip.py` | 2026-07-31 |
| `gen_vinculos_iskvw.py` | VIVO | vinculos entre obras CON EL MOTIVO adentro, sacados de los conceptos que la percepcion extrajo y que nadie usaba (7.985 menciones). `gen_archivo_iskvw.py` vincula por etiqueta compartida y lo declara: "nadie midio que se parezcan, comparten una palabra"; esto declara `clase: concepto` y lista los conceptos compartidos en `porque`, asi que el vinculo se puede refutar. Medido antes de escribirlo: 1 concepto compartido da 31.992 pares sobre 1.359 obras (una maraña), 2 dan 1.851 vinculos que alcanzan 863 obras (64%). Tres exclusiones, todas CONTADAS y reportadas -- conceptos en una sola obra (819, no vinculan nada), los mas frecuentes (uno en 305 obras es una CATEGORIA) y los que pasan `--tope-obras`. El pliegue de plural/tilde es para AGRUPAR: `porque` muestra la grafia que el modelo escribio, porque `patrone geometrico` es una llave y no una palabra. `tests/test_vinculos_iskvw.py` | 2026-08-01 |
| `route_idea.py` | VIVO | CLI que convierte una idea o incidente en un packet minimo por area; consume `flujo.diagnostics.route_idea` y evita que un agente externo tenga que leer todo el repo; `tests/test_diagnostics.py` | 2026-08-16 |
| `interpretive_garden_workflow.py` | VIVO | construye el modelo SQLite y los reportes derivados del laboratorio de investigacion; conserva fuentes, claims, entidades, relaciones, semantica y procedencia sin llamar APIs | 2026-08-17 |
| `research_job_router.py` | VIVO | convierte una pregunta en un job persistente por dominio (plantas, VJ, curatoria, RD o portafolio), con pasos semanticos, politica de proveedores y plan Markdown/JSON; consumido por MAK 8900 | 2026-08-17 |
| `execute_research_job.py` | VIVO | ejecuta discovery/capture acotado para un job, separa candidatos de fuentes oficiales, registra hashes, estados, licencia y creditos estimados; no llama modelos | 2026-08-17 |
| `gen_capas_iskvw.py` | VIVO | corre las capas de `data/iskvw_capas.json` sobre `iskvw/datos/campo.json` y deja un dato medido por obra (hoy `tilde`, el residuo diacritico de lo percibido via `tools/tilde_meter.py`, y `trazo`, la densidad del vector); sumar una capa es una entrada mas y una funcion, sin tocar la piel; `tests/test_capas_iskvw.py` | 2026-07-27 |
| `gen_campo_iskvw.py` | VIVO | genera `iskvw/datos/campo.json`, las posiciones del campo de iskvw; proyecta los embeddings del micelio de MAK con t-SNE (48.9% de vecindad conservada, medido contra PCA 3.8% y fuerzas 16.4%) y toma que tipos entran de `data/iskvw_campo_filtro.json`; consumido por `iskvw/piel/campo/index.html` | 2026-07-27 |
| `gen_iskvw_prototipo.py` | VIVO | genera `docs/iskvw/prototipo.html`, el prototipo del portafolio ISKVW; lee `tools/portfolio/proyectos.json` y mide el repo al generar, sin telemetria decorativa | 2026-07-26 |
| `triangular_fichas.py` | VIVO | triangula `fichas.jsonl` de MAK en eventos + productoras candidatas; consumido por `gen_dashboard_productoras.py` y `gen_presentacion_db.py` | 2026-07-25 (llega a main con la promocion de `rd`, PR #303) |
| `gen_mapa_comandos.py` | VIVO | genera el bloque de comandos de `MAPA.md`; `tests/test_mapa_completo.py` exige que el mapa cubra todo el CLI | 2026-07-25 |
| `construir_mapa_visual.py` | VIVO | builds a bounded visual contact sheet from declared portfolio media; used by the MAK visual review workflow and kept separate from public promotion | 2026-08-08 |
| `verificar_piel_honesta.mjs` | VIVO | sonda de navegador real (headless, nunca una ventana) para las cuatro afirmaciones de la piel campo que el 2026-07-30 se vendieron mas fuertes que su evidencia: el gesto de quedarse quieto nunca se ejercito de verdad, las letras doublecup nunca se VIERON, el regimen industrial nunca se manejo desde el ARCHIVO, y los fps nunca se tomaron en el estandar declarado (viewport de telefono, CPU x4). Consumidor: el operador antes de afirmar cualquiera de las cuatro; no es test de CI porque necesita el sitio servido. `playwright-core` NO es dependencia del repo -- se resuelve por `PLAYWRIGHT_CORE` o instalacion normal, y sin el la herramienta dice como instalarlo en vez de morir | 2026-07-31 |
| `iconos_conjunto.py` | VIVO | valida y construye la galeria de un CONJUNTO de iconos (`--raiz`, sirve a cualquiera, no solo al del ensayo rave); consumidor medido: `docs/cultura/ensayos/rave/` (16 iconos, 0 errores) y el anexo iconografico que exige `docs/cultura/FORMATO_ENSAYO.md`; `tests/test_iconos_conjunto.py` | 2026-07-30 |
| `gen_vocabulario_motor.py` | VIVO | exporta el vocabulario del motor semantico (22 figuras/12 gestos/9 tonos) a `docs/cultura/lib/vocabulario.json` para que el MISMO spec compile en el navegador sin re-portar la geometria a mano; consumidor: `docs/cultura/lib/compilador.js` + el taller de la galeria; `--verificar` falla si quedo viejo respecto de `vocabulario.py`; `tests/test_compilador_navegador.py` | 2026-07-30 |
| `render_video_rd.py` | LEGACY/MANUAL-ONLY | pipeline histórico H264 sobre `RD.paravideo.blend`; no es la ruta productiva MAK | 2026-08-18 |
| `system_map.py` | VIVO | mapa mecanico del repo (soporte de `contexto_repo.py`) | 2026-07 |
| `tapiz_telemetry.py` | VIVO | imported directly by `tests/test_compete_engine.py` (`TestLiveTelemetry`: `import tapiz_telemetry as tt`, exercises `build_live_ecosystem`, `_is_excluded`, `_path_excluded`); its `--live` output was rendered into the checked-in artifact `projects/tapiz/piezas_curadas/field_telemetry.svg` | 2026-08-29 |
| `tilde_meter.py` | VIVO | `projects/cultura/tilde_paridad.py` + `tests/test_tilde_meter.py` + `tests/test_tilde_render.py`; area Cultura de CLAUDE.md | 2026-07-25 (movido de desktop/ en la poda de stack muerto) |
| `venue_geometria_scd.py` | VIVO | genera la sala DEMO `data/venues/scd-plaza-egana.json` (derivada del modelo radial de `projects/plano/referencia_plano_teatro.py`) que abre por defecto el visor `iskvw/piel/venue/`; `tests/test_venue.py` verifica que el archivo del repo sea lo que imprime el generador | 2026-07-30 |
| `audit_blend_scene.py` | VIVO | registered in `src/flujo/knowledge/project_router.py` TOOL_CATALOG as `blend_scene_audit` (mode read_only); `src/flujo/knowledge/episode_runner.py` builds the actual Blender invocation command when that tool_id is selected; part of the four-script Blender-audit family statically reviewed 2026-08-19 (`context/LAST_HANDOFF.md` Phase 594: AST parses clean, no destructive save ops) | 2026-08-29 |
| `bake_static_materials.py` | VIVO | part of the same Blender-tools family, statically audited 2026-08-19 (`context/LAST_HANDOFF.md` Phase 594: writes only to `--output`, source `.blend` never saved); an earlier handoff entry, rotated out of the live file and recovered at `/home/mak/.local/share/Trash/files/flujo/context/LAST_HANDOFF.md:13251`, records an actual run: `blender -b RD.blend --python tools/bake_static_materials.py -- --output RD.baked-static.v1.blend --resolution 2048` | 2026-08-29 |
| `build_application_intake.py` | VIVO | registered in `src/flujo/knowledge/project_router.py` TOOL_CATALOG as `project_intake`; imported directly by `tests/test_project_reconstruction.py` (`from tools.build_application_intake import select_candidates`); listed as a `data/mak_knowledge.db` consumer in the CI-checked graph of `tools/repo_audit.py` | 2026-08-29 |
| `build_effort_consumer_crosswalk.py` | VIVO | executed against a temporary SQLite database 2026-08-19 (`context/LAST_HANDOFF.md` Phase 595): exit 0, `database_mutated=0` | 2026-08-29 |
| `build_mak_knowledge_db.py` | VIVO | dynamically loaded via `importlib.util.spec_from_file_location` in `tests/test_knowledge_scanner_skips.py` to test `is_virtual_environment`/`should_skip_dir`; also executed 2026-08-19 against a fixture database (`context/LAST_HANDOFF.md` Phase 595: exit 0, 2 fixture files indexed) | 2026-08-29 |
| `build_mak_canonical_map.py` | VIVO | operator-run filesystem measurement; writes only `/home/mak/indexes/mak-canonical-20260829/mak-canonical-map.json`, with protected and runtime-only roots explicitly recorded | 2026-08-29 |
| `compute_effort_residuals.py` | VIVO | executed 2026-08-19 against a temporary knowledge database (`context/LAST_HANDOFF.md` Phase 595): exit 0, valid empty reports with `integrity=ok` | 2026-08-29 |
| `gen_animadas_obras.py` | VIVO | imported directly by `tests/test_gen_animadas_obras.py` (`sys.path.insert` + `from gen_animadas_obras import TONO_POR_COLOR, derivar_spec`); its output feeds `contrato_archivo.desde_animadas` | 2026-08-29 |
| `mak_status.py` | VIVO | listed as a `data/mak_knowledge.db` consumer in the CI-checked graph of `tools/repo_audit.py`; operator CLI `tools/mak_status.py --db data/mak_knowledge.db --json` run and measured (`context/LAST_HANDOFF.md`: 11 components, exit 0); same contract as `GET /api/status` | 2026-08-29 |
| `optimize_blend_scene.py` | VIVO | part of the Blender-tools family, statically audited 2026-08-19 (`context/LAST_HANDOFF.md` Phase 594: no destructive save, writes only to `--output`); documented usage `blender -b RD.blend --python tools/optimize_blend_scene.py -- --output ...` | 2026-08-29 |
| `profile_blender_animation.py` | VIVO | part of the Blender-tools family, statically audited 2026-08-19 (`context/LAST_HANDOFF.md` Phase 594); an earlier handoff entry, recovered at `/home/mak/.local/share/Trash/files/flujo/context/LAST_HANDOFF.md:13332`, records an actual run: `blender -b RD.blend --python tools/profile_blender_animation.py -- --frames 1 50 75` | 2026-08-29 |
| `project_gate.py` | VIVO | the CLI that ties `flujo.knowledge.project_router`, `episode_runner` and `project_api` together; operator-run and measured (`context/LAST_HANDOFF.md`: "Tennis Project IR probe", route selects the tennis consumer, probe status `succeeded`) | 2026-08-29 |
| `project_lanes.py` | VIVO | imported directly by `tests/test_project_lanes.py` (`from tools import project_lanes`); operator CLI `summary`/`validate` run and measured (`context/LAST_HANDOFF.md`, `knowledge/README.md`: 19 lanes, exit 0) | 2026-08-29 |
| `project_learning.py` | VIVO | operator CLI run and measured against `data/mak_knowledge.db` (`context/LAST_HANDOFF.md`: 8 eligible in 4 projects, `status=abstain`, no independent holdout); `--record-result` path also documented | 2026-08-29 |
| `reconcile_garden_knowledge.py` | VIVO | executed 2026-08-19 against the real garden and knowledge databases (`context/LAST_HANDOFF.md` Phase 595): exit 0, `hash_match=1`, both integrity checks `ok`, 40 URLs, 22 claims, 12 tools; report written to a temporary path only | 2026-08-29 |
| `research_source_capture.py` | VIVO | registered in `src/flujo/knowledge/project_router.py` TOOL_CATALOG as `research_source_capture` (mode plan_only, output `source_capture`) | 2026-08-29 |
| `triangulate_project_context.py` | VIVO | operator CLI documented and run (`docs/GLOSSARY.md`, `context/LAST_HANDOFF.md`); wraps `flujo.knowledge.project_context`, whose graph is served read-only by both hubs at `/api/project/context` | 2026-08-29 |

Nota: el director listo tambien `render_flyer_mak.py` (VIVO, mak_ops) en
su mensaje de spec, pero ese archivo NO existe en `tools/` de este
worktree (ni en ninguna ruta del repo, verificado con busqueda global) --
omitido de la tabla, ver desvio reportado en el cierre de sesion.

## 5-ter. Manual-only overlay (reconciled with generated measurement 2026-08-31)

The current MAK consumer graph searched these top-level tools by filename, bare
module name, and dynamic-loading context across `flujo/` and the seven organ
roots. It does not recurse into remote rclone mounts, archive/history, or
`curatoria_inbox`. This is an interpretation overlay, not a second inventory.
The generated `mak-tool-consumer-inventory-v1` output is the measurable source;
this table keeps the operator explanation for the 32 entries without a direct
reference. No-reference is not tool death: the
consumer may be an operator-run command, Blender invoked by an operator, or a
wrapper contract. The overlay never grants permission to retire a file by name
alone.

| file | consumer kind | measured interpretation |
|---|---|---|
| `aep_reference_scan.py` | manual-only | operator CLI; tests exercise the RIFX reader contract |
| `drenar_material.py` | manual-only | operator-only bounded queue drain; writes only to its explicit output and queue paths |
| `ig_metadatos.py` | manual-only | operator metadata report over a published Instagram export; optional explicit output |
| `medir_test_overlap.py` | manual-only | read-only AST-shape overlap report; never edits tests or production files |
| `medir_tests.py` | manual-only | read-only test chronology/count report from Git history |
| `build_mak_canonical_map.py` | manual-only | operator measurement; current output is the canonical physical MAK map |
| `bake_static_materials.py` | manual-only | operator invokes the Blender CLI; no in-tree caller |
| `build_effort_consumer_crosswalk.py` | manual-only | operator report CLI; temporary database run |
| `compile_contracurator.py` | manual-only | CLI wrapper; Hub/tests consume the wrapped contract |
| `compute_effort_residuals.py` | manual-only | operator report CLI; temporary database run |
| `execute_research_job.py` | manual-only | operator discovery/capture CLI; no automatic dispatch |
| `gen_dashboard_productoras.py` | manual-only | operator static-document generator |
| `gen_iskvw_prototipo.py` | manual-only | operator static-prototype generator |
| `gen_presentacion_db.py` | manual-only | operator static-document generator |
| `optimize_blend_scene.py` | manual-only | operator invokes the Blender CLI; no in-tree caller |
| `profile_blender_animation.py` | manual-only | operator invokes the Blender CLI; no in-tree caller |
| `project_gate.py` | manual-only | operator route/probe CLI; Hub consumes the underlying API |
| `project_learning.py` | manual-only | operator learning CLI; result recording is explicit |
| `reconcile_garden_knowledge.py` | manual-only | operator reconciliation report CLI |
| `substrate_experiment.py` | manual-only | operator-run preregistered experiment |
| `triangulate_project_context.py` | manual-only | operator context CLI; Hub consumes the underlying graph |


## 5-quater. Herramientas que salieron a FLUJO (separacion 2026-09-02)

Causa: la separacion fisica de MAK y FLUJO movio la cadena de portafolio,
oportunidades y render a `/home/mak/flujo/tools/`. El registro de MAK las
seguia declarando, asi que `test_registro_sin_herramientas_fantasma` media 35
fantasmas y un agente que buscara `compile_ssd_order_foundation.py` en esta
rama concluia que no existe. No estan muertas: cambiaron de rama.
Verificado el 2026-09-02: las 35 existen en `flujo/tools/` y ninguna en
`tools/`. Su registro vive en `flujo/CAPACIDADES.md`, no aqui.
Retiro de esta seccion: cuando el registro se genere desde el arbol.

- `adapt_practice_receipts.py` -> `flujo/tools/adapt_practice_receipts.py`
- `archive_observer.py` -> `flujo/tools/archive_observer.py`
- `arica01_portfolio.py` -> `flujo/tools/arica01_portfolio.py`
- `build_evidence_return.py` -> `flujo/tools/build_evidence_return.py`
- `build_possibility_field.py` -> `flujo/tools/build_possibility_field.py`
- `certified_query.py` -> `flujo/tools/certified_query.py`
- `classification_review.py` -> `flujo/tools/classification_review.py`
- `compile_application_research_package.py` -> `flujo/tools/compile_application_research_package.py`
- `compile_autonomy_plan.py` -> `flujo/tools/compile_autonomy_plan.py`
- `compile_cross_archive_relations.py` -> `flujo/tools/compile_cross_archive_relations.py`
- `compile_cross_archive_research_frontier.py` -> `flujo/tools/compile_cross_archive_research_frontier.py`
- `compile_portfolio.py` -> `flujo/tools/compile_portfolio.py`
- `compile_practice_evidence_state.py` -> `flujo/tools/compile_practice_evidence_state.py`
- `compile_product_episode.py` -> `flujo/tools/compile_product_episode.py`
- `compile_ssd_order_foundation.py` -> `flujo/tools/compile_ssd_order_foundation.py`
- `deep_learning_gate.py` -> `flujo/tools/deep_learning_gate.py`
- `evaluate_artistic_program_hypotheses.py` -> `flujo/tools/evaluate_artistic_program_hypotheses.py`
- `evaluate_opportunity_fit.py` -> `flujo/tools/evaluate_opportunity_fit.py`
- `evaluate_product_learning.py` -> `flujo/tools/evaluate_product_learning.py`
- `gen_rd_standalone.py` -> `flujo/tools/gen_rd_standalone.py`
- `import_project_reconstruction.py` -> `flujo/tools/import_project_reconstruction.py`
- `materialize_pilot_run.py` -> `flujo/tools/materialize_pilot_run.py`
- `math_kernel.py` -> `flujo/tools/math_kernel.py`
- `project_reconstruction.py` -> `flujo/tools/project_reconstruction.py`
- `project_review.py` -> `flujo/tools/project_review.py`
- `render_output_edges.py` -> `flujo/tools/render_output_edges.py`
- `research_simulation.py` -> `flujo/tools/research_simulation.py`
- `run_archive_toolchain.py` -> `flujo/tools/run_archive_toolchain.py`
- `run_vision_feedback.py` -> `flujo/tools/run_vision_feedback.py`
- `show_asset_usage.py` -> `flujo/tools/show_asset_usage.py`
- `source_learning_bridge.py` -> `flujo/tools/source_learning_bridge.py`
- `tennis_mcp_ingest.py` -> `flujo/tools/tennis_mcp_ingest.py`
- `tennis_shot_events.py` -> `flujo/tools/tennis_shot_events.py`
- `venue.py` -> `flujo/tools/venue.py`
- `venue_screen_setup.py` -> `flujo/tools/venue_screen_setup.py`
## 5-bis. Snapshot histórico del registro medido (2026-08-28; superado)

La tabla de arriba declara el consumidor en prosa. Esta fue el primer chequeo
automático y se conserva como evidencia fechada, no como estado actual. La
salida vigente es el inventario generado `mak-tool-consumer-inventory-v1` de
`tools/repo_audit.py`; su proyección completa se guarda en
`/home/mak/state/codex-retomar-20260831/evidence/repo-audit-tools-20260831.md`
y se regenera con `.venv/bin/python tools/repo_audit.py --format markdown`.
La regla del 2026-07-25 sigue vigente: no se retira una herramienta sólo por
carecer de una referencia automática.

**Como se mide cada columna**

- `existe`: `tools/<archivo>` esta en el arbol.
- `refs produccion`: archivos fuera de `tests/` que mencionan la herramienta en
  `src`, `tools`, `cultura`, `scripts`, `Makefile`, `.github`, `iskvw`, `xio`.
- `refs test`: idem dentro de `tests/`.
- `disparador`: workflow de `.github/workflows/` que la nombra.

Se buscan formas explícitas por herramienta: `<nombre>.py` (invocación por ruta),
`tools.<stem>` y `import/from <stem>` (import de módulo). Se excluyen fixtures y
documentación; en Python se ignoran comentarios y docstrings, conservando
strings ejecutables de comandos. Buscar solo la primera fue un error medido en esta misma sesion:
daba 0 referencias para `agent_bootstrap.py`, que si tiene test, porque
`tests/test_agent_bootstrap.py` hace `from tools.agent_bootstrap import SCHEMA`.
La primera medicion de esta seccion reporto 24 herramientas sin referencia; con
las tres formas son 13.

**Que NO prueba esta tabla**

Cero referencias no es muerte. Varias de las 13 son CLI que una persona corre a
mano y que ningun automatismo va a ejercitar nunca: eso es exactamente lo que la
columna dice y nada mas. Lo que la tabla si prueba es que **4 de 92 herramientas
tienen disparador**, o sea que 88 solo corren si alguien tipea el comando.

**Resumen histórico (no usar para el estado actual)**

| | de 92 |
|---|---:|
| existen en `tools/` | 92 |
| con referencia en produccion | 46 |
| solo referenciadas por un test | 33 |
| sin ninguna referencia | 12 (13 medidos 2026-08-28; uno, `render_archaeology_deliverables.py`, fue retirado 2026-08-29) |
| **con disparador de workflow** | **4** |

Los 4 con disparador:

| herramienta | workflow | evento |
|---|---|---|
| `tools/render_flyer_mak.py` | `issue_descarga_ig.yml` | `issues` |
| `tools/render_video_sequence_mak.py` | `issue_descarga_ig.yml` | `issues` |
| `tools/gen_archivo_iskvw.py` | `ci.yml`, `publicar_iskvw.yml` | `push`/`pull_request`, `workflow_dispatch` |
| `tools/repo_audit.py` | `ci.yml` | `push`/`pull_request` |

Solo dos responden a la accion de una persona (abrir un issue), y son las dos del
render de flyers. Las otras dos son higiene de CI.

Las 12 sin ninguna referencia: `arica01_portfolio.py`,
`compile_contracurator.py`, `compile_ssd_order_foundation.py`,
`run_vision_feedback.py`, `show_asset_usage.py`, `substrate_experiment.py`,
`certified_query.py`, `classification_review.py`, `venue_screen_setup.py`,
`aep_reference_scan.py`, `execute_research_job.py`, `gen_iskvw_prototipo.py`.
`render_archaeology_deliverables.py` was one of the original 13 but was
retired 2026-08-29 (commit `1957d846`, moved to
`_archive/orden-limpieza-20260828/`); it no longer exists in `tools/` and the
detailed table below was already corrected (commit `3850ea74`) -- this prose
count was the one line that commit missed.

| archivo | existe | refs produccion | refs test | disparador |
|---|:-:|---:|---:|---|
| `tools/archive_observer.py` | si | 0 | 1 | -- |
| `tools/arica01_portfolio.py` | si | 0 | 0 | -- |
| `tools/build_evidence_return.py` | si | 1 | 2 | -- |
| `tools/build_possibility_field.py` | si | 1 | 3 | -- |
| `tools/compile_contracurator.py` | si | 0 | 0 | -- |
| `tools/compile_portfolio.py` | si | 1 | 2 | -- |
| `tools/compile_ssd_order_foundation.py` | si | 0 | 0 | -- |
| `tools/compile_application_research_package.py` | si | 1 | 3 | -- |
| `tools/compile_autonomy_plan.py` | si | 1 | 1 | -- |
| `tools/compile_opportunity_constraints.py` | si | 1 | 5 | -- |
| `tools/compile_portfolio_dossier.py` | si | 1 | 3 | -- |
| `tools/compile_practice_evidence_state.py` | si | 0 | 1 | -- |
| `tools/compile_product_episode.py` | si | 1 | 1 | -- |
| `tools/compile_product_plan.py` | si | 1 | 3 | -- |
| `tools/adapt_practice_receipts.py` | si | 0 | 1 | -- |
| `tools/capture_opportunity_validity.py` | si | 0 | 1 | -- |
| `tools/compile_cross_archive_relations.py` | si | 0 | 1 | -- |
| `tools/compile_cross_archive_research_frontier.py` | si | 0 | 1 | -- |
| `tools/compile_opportunity_delta.py` | si | 0 | 1 | -- |
| `tools/compile_selective_recompute_receipt.py` | si | 0 | 1 | -- |
| `tools/compile_vigia_capture_plans.py` | si | 0 | 1 | -- |
| `tools/inspect_operational_memberships.py` | si | 0 | 1 | -- |
| `tools/materialize_pilot_run.py` | si | 0 | 1 | -- |
| `tools/render_product_view.py` | si | 0 | 1 | -- |
| `tools/run_archive_toolchain.py` | si | 0 | 1 | -- |
| `tools/run_vision_feedback.py` | si | 0 | 0 | -- |
| `tools/compile_research_frontier.py` | si | 1 | 2 | -- |
| `tools/evaluate_artistic_program_hypotheses.py` | si | 0 | 1 | -- |
| `tools/evaluate_opportunity_fit.py` | si | 1 | 3 | -- |
| `tools/evaluate_product_learning.py` | si | 2 | 1 | -- |
| `tools/generate_artistic_program_hypotheses.py` | si | 1 | 5 | -- |
| `tools/triangulate_research_evidence.py` | si | 2 | 4 | -- |
| `tools/order_projection.py` | si | 0 | 1 | -- |
| `tools/resolve_identity_ties.py` | si | 1 | 1 | -- |
| `tools/show_asset_usage.py` | si | 0 | 0 | -- |
| `tools/substrate_experiment.py` | si | 0 | 0 | -- |
| `tools/substrate_scan.py` | si | 2 | 0 | -- |
| `tools/png_xmp_witness.py` | si | 0 | 1 | -- |
| `tools/certified_query.py` | si | 0 | 0 | -- |
| `tools/reconcile_iskvw_media.py` | si | 0 | 1 | -- |
| `tools/classification_review.py` | si | 0 | 0 | -- |
| `tools/project_review.py` | si | 0 | 1 | -- |
| `tools/env_baseline.py` | si | 0 | 2 | -- |
| `tools/venue_screen_setup.py` | si | 0 | 0 | -- |
| `tools/update_readme_svg.py` | si | 1 | 1 | -- |
| `tools/becas_calendario.py` | si | 1 | 2 | -- |
| `tools/idioma.py` | si | 0 | 3 | -- |
| `tools/render_flyer_mak.py` | si | 2 | 2 | issue_descarga_ig.yml |
| `tools/render_video_sequence_mak.py` | si | 1 | 1 | issue_descarga_ig.yml |
| `tools/render_output_edges.py` | si | 0 | 1 | -- |
| `tools/aep_reference_scan.py` | si | 0 | 0 | -- |
| `tools/blender_scene_probe.py` | si | 1 | 2 | -- |
| `tools/compete_engine.py` | si | 13 | 2 | -- |
| `tools/context_pack.py` | si | 1 | 1 | -- |
| `tools/comparar_cobertura_fichas.py` | si | 1 | 1 | -- |
| `tools/consolidar_fichas.py` | si | 3 | 2 | -- |
| `tools/ig_metadatos.py` | si | 3 | 0 | -- |
| `tools/conversacion.py` | si | 0 | 1 | -- |
| `tools/inferential_archaeology.py` | si | 1 | 1 | -- |
| `tools/drenar_material.py` | si | 0 | 1 | -- |
| `tools/gen_archivo_iskvw.py` | si | 11 | 8 | ci.yml, publicar_iskvw.yml |
| `tools/gen_propuestas_rd.py` | si | 2 | 3 | -- |
| `tools/gen_rd_standalone.py` | si | 0 | 1 | -- |
| `tools/repo_audit.py` | si | 2 | 1 | ci.yml |
| `tools/gen_dashboard_productoras.py` | si | 0 | 1 | -- |
| `tools/gen_presentacion_db.py` | si | 0 | 1 | -- |
| `tools/gen_propuesta_directiva.py` | si | 2 | 0 | -- |
| `tools/vendorizar_iskvw.py` | si | 0 | 4 | -- |
| `tools/validar_curaduria.py` | si | 3 | 2 | -- |
| `tools/gen_vinculos_iskvw.py` | si | 0 | 1 | -- |
| `tools/route_idea.py` | si | 0 | 1 | -- |
| `tools/interpretive_garden_workflow.py` | si | 4 | 0 | -- |
| `tools/research_job_router.py` | si | 7 | 0 | -- |
| `tools/execute_research_job.py` | si | 0 | 0 | -- |
| `tools/gen_capas_iskvw.py` | si | 0 | 2 | -- |
| `tools/gen_campo_iskvw.py` | si | 1 | 4 | -- |
| `tools/gen_iskvw_prototipo.py` | si | 0 | 0 | -- |
| `tools/triangular_fichas.py` | si | 3 | 1 | -- |
| `tools/gen_mapa_comandos.py` | si | 1 | 4 | -- |
| `tools/construir_mapa_visual.py` | si | 1 | 1 | -- |
| `tools/iconos_conjunto.py` | si | 4 | 2 | -- |
| `tools/gen_vocabulario_motor.py` | si | 0 | 2 | -- |
| `tools/render_video_rd.py` | si | 1 | 2 | -- |
| `tools/system_map.py` | si | 6 | 2 | -- |
| `tools/tapiz_live_loop.py` | si | 1 | 0 | -- |
| `tools/tapiz_telemetry.py` | si | 2 | 1 | -- |
| `tools/tilde_meter.py` | si | 5 | 6 | -- |
| `tools/token_budget.py` | si | 1 | 1 | -- |
| `tools/venue_geometria_scd.py` | si | 1 | 2 | -- |
| `tools/verify_all.py` | si | 0 | 1 | -- |

### Reproducir esta medicion

Desde `/home/mak/flujo`, para una herramienta:

```bash
grep -rIl --exclude-dir=__pycache__ -e 'agent_bootstrap.py' \
     -e 'tools.agent_bootstrap' src tools cultura scripts tests .github
grep -l 'agent_bootstrap' .github/workflows/*.yml
```

Si la fila de la seccion 5 dice VIVO y estas dos consultas devuelven vacio, la
fila afirma un consumidor que no existe. Esa es la contradiccion que esta
seccion hace visible sin que nadie tenga que leer 92 lineas de prosa.

### La misma medicion, repetida el 2026-08-31

No se corrige la de arriba: se fecha y se supera. Corrida con el mismo metodo
que declara la seccion "Reproducir esta medicion", tres dias despues.

| | 2026-08-28 | 2026-08-31 |
|---|---:|---:|
| herramientas en `tools/` | 92 | **137** |
| con referencia en produccion | 46 | **48** |
| solo referenciadas por un test | 33 | **41** |
| sin ninguna referencia | 13 | **48** |
| con disparador de workflow | 4 | **4** |

Los 4 con disparador: `gen_archivo_iskvw.py`, `render_flyer_mak.py`,
`render_video_sequence_mak.py`, `repo_audit.py`.

**Lo que el salto de 13 a 32 NO significa.** No es podredumbre: las 32
herramientas tienen explicación `manual-only` en la sección 5-ter. El número
también creció porque se escribieron más CLI
de uso manual —`medir_tests.py` y `build_mak_canonical_map.py` están entre ellas—
y porque la medición endurecida ya no cuenta comentarios, docstrings o fixtures
como consumidores.

Cero referencias no es muerte, y esta tabla lo dice desde el 28. Lo que hoy
confirma es lo mismo con otras cifras: **4 de 137 tienen disparador**, o sea 133
solo corren si alguien tipea el comando. Eso no es un defecto de MAK; es lo que
MAK es.

## 6. thi.ng / umbrella: LEER ANTES de escribir un generador, un pipeline o un grafo

Regla 2026-07-30 (causa: el usuario pidio thi.ng en varias sesiones seguidas y
al medirlo habia UNA sola libreria viva de cuatro vendorizadas, mientras la
sesion siguiente mandaba a escribir la misma capacidad desde cero. Retiro:
cuando cada fila EN USO tenga su test y ninguna quede en `candidata`).

thi.ng son ~350 paquetes de Karsten Schmidt (`https://thi.ng/#tags`), en
TypeScript; el umbrella vive hoy en `https://codeberg.org/thi.ng/umbrella`.
Hay una recomendacion externa priorizada de 15 para este repo. Esta tabla es el
estado REAL, medido, no la recomendacion:

| paquete | estado | donde, y que retira | senal |
|---|---|---|---|
| `@thi.ng/rstream-gestures` | **EN USO** | `iskvw/piel/campo/index.html` la carga con `import('../lib/gestos.js')`; trajo el pellizco multi-touch (antes: cuatro listeners y un solo dedo). Degrada a los listeners si no carga | 2026-07-27 |
| `@thi.ng/hiccup` + `@thi.ng/hiccup-svg` | **EN USO** | `docs/cultura/lib/compilador.js`: el gemelo de navegador del motor semantico arma el arbol SVG con `svg/group/rect/text` + `serialize`, en vez de concatenar strings. El taller de `docs/cultura/ensayos/rave/galeria.html` compila una spec sin Python y sin PC | 2026-07-30 |
| `@thi.ng/color` | **EN USO** | mismo compilador: el contraste WCAG lo calcula la libreria en vez de repetir la formula de luminancia a mano | 2026-07-30 |
| `@thi.ng/tsne` | **descartada con medicion** | no puede bajar 768 dimensiones a 2 (dim de salida = dim de entrada), asi que `tools/gen_campo_iskvw.py` sigue con sklearn. `tests/test_iskvw_librerias.py` fija el limite para que nadie lo reintente | 2026-07-27 |
| `@thi.ng/geom-trace-bitmap` | vendorizada, sin consumidor | imagen a vector de linea. El trazador vive en Python y ya esta afinado; solo paga si trazar se mueve al navegador | 2026-07-27 |
| `@thi.ng/distance-transform` | vendorizada, sin consumidor | campo de distancia, paso previo para engrosar/erosionar un trazo. Ninguna piel llego a ese paso | 2026-07-27 |
| `@thi.ng/graph` + `@thi.ng/rstream-graph` | **no adoptada: nombre por confirmar** | el micelio ya tiene una proyeccion en memoria en `cultura/mak_plataforma/contrato_archivo.py` y el Hub ahora expone el portafolio como `block/channel/connection`; `npm view @thi.ng/graph` devolvio 404 el 2026-08-09 y MAK no tiene Node. No se instala ni se reimplementa hasta identificar el paquete real | 2026-08-09 |
| `@thi.ng/transducers` | candidata, prioridad 2 | los pipelines de ingesta/curatoria (`mak_curatoria`, `extraccion_db`) como transformaciones composables | sin medir |
| `@thi.ng/validate` | candidata, prioridad 3 | limite de seguridad antes de persistir: metadatos de una pieza, config de un conjunto | sin medir |
| `@thi.ng/geom` | candidata | geometria 2D. Se solapa con las 22 figuras del vocabulario, que hoy son geometria a mano en Python | sin medir |
| `@thi.ng/fuzzy`, `@thi.ng/intervals`, `@thi.ng/rdom`, `@thi.ng/atom`, `@thi.ng/associative`, `@thi.ng/parse` | no evaluadas | busqueda tolerante, rangos de fechas, interfaz reactiva, estado, consultas anidadas, parsers | -- |

Como se agrega una: entrada en el manifiesto que corresponda
(`data/iskvw_librerias.json` para la piel de iskvw, `data/motor_librerias.json`
para el motor) y `py tools/vendorizar_iskvw.py --manifiesto <m> --destino <d>`.
Queda un ESM autocontenido con su README al lado: sin CDN, sin build, funciona
sin internet. `--destino` tiene que poder resolverse absoluto (esbuild corre en
un temporal).

Las dos reglas que esta tabla hace cumplir:

1. **No se escribe desde cero una capacidad que tiene fila aca.** Si la fila
   dice `candidata`, el trabajo es medirla y adoptarla o descartarla con
   numero -- no reimplementarla.
2. **Una libreria entra cuando retira trabajo escrito a mano, medido.** No por
   prioridad en una lista. `@thi.ng/tsne` es el ejemplo: prioridad alta en la
   recomendacion, descartada al medirla.
3. **Research SVG is an explicit lane.** If a future tool builds a research
   gallery, post proposal, laser/plotter seed, animation, or README-like ASCII
   SVG from MAK essays, it must call `gen_archivo_iskvw.py --fuente ensayos` or
   `--fuente todo --incluir-ensayos` deliberately. The public archive default
   stays clean; the research guarantee lane stays usable.

Lo que la recomendacion externa pide NO priorizar todavia: WebGL, shaders,
fisica, particulas, audio, simulacion, hardware, fabricacion digital.
