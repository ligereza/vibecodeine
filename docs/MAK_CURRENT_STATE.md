# Estado actual de MAK

> Fuente canónica de orientación para agentes y colaboradores. Leer primero
> `/home/mak/flujo/agents.md`, ejecutar `tools/agent_bootstrap.py`, luego este
> archivo y únicamente el paquete `Agent bootstrap — CURRENT` que emite el
> bootstrap. No recorrer el cuerpo histórico de `context/LAST_HANDOFF.md` para
> decidir el estado actual. Verificado el 2026-08-29.

Este documento consolida decisiones durables. No reemplaza la evidencia
histórica, no convierte cada experimento en una obligación y no afirma que una
credencial funcione solo porque existe en un archivo de entorno.

El traspaso estructurado de la consolidación local está en
`/home/mak/MAK_CODEX_HANDOFF.md`. Léelo junto con este estado; no crees otro
inventario paralelo.

## Consolidación local completada — 2026-08-29

MAK local significa `/home/mak`, no sólo `/home/mak/flujo`. En esta sesión se
consolidaron duplicados, proyecciones y placeholders con movimientos
reversibles bajo `/home/mak/_archive/orden-limpieza-20260828/`. `WIN`,
`curatoria_inbox`, Git como sistema de cambios, GoogleDrive/OneDrive y el repo
independiente XIO quedaron fuera del write-set.

El mapa físico actual es
`/home/mak/indexes/mak-canonical-20260829/mak-canonical-map.json`. El reporte
exacto registra 112 grupos, 300 filas y 188 rutas excedentes; no quedan grupos
de Python byte-identical. Los 100 `.py` externos son bridges de compatibilidad
hacia módulos canónicos y los 51 aliases activos son symlinks, no copias
físicas. Las decisiones detalladas están en
`/home/mak/indexes/mak-consolidation-20260829/MAK-DIRECTIVE-REGISTRY.md` y
`CONSOLIDATION-DECISIONS.md`.

El archivo de retiros tiene 234 filas, todas con destino existente y sin
duplicados de origen o destino. La suite completa termina con exit 0 y Git se
usó sólo en modo lectura para procedencia y validación.

La continuación del 2026-08-29 amplió el paquete actual con la reproducción de
CI en un entorno de dependencias declarado, pruebas directas de
`ingesta_archivo.py`, detalle estático de las 23 líneas de cron y el pulso JSON
`mak-organism-heartbeat-v1`. El mapa de retiros ahora tiene 234 filas; la
descripción precisa y los cambios pendientes de commit están en
`/home/mak/MAK_CODEX_HANDOFF.md` secciones 9 y 10. Esa apertura también
confirmó que `actions-runner` es runtime vivo de sistema; las raíces locales
restantes quedaron clasificadas sin crear inventarios paralelos ni tocar los
montajes externos.

## Reconciliación de autoridad y bases — 2026-08-27

La topología física actual y sus hashes están en
`/home/mak/indexes/mak-canonical-20260829/mak-canonical-map.json`.
`docs/system_learning/master/inventory.json:physical_organism_registry` queda
como registro de aprendizaje y evidencia histórica; el mapa causal de
conexiones está en `docs/system_learning/master/hashmap.json`. La autoridad
operativa queda fijada así:

```text
data/mak_knowledge.db  = memoria MAK transversal
data/rd.db             = proyección regenerable del catálogo RD
data/rd_datos.db       = frontera privada de datos RD
data/flujo.db          = índice de flyers FLUJO
research/...sqlite     = Research/capturas versionadas
labs/...sqlite         = índices y ejecuciones históricas
experiments/...sqlite  = evidencia de pilotos acotados
out/archaeology/...    = análisis histórico
```

Estas bases están conectadas por contratos, `artifact_ref`, `project_id`,
`requirement_id`, `evidence_ref`, hashes y consumidores declarados. No se
fusionan físicamente porque no comparten autoridad, privacidad ni ciclo de
vida. “Limpio” significa que cada una tiene clase, owner, consumidor y estado
visible; no significa eliminarla ni copiarla a una base universal.

## Reconciliación del organismo completo fuera de WIN — 2026-08-27

La frontera operativa de MAK es `/home/mak`, no sólo `/home/mak/flujo`.
`/home/mak/WIN` queda expresamente fuera por ser archivo histórico protegido;
`GoogleDrive` y `OneDrive` son montajes externos y no fueron recorridos. `WIN`
y `curatoria_inbox` son superficies protegidas. El registro físico canónico
actual es `/home/mak/indexes/mak-canonical-20260829/mak-canonical-map.json`;
su mapa causal especializado sigue siendo
`docs/system_learning/master/hashmap.json`.

El resumen del JSON contiene el conteo actual de entradas, archivos hashados,
bytes medidos y errores de lectura. Se regenera con
`python3 ~/flujo/tools/build_mak_canonical_map.py` y no sustituye las
mediciones de procesos o servicios.

La clasificación funcional por raíz queda así: `flujo` autoría e integración;
`plataforma`, `research`, `codex`, `lenguaje`, `curatoria`, `vigia` y
`xio_puente` órganos/runtime; `RD`, `portfolio_media`, `bucle` y `trazos`
producción; `indexes`, `labs`, `state`, `backups`, `_archive` y `renders`
referencias, snapshots o evidencia; `actions-runner`, `tools`, `src`, `apps`,
`models`, `blender`, `opt`, `go`, `venvs` y `venv-providers` soporte/vendor.
Las carpetas XDG (`Descargas`, `Documentos`, `Documents`, `Escritorio`,
`Imágenes`, `Música`, `Plantillas`, `Público` y `Vídeos`) se conservan como
espacio del usuario, no como almacenamiento MAK sin una clasificación interna.

La búsqueda SQLite acotada, con `-xdev`, encontró 270 archivos fuera de `WIN`:
85 pertenecen a superficies MAK y 185 son cachés del host/aplicaciones. Los
85 pasaron `integrity_check` en modo lectura; no se copiaron ni fusionaron.
`data/mak_knowledge.db` sigue siendo la memoria MAK transversal, pero las
réplicas CI, stores de agentes, arqueología, snapshots de Research, bases de
labs y cachés no se elevan a esa autoridad. Sus conexiones son contratos,
hashes y refs; su presencia física no prueba que sean consumidores activos.

Runtimes comprobados por proceso/listener: Hub `127.0.0.1:8900`, Research
`127.0.0.1:8890`, Codex `127.0.0.1:8891`, Ollama `127.0.0.1:11434`, Open WebUI
`:8080`, runner de Actions y los puentes rclone. Esto prueba presencia, no
salud, capacidad del proveedor ni corrección de sus datos.

## Regla de parada para tareas simples

Una consulta de sólo lectura con alcance y formato acotados se resuelve con
este estado actual y los archivos directamente nombrados. No debe disparar un
escaneo del repositorio, una recalculación de hashes no solicitada, una
consulta de base o servicio, ni una auditoría de consumidores. Una discrepancia
ajena a la pregunta se registra brevemente y no abre otro trabajo. Esta regla
no reduce los gates de una edición o integración: sólo evita que una pregunta
pequeña se convierta en un diagnóstico no pedido.

## Current experimental frontier — 2026-08-25

Los ciclos aislados C02–C04 demostraron observación nativa, límites de entrada
pública y separación entre referencia técnica y rol de output. C05 agregó el
primer witness real de exportación: `RAYU.blend` → `rayu_export.py` →
`rayu_resources.glb`. Su gate pasa siete comprobaciones y conserva el hash de
la fuente antes/después; el resultado está en
`experiments/cycles/C05/real_export_witness.json` y
`experiments/cycles/C05/RESULTS.md`.

C05 permite afirmar únicamente un evento `export` apoyado para ese GLB. C06 ya
lo materializa como una arista aislada `EXPORTS_TO`; sus tres casos
adversariales vuelven a `unknown` y crean cero aristas. Ninguno prueba entrega
final, publicación, autoría, intención artística ni ausencia de modificación
posterior. El catálogo público real sigue unavailable y el rol de output del
caso AEP/MP4 de C04 sigue `unknown`. El siguiente slice debe probar el join con
una manifestación pública real o registrar explícitamente su ausencia; no
integrar producción ni ejecutar scripts de archivos artísticos.

La búsqueda mecánica acotada en `ARICA` encontró además un segundo patrón
importante: `MYRA_final.mp4`, frames PNG, marcadores `done ok=True`, un log de
sequencer y `ffprobe` real (`H.264`, `1440x1080`, 20 s, 600 frames). Sin
embargo, dentro de `ARICA` no apareció un `.uproject`, `.uasset` o `.umap` que
permita enlazar ese resultado con su estado Unreal nativo. Se conserva como
`activity/output observed` con `source_binding=unknown`, no como un segundo
`EXPORTS_TO` apoyado. Esto fija un caso real de salida sin proyecto fuente.

### Practice graph and curatorial evaluation — 2026-08-25

C07 y C08 cambian la unidad experimental: el archivo ya no se trata como un
catálogo de labels únicas. C07 observa artefactos y propone relaciones
`component_of`, `version_of`, `manifestation_of`, `same_series_candidate` y
`published_as` con score explicable, evidencia, alternativas, evidencia
faltante y próxima sonda. Un frame, una escena, un proyecto nativo, un export
y una publicación pueden coexistir como nodos distintos; `pending_relation` y
`unresolved_candidate` son estados operativos, no un callejón sin salida.

C08 evalúa esas relaciones contra un baseline vacío y agrega fases, series y un
planificador greedy mínimo de portafolio. Sobre cinco fixtures compartidas con
C07, el puente de integración obtuvo recall `1.000` al top-5, precision
`0.400` al top-1 y `0.240` al top-5; por eso no hay promoción automática de
relaciones. El planificador cubrió las cuatro fases y los tres cortes
cronológicos sin repetir la secuencia de 2.048 frames.

Estos resultados son evidencia de contrato y de arquitectura, no aprendizaje
estadístico sobre ARICA. El siguiente experimento debe ejecutar C07 sobre una
muestra acotada de ARICA y compararlo con un gold set ciego del artista antes
de incorporar embeddings, modelos grandes o producción.

## 0. Aprendizaje evaluable

La primera capa de MAK es artistica, cultural y de investigacion. Curatoria,
Portfolio, Research y Matematicas no son silos: comparten Project IR,
procedencia, relaciones, incertidumbre y consumidores. En esta lectura, el
orden de carpetas y proyectos es una representacion operacional de la
hipotesis P versus NP: encontrar una organizacion/reduccion barata y
verificarla con evidencia no equivale a afirmar que P=NP.

`src/flujo/knowledge/learning_policy.py` y `tools/project_learning.py` son la
capa compacta de aprendizaje del ledger. Compilan únicamente episodios con
resultado y validación explícitos, separan entrenamiento y holdout por
`project_id` y pueden registrar una política categórica como regla candidata;
la promoción al router sigue bloqueada hasta contar con evidencia
independiente. Episodios `abstained`, `failed` o `needs_evidence` no se
convierten en etiquetas negativas. La consulta de solo lectura es:

```text
./.venv/bin/python tools/project_learning.py --db data/mak_knowledge.db
```

Un workflow puede registrar un resultado ya validado con
`./.venv/bin/python tools/project_learning.py --db <db> --record-result
<packet.json>`. El paquete debe declarar `schema=mak-verified-result-v1`, un
`project_id` existente, `tool_id`, evidencia y un validador con checks
pasados; si falta algo, el registro falla cerrado.

`tools/source_learning_bridge.py` aplica ese contrato a memoria historica y
paquetes posteriores de investigacion. No copia los arboles: conserva las dos
raices, archivos seleccionados, hashes, UUIDs de mensajes, clase epistemica,
limites de afirmacion y unidades aprendibles. El caso versionado
`knowledge/learning_cases/mak_pnp_search_ecology_2026-08-19.json` conecta
`/home/mak/WIN/claude_sesiones` con
`/home/mak/curatoria_inbox/MAK_TODO_SESION_2026-08-19`. Su episodio verificado
certifica integridad, trazabilidad y contrato de ruta; declara expresamente
`mathematical_truth_validated=false` y no prueba ni refuta P versus NP.

La ingesta del SSD ya tiene una reconstruccion ejecutable de proyectos latentes:
`src/flujo/knowledge/project_reconstruction.py` y
`tools/project_reconstruction.py` leen el indice en modo read-only, distinguen
unidades, subproyectos, exportaciones, bibliotecas y recursos compartidos, y
conservan decisiones, relaciones, unknowns y fingerprint del indice en
`mak-project-reconstruction-v1`. `tools/build_application_intake.py` puede
recibir esa salida mediante `--reconstruction`; los candidatos de biblioteca
dejan de competir como postulaciones y el paquete derivado conserva la
decision y su provenance. La reconstruccion no afirma que un proyecto sea
postulable: solo mejora la unidad material que llega a Curatoria/Postulacion.

El puente `src/flujo/knowledge/reconstruction_adapter.py` y
`tools/import_project_reconstruction.py` convierte cada unidad reconstruida en
`mak-project-ir-v1` con `source.kind=portable_ssd_index`, artefactos
referenciados, relaciones y unknowns. El enrutador comun produce abstencion
para esos registros mientras la fuente fisica no este montada/verificada;
`--db` es opt-in y guarda solo en el LearningStore existente. La politica de
Portfolio es no publicar automaticamente y la de Postulacion es no crear un
paquete desde este puente.

El contexto DREFGIRA ya tiene una capa persistente y consultable en la misma
base `data/mak_knowledge.db`: `src/flujo/knowledge/project_context.py` y
`tools/triangulate_project_context.py` reutilizan el catalogo `entities` y
agregan `context_sources`, `context_relations` y `project_contexts`. El paquete
versionado es `knowledge/project_context/drefgira_2025.json`. La triangulacion
real registro 10 entidades, 9 fuentes y 12 relaciones: 3 verificadas con dos
grupos independientes, 4 atestiguadas por el operador y 5 candidatas. El show
del 2025-11-02 en Movistar Arena queda verificado; Antofagasta/Club Montecarlo
del 2025-11-28 queda candidato por tener una sola fuente. Los cinco registros
DREFGIRA fueron enlazados a artista, album y alcance de gira, conservaron
`review_required`, siguen absteniendose en Curatoria/Postulacion y no generaron
ninguna postulacion. El JSONL y las rutas derivadas fueron regenerados para no
dejar una proyeccion anterior del proyecto.

Con el estado verificado el 2026-08-20, la salida correcta es `status=abstain`
con `eligible_examples=8`, `holdout_count=0` y razón
`no_independent_holdout`: hay ocho ejemplos elegibles distribuidos en cuatro
proyectos, pero el split determinista actual no dejó un proyecto en holdout.
No se promueve ninguna política. Esto es preparación de aprendizaje
estadístico, no entrenamiento de pesos de deep learning.

`src/flujo/knowledge/math_kernel.py` materializa la parte matematica de esa
misma capa. `knowledge/math_targets/` conserva capsulas de target, no una
jerarquia matematica paralela. El starter `MILLENNIUM-PNP-001` esta en
`semantic_fidelity_status=UNTRUSTED`, por lo que el Project IR queda en
`review_required`; el ciclo bounded solo agenda requests `METADATA_ONLY` y
ResultCards con hashes/referencias. El scheduler mantiene las relaciones con
`cultura`, `curatoria`, `portfolio` y `research`, y bloquea toda promocion de
verdad hasta contar con fidelidad semantica y un verificador confiable.

`knowledge/lane_registry/mak_cross_domain_registry_2026-08-20.json` extiende
esa capa a 19 lineas: P=NP, tenis, captura/scraping, deep learning y micelio,
transpilacion, eventos object-centric, simulacion de crecimiento, XIO, entrevistas, aprendizaje de
lenguas, patentes, crops, dental, jardin/geometria, vibe coding, storage,
patronage y autoria cultural. Es un mapa read-only de evidencia y siguientes
gates; no declara implementadas las propuestas. Se consulta con
`./.venv/bin/python tools/project_lanes.py summary`.

El lane de tenis ya tiene un consumidor local read-only: `tennis_mcp_ingest.py`
conserva la fila y su hash, y `tennis_shot_events.py` proyecta eventos
`mak.tennis.shot_event.v0.1` con `transform_chain`, tokens desconocidos e
incertidumbres explícitas. El router lo selecciona solo para un Project IR
activo/verified con dominio `tennis` y formato `data`.

Scraping y deep learning también tienen gates locales, no promesas de
ejecución: `research_source_capture.py` separa plan de captura y solo registra
una URL por vez con hash/backend; `deep_learning_gate.py` exige objetivo,
labels, holdout independiente, `group_key` y validador antes de cualquier
modelo. Ambos permanecen sujetos a revisión de evidencia.

Research 4 añade un consumidor simbólico para `simulate`: acepta un manifiesto
L-system con reglas declaradas, ejecuta una trayectoria acotada y conserva
`simulated`/`model_not_reality`. La licencia de las fuentes y la revisión de la
gramática candidata siguen abiertas.

El estado operacional no se reconstruye leyendo este documento ni el handoff:
se consulta con
`./.venv/bin/python tools/mak_status.py --db data/mak_knowledge.db` o desde
`GET http://127.0.0.1:8900/api/status`. Ambos exponen
`mak-system-status-v1`, un sobre read-only que reúne el ledger
`mak-operational-status-v1` con los consumidores físicos: Hub 8900, Research
8890, puente Codex 8891, búsqueda local, runner de eventos, Blender/RD,
portafolio, runtimes, configuración de proveedores y el registro transversal
de lanes. Los listeners y procesos
se comprueban localmente; las APIs externas solo se marcan como configuradas,
nunca como probadas por inferencia. La consulta abre SQLite en modo read-only y
el endpoint no inicia trabajos. `abstain` es información de seguridad; no se
cuenta como éxito ni como bloqueo.

## 1. Autoridad y alcance

- MAK es el equipo Linux Debian 12. La autoridad física empieza en
  `/home/mak/*`.
- `/home/mak/flujo` es el baseline de autoría, integración, documentación y
  publicación web.
- `/home/mak/WIN` es archivo histórico de la antigua máquina Windows. Sirve
  para genealogía y recuperación selectiva; no es runtime ni dependencia del
  flujo Linux.
- Git transporta una proyección revisada. No decide por sí solo qué existe en
  MAK ni sustituye la verificación física.
- El README y su obra SVG actual son activos protegidos. No se reescriben como
  parte de una limpieza.
- Los phase files son evidencia de decisiones y pruebas. Este documento es la
  síntesis operativa y tiene precedencia para el trabajo nuevo.

## 2. Interfaces y procesos actuales

| Superficie | Estado | Uso |
|---|---|---|
| `cultura/mak_plataforma/hub.py` | Activa | Interfaz única de MAK en `127.0.0.1:8900`. Agrupa departamentos y rutas. |
| SearXNG local | Activa | Backend de búsqueda en `127.0.0.1:8888`; no es una interfaz adicional de usuario. |
| `python3 -m flujo app/serve` | Portátil/temporal | FLUJO APP offline, con default histórico `8765`; no debe confundirse con el hub MAK ni dejarse como servicio permanente. |
| GitHub Actions runner `mak` | Activo bajo evento | Ejecuta el workflow de eventos cuando llega una orden externa. |
| `tools/route_idea.py` | Activo | Convierte una idea o incidente en un packet mínimo por área, para que un agente externo no tenga que leer todo el repo. |

No hay que abrir puertos adicionales para las herramientas offline. El puerto
8900 es la interfaz local agrupada; el 8888 es una dependencia interna de
research. La ausencia de un listener en 8765 no implica que el código FLUJO
esté roto: es una ruta portátil distinta y se valida bajo demanda.

## 3. Mapa de departamentos y consumidores

| Área | Owner físico principal | Consumidor y contrato |
|---|---|---|
| RD | `RD/`, `src/flujo/`, `data/rd.db` | Eventos, cotizaciones, packs, suplementos, plano/rider, venues y entregables operativos. |
| Portfolio / ISKVW | `web/`, `iskvw/`, `tools/portfolio/` | Obras, archivo público, piezas SVG, vínculos y presentación autoral. |
| Research | `cultura/mak_research/`, `tools/research_job_router.py`, `tools/execute_research_job.py` | Preguntas por dominio, fuentes, claims, relaciones, hashes, licencias y reportes/propuestas. |
| Curatoria | `curatoria/`, `cultura/mak_curatoria/` | Carpetas caóticas -> clasificación, índice, procedencia, triangulación y dossier. |
| Cultura / MAK | `cultura/mak_plataforma/` | Orquestación local, health, gobierno, backlog, entrega y exposición en 8900. |
| Lenguaje / Vigía | `cultura/mak_lenguaje/`, `cultura/mak_vigia/` | Contratos de idioma y vigilancia de convocatorias sin convertir candidatos en hechos. |
| Venue / SCD | `data/venues/`, `tools/venue*.py`, `tools/venue3d_smoke.mjs` | Ficha de venue, geometría, plano visual y demostración 3D. SCD es un demostrador, no un levantamiento técnico certificado. |

RD y Portfolio comparten entidades y procedencia, pero no pierden su
autoridad propia. Cultura puede investigar para cualquiera de los dos; no
debe duplicar sus bases ni asumir que un candidato ya es un dato confirmado.

## 4. Semántica compartida

Las relaciones entre RD, Portfolio, Curatoria, Research y Venue se expresan
con campos estables, no con nombres ambiguos de carpetas:

- `venue_id`: sala, espacio o lugar de trabajo.
- `project_id`: proyecto, evento, obra o propuesta.
- `asset_id`: imagen, video, documento, SVG, blend o evidencia.
- `provenance`: fuente física y cadena de transformación.
- `confidence`: nivel de confirmación del dato.
- `publico`: si puede salir de la superficie privada hacia un producto público.
- `consumer`: qué herramienta realmente lee el dato.

Una relación entre Venue y RD puede alimentar un plano/rider; una relación
entre Venue y Portfolio puede alimentar un portafolio o una propuesta visual;
una relación entre Curatoria y Research puede alimentar un dossier o una
postulación. La relación debe quedar tipada y trazable, no fusionarse por
parecido textual.

## 5. Datos y bases de RD

- `data/rd.db` es el catálogo activo de lectura para reactivos, packs,
  productoras, venues y consultas RD. Es una fuente/proyección delimitada; no
  se fusiona a ciegas con otro SQLite.
- `data/rd_datos.db` es un almacén separado de datos de campo/privacidad y está
  vacío por diseño según la verificación documentada. No se rellena con una
  copia del catálogo.
- `data/venues/*.json` conserva la fuente declarativa de venues y sus esquemas.
  Los índices y HTML son salidas derivadas y regenerables.
- Las memorias, credenciales, exports privados, bases protegidas y productos
  grandes permanecen en su dueño físico. El repo guarda contratos, hashes,
  manifiestos o proyecciones seleccionadas, no copias masivas.

## 6. Workflow de eventos y Blender

La cadena productiva actual es:

```text
correo externo -> issue etiquetado -> runner MAK -> download_post
    -> preservación temprana en OneDrive -> clasificación media
    -> renderer MAK de imagen o video -> publicación en OneDrive
```

El tramo correo -> issue vive fuera del repo. Dentro del repo, el workflow
activo es `.github/workflows/issue_descarga_ig.yml`:

- `image`: `tools/render_flyer_mak.py` y el grafo compartido de
  `src/flujo/eventos/blender_nodes.py`.
- `video`: `tools/render_video_sequence_mak.py` y
  `src/flujo/eventos/blender_nodes_video_seq.py`.
- `carousel`: conserva el comportamiento de imagen/poster; no se inventa un
  render de video múltiple.
- tipo desconocido: falla cerrado; no adivina.

El workflow guarda el MP4, poster, metadata y caption antes de iniciar Blender
y conserva logs, manifest y frames parciales aunque el render falle. El issue
solo se cierra cuando el resultado completo se publica correctamente.

### Política visual permanente

- Imágenes: `fitwidth_fade`, proporción preservada, abertura llena en ancho,
  centrado vertical y fade existente.
- Video retrato 9:16 (tolerancia de razón `0.03`):
  `video_portrait_9_16` con `cover_center`, proporción preservada, centrado
  X/Y y recorte solo arriba/abajo, sin barras negras.
- Cualquier otra proporción de video: `video_other_aspect` con
  `contain_bars`, proporción preservada, centrado X/Y y fuente completa;
  las bandas negras ocupan el eje que sobra (arriba/abajo para fuentes anchas,
  laterales para fuentes muy angostas).
- La decisión usa las dimensiones reales descargadas, no el nombre del archivo
  ni la suposición de que todo reel es retrato 9:16. El manifiesto registra
  `issue_flow`, política, razón y eje de recorte o de bandas.
- Video: `/home/mak/RD/AUTOMATIZACION/RD.blend`, Blender
  `/home/mak/blender/blender`, Cycles, 128 samples, GPU obligatoria y
  `render_manifest.json` con proporciones, eje de recorte y dispositivo.
- El `.blend` no se guarda durante los renders de validación.

La política completa y sus pruebas están en
`context/VIDEO_WORKFLOW_MAK_20260817.md`.

## 7. Research, APIs y límites

Research separa discovery, captura, evidencia, claims, relaciones y
productos. `tools/interpretive_garden_workflow.py` construye el modelo SQLite
y reportes del laboratorio sin llamar APIs; `research_job_router.py` crea un
job persistente por dominio; `execute_research_job.py` ejecuta una captura
acotada y registra estado, hash, licencia y créditos.

La casa tiene un catálogo de integraciones (modelos, búsqueda, scraping,
GitHub, Instagram metadata, Drive, OneDrive y otras rutas
opcionales). La cantidad de claves no equivale a cantidad de APIs operativas:
cada proveedor debe tener una prueba reciente, un consumer, una política de
costo y una salida registrada en el handoff. Una key nunca se copia a Git ni
se imprime en un reporte. Cerebras quedó observado con HTTP 402; la ruta
cloud verificada es Groq -> Gemini y Ollama queda como fallback local. Los
proveedores retirados por decisión del usuario no se presentan como activos.

Firecrawl/Crawl4AI/SearXNG son herramientas de captura/búsqueda, no fuentes de
verdad. El resultado debe separar fuente oficial, candidato, claim, relación,
fecha, licencia y confianza. Un research puede terminar en informe o borrador
de propuesta, pero una propuesta sigue siendo un producto revisable, no una
escritura automática sobre RD o Portfolio.

## 8. Superficies históricas y exclusiones

Estas rutas se conservan para evidencia, recuperación o uso manual acotado,
pero no son llamadas por el workflow Linux nuevo:

- `src/flujo/eventos/flyer_auto.py`: legado con supuestos Windows/Droplet y
  todavía expuesto por un comando CLI histórico; no borrarlo sin una fase de
  compatibilidad propia.
- `tools/render_video_rd.py`: ruta H264 manual sobre
  `RD.paravideo.blend`, manual-only; no es el renderer de secuencia MAK.
- `RD.paravideo.blend` y cualquier MP4 histórico: evidencia, no input actual.
- `/home/mak/WIN`: archivo histórico completo, no dependencia de runtime.
- `n8n`: fuera del objetivo operativo actual por decisión del usuario.
- `XIO`: integración diferida, no obsoleta; conecta Chataigne/OSC con shows,
  venues y el trabajo VJ. Se retoma cuando exista un show que requiera probarla.

La existencia de una herramienta legacy no significa que esté rota; significa
que no debe confundirse con el consumidor actual. Cualquier futura eliminación
requiere demostrar imports, entrypoints, tests, consumidores y rollback.

## 9. Git y publicación web

- `main` es la única rama permanente y el tronco de publicación.
- `archive/house-history` es el único tag de preservación de la topología
  histórica.
- Las ramas de tema son opcionales y cortas (`rd/*`, `portfolio/*`, `mak/*`,
  `tools/*` o `cleanup/*`); se eliminan después de promover a `main`.
- No se crean ramas permanentes por departamento, `source/*`, `work/*`,
  `develop`, `staging` ni release branches.
- Cada cambio debe tener un consumidor, write set acotado, prueba foreground y
  rollback. Se hace `git add` explícito; no se publica un árbol completo por
  accidente.
- Un agente externo puede empezar leyendo solo `agents.md`, este documento,
  `context/OWNER_MANIFEST.md` y el packet producido por `tools/route_idea.py`.
  Luego lee únicamente el handoff o contrato del área que va a tocar.

## 10. Qué se aprendió de las fases históricas

La genealogía completa queda respaldada en `context/PHASE*.md/.csv` y en el
handoff. Sus conclusiones durables se pueden entender por familias:

| Familia | Decisión durable |
|---|---|
| Inventario y genealogía | La autoridad es física (`/home/mak/*`); WIN es historia; Git es transporte. |
| Crosswalk WIN -> MAK | Solo se migra un slice vertical con consumidor real; no se copia un árbol ni se convierte una idea en integración. |
| Ownership y semántica | Cada herramienta tiene owner, consumidor, dependencia, idioma, plataforma, procedencia y estado. |
| RD y datos | `rd.db`, `rd_datos.db`, venues y productos derivados tienen límites distintos; el almacén vacío no se rellena por conveniencia. |
| Research y Curatoria | Discovery, captura, triangulación, claims y propuestas son pasos separados; candidatos no son hechos. |
| Portfolio y Venue | Venue puede unir RD y Portfolio; SCD es una demostración geométrica y no sustituye una ficha técnica certificada. |
| Salud y limpieza | Se valida antes de mover/borrar; basura confirmada se cuarentena de forma reversible; evidencia no se elimina. |
| Git | Se consolidó una sola `main` y un tag histórico; no se conserva un bosque de ramas. |
| Eventos y video | El camino Linux MAK quedó separado de WIN, con preservación temprana, clasificación image/video y composición por proporción. |
| APIs y costo | Una API solo se declara operativa con consumer y prueba reciente; las claves y servicios no son evidencia suficiente. |

## 11. Pendientes reales, sin reabrir lo cerrado

1. Observar un issue real nuevo para confirmar en Actions la preservación
   temprana y la publicación en OneDrive; no inventar ese resultado en local.
2. Ejecutar, cuando corresponda, un smoke acotado de `layout` en un video real
   y revisar su manifest antes de renderizar una secuencia completa.
3. Mantener la matriz de proveedores del handoff actualizada con pruebas,
   costos y fallos; no reactivar proveedores retirados.
4. Hacer una fase separada para retirar o cuarentenar rutas legacy solo si se
   demuestra que no tienen consumidores legítimos.
5. Revisar dominio/hosting del Portfolio en una tarea aparte; no mezclarlo con
   el runtime local ni con el catálogo RD.

El siguiente trabajo seguro por defecto es el punto 1 o un nuevo packet de
idea generado por `tools/route_idea.py`. No hay que volver a leer las 600
fases para cada cambio: esta síntesis, el owner manifest y la evidencia
acotada del área son suficientes.

## Referencias canónicas

- `agents.md`
- `context/LAST_HANDOFF.md` (solo el paquete `Agent bootstrap — CURRENT`; el
  resto es evidencia histórica)
- `context/OWNER_MANIFEST.md`
- `context/VIDEO_WORKFLOW_MAK_20260817.md`
- `CAPACIDADES.md`
- `MAPA.md`
- `docs/AUTORIDAD.md` (qué documento manda sobre cuál, y por qué)
- sección `Historical checkpoint — Phase 495` y fases posteriores en
  `context/LAST_HANDOFF.md`

Dos archivos que esta lista citaba fueron retirados de ella el 2026-08-28
porque **ya no existen**: PHASE209 (retirado)
y PHASE413 (retirado). De los 748 archivos
`PHASE*` que `context/PHASE_REPORTS_INDEX.md` contaba en agosto quedan 13, y
esos dos no están entre ellos. Este documento es el segundo del orden de
lectura, así que una cita colgando acá le cuesta una sesión a quien la siga.
