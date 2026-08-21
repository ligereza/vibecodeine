# Operational Handoff

## Current objective

Mantener el repo web y el runtime local en un estado coherente y verificable,
con una primera capa artistica-cultural-investigativa comun para curatoria,
portfolio, research y matematicas. La hipotesis P versus NP se usa aqui como
modelo conceptual de representacion, busqueda y certificados; no como un
teorema ya demostrado.
El estado operacional ya no depende de releer este archivo: se consulta en la
CLI y en el Hub real de 8900 mediante `mak-system-status-v1`, que reúne el
ledger con los consumidores locales y deja las atenciones explícitas. Los
gates de esta tanda quedaron cerrados: se preserva la incertidumbre
matematica y Research 4 tiene un consumidor local simbólico, con licencia y
revisión humana aún pendientes. La continuidad de ideas se consulta en el lane
registry, no releyendo la memoria historica completa.

## Session transfer checkpoint — 2026-08-21

La fase web/DB queda validada y lista para publicar. El conjunto propio de esta
fase es la limpieza de superficies Windows obsoletas, la preservacion de XIO
como workflow manual diferido, el gate `tools/repo_audit.py`, su regresion,
`tools/gen_rd_standalone.py`, la fila de `CAPACIDADES.md`, los cambios de CI/
Makefile y este handoff. No se debe hacer `git add .`: el worktree contiene
otros cambios de sesiones anteriores que deben permanecer intactos y sin
mezclarse.

Pruebas cerradas: pytest completo exit 0; `npm run typecheck` exit 0;
`repo_audit` exit 0 (36 modulos, 35 alcanzables, 0 muertos, 0 referencias
obsoletas, cuatro SQLite integras); compileall y `git diff --check` exit 0.
No hay procesos de pytest, intake, Blender ni render activos. La siguiente
accion exacta es revisar el staging del conjunto propio, crear el commit y
hacer push de `main`; despues la nueva sesion debe continuar desde `Next
concrete action` sin repetir la auditoria.

## Physical authority and migration status

- La autoridad física es `/home/mak/*`; `/home/mak/flujo` es el baseline de
  autoría y `/home/mak/WIN` es evidencia histórica de Windows.
- No se copia ni se borra el árbol histórico. Los datos locales ignorados y los
  productos generados se preservan fuera del commit salvo que una regla del
  repo los declare artefactos versionables.
- Git tiene una sola rama local (`main`) y una sola rama remota operativa
  (`origin/main`). El README y su SVG protegido no se modifican.
- En la inspección actual se observaron `cron`, el runner local de GitHub
  Actions y Open WebUI ya instalados; esta tarea no inició ninguno. El Hub
  existente `mak-hub.service` fue reiniciado de forma controlada para activar
  la nueva ruta read-only y quedó activo en 8900; no se inició ningún servicio
  nuevo ni se dejó un render adicional.
- La interfaz temporal del Research local ya estaba activa antes de esta
  tanda; no fue iniciada, detenida ni modificada aquí.

## Completed work with command and result

- Se agregó `src/flujo/knowledge/learning_policy.py`: learner categórico
  auditable, split por `project_id`, abstención ante evidencia insuficiente y
  registro de política solo como candidata.
- Se agregó `tools/project_learning.py` y
  `tests/test_learning_policy.py`. El adaptador
  `mak-verified-result-v1` exige proyecto existente, evidencia, validador y
  checks pasados; es idempotente y falla cerrado.
- `src/flujo/knowledge/project_api.py` expone `learning.policy` en modo
  read-only. `CAPACIDADES.md` y `docs/MAK_CURRENT_STATE.md` declaran el
  contrato.
- Se integró `operational_status()` en
  `src/flujo/knowledge/project_api.py`, `tools/mak_status.py` y el campo
  `operational` de `GET /api/status`. CLI y Hub comparten el mismo contrato
  read-only: estado general, evidencia pendiente, bloqueos, abstenciones y
  siguientes acciones. El Hub conserva sus campos históricos de servicio.
- Se agregó `src/flujo/knowledge/system_status.py`, el sobre
  `mak-system-status-v1` que conecta el ledger con once consumidores físicos:
  fuente/Hub 8900, Research 8890, Codex 8891, SearXNG 8888, runner de eventos,
  Blender/RD, portafolio, runtimes, configuración de proveedores y el registro
  transversal de lanes. Solo lee
  rutas, `/proc`, listeners loopback y nombres de variables; no hace requests
  externos, no inicia jobs y nunca devuelve valores de claves.
- El Hub canónico `/home/mak/plataforma/hub.py` ahora expone
  `GET /api/status` y una pestaña `● estado` en 8900. El endpoint real fue
  verificado con HTTP 200, esquema `mak-system-status-v1`, once componentes y
  `read_only=true` después del reinicio controlado.
- El componente `lanes` del mismo sobre valida, sin mutar, el registro
  `mak-cross-domain-lane-registry-v1`: 19 lanes bajo
  `cultural_research_first` (1 implementada, 7 parciales, 11 propuestas).
  El CLI y el estado del Hub comparten ahora el módulo
  `src/flujo/knowledge/lane_registry.py`.
- Se agregó `runtime_tools.resolve_blender()`: resuelve la instalación real
  `/home/mak/blender/blender` aunque no esté en `PATH`. `contract_registry` y
  `episode_runner` comparten esa resolución, eliminando el falso faltante de
  `blender_optional` sin instalar ni ejecutar Blender desde el estado.
- El probe de render cuenta procesos por el ejecutable real de `/proc`, no por
  texto de argumentos: una orden de inventario que mencionaba la ruta de
  Blender había producido un falso `active`. La lectura final muestra
  `render=ready` y `process.running=false`; no hay render en segundo plano.
- La auditoría de contratos más reciente se registró explícitamente como
  `simulation_consumer_20260820`: 59 contratos, 59 verificados, 0 con
  evidencia pendiente y 0 no disponibles. El ledger actual queda con 2
  atenciones accionables (4 proyectos en revisión y 3 episodios sin evidencia)
  y 2 informativas (abstención segura y falta de holdout independiente).
- `tools/source_learning_bridge.py` y
  `src/flujo/knowledge/source_learning.py` conectan dos raices fisicas por
  referencias: `/home/mak/WIN/claude_sesiones` como memoria de hipotesis y
  `/home/mak/curatoria_inbox/MAK_TODO_SESION_2026-08-19` como auditoria y
  contratos de investigacion. El caso versionado valida 2 raices, 9 archivos,
  9 mensajes por UUID/hash, 7 hallazgos y 5 unidades de aprendizaje sin copiar
  los arboles ni el texto privado de las conversaciones.
- La ingestion real se registro como proyecto activo
  `mak-pnp-search-ecology-2026-08-19` y episodio verificado
  `episode-source-learning-c6f328491b44e1af7828ec1b`. El alcance guardado es
  `source_integrity_and_epistemic_contract_only` y
  `mathematical_truth_validated=false`: no afirma una solucion de P versus NP.
- `src/flujo/knowledge/math_kernel.py` agrega un scheduler metadata-only sobre
  el mismo Project IR y la misma base SQLite: una capsula `MILLENNIUM-PNP-001`,
  requests acotados y ResultCards sellados. El proyecto conserva los dominios
  `cultura`, `curatoria`, `portfolio`, `research` y `mathematics`; como la
  fidelidad semantica esta `UNTRUSTED`, su estado es `review_required` y el
  ciclo real solo dejo una request `METADATA_ONLY` en cola. No se ejecuta un
  worker ni se promueve verdad por ausencia de contraejemplos.
- `knowledge/lane_registry/mak_cross_domain_registry_2026-08-20.json` y
  `tools/project_lanes.py` agregan un mapa read-only de 19 lineas bajo la misma
  primera capa: P=NP, tenis, captura/scraping, deep learning/micelio,
  transpilacion, eventos, simulacion de crecimiento, XIO, claims, lenguas, patentes, crops, dental,
  jardin/geometria, vibe coding, storage, patronage y autoria. Cada linea
  conserva dialectos, estado epistemico, evidencia, consumidor si existe,
  guardrails y un siguiente gate; las propuestas no se presentan como trabajo
  implementado.
- El lane de tenis ya tiene `src/flujo/tennis/shot_events.py` y el consumidor
  read-only `tools/tennis_shot_events.py`: proyectan a
  `schemas/tennis/shot_event.schema.json`, conservan `raw_ref`, hash,
  `transform_chain` y tokens desconocidos, y el router solo lo selecciona para
  un Project IR activo/verified del dominio `tennis`.
- Se registró el primer episodio verificable del lane: proyecto
  `mak-tennis-decision-lab-fixture-20260820`, episodio
  `episode-tennis-shot-fixture-20260820`, 4 eventos, hash de fixture y 2
  tokens desconocidos preservados; `network_calls=0` y sin contrafactuales.
- El probe de ruta del mismo proyecto selecciona
  `tennis_shot_event_consumer` y queda registrado como
  `episode-tennis-consumer-probe-20260820`; prepara un comando local acotado,
  no lo ejecuta ni escribe salida generada.
- Scraping y deep learning ya tienen consumidores acotados: `research_source_capture.py`
  separa plan/captura y registra una sola URL con hash en `SourceCorpusStore`;
  `deep_learning_gate.py` exige labels, holdout independiente, agrupación
  anti-leakage y validador, pero nunca autoriza entrenamiento por sí solo.
- La evidencia física de Research 4 quedó enlazada al Project IR como proyecto
  `mak-research-capture-job4-20260820` y episodio
  `episode-research-capture-job4-20260820`: 4 fuentes capturadas, hashes y
  etapas verificadas; licencia pendiente; el consumidor simbólico queda sujeto
  a revisión humana y no afirma crecimiento biológico.
- Research 4 ya tiene un consumidor `research_simulation_consumer`:
  `knowledge/research_simulations/job4_lsystem_candidate_20260820.json` usa
  reglas explícitas, límite de símbolos y alcance `visual_grammar`; la salida
  se etiqueta `simulated`/`model_not_reality` y no se interpreta como biología.
- El dataset existente de logo-clean quedó enlazado como
  `mak-logo-clean-learning-gate-20260820`; su episodio
  `episode-deep-learning-gate-logo-clean-20260820` abstiene correctamente:
  solo hay 3 ejemplos y no existe holdout independiente, por lo que no se
  autoriza entrenamiento.
- `tests/test_system_status.py` cubre resolución local, redacción de secretos
  y ausencia de escrituras. El cambio de `providers.provider_registry()` hace
  que un entorno explícito no cargue silenciosamente otro `.env`.
- `web/src/components/HubDashboard.tsx` muestra el estado unificado antes del
  ledger, y `web/src/api/flujoApi.ts` consume `/api/status` como fuente única;
  las páginas generadas de `context/` fueron reconstruidas con Node 24.19.0.
- La consulta actual del ledger devuelve `attention` con 2 asuntos accionables
  y 2 informativos: cuatro proyectos en revisión, tres episodios sin evidencia,
  abstención segura y falta de holdout independiente. Los 59 contratos,
  incluido Blender y el puente de memoria, quedaron verificados.
- Research job 4 sobre `JARDINES_INTERPRETATIVOS.md` capturó cuatro fuentes,
  extrajo claims, relaciones, contexto e interpretación y dejó el siguiente
  paso en `simulate`; el runner histórico no tenía una función ejecutable para
  ese paso (`interpretive_simulation_callables=[]`,
  `research_router_simulation_callables=[]`), pero ahora existe el consumidor
  local simbólico `research_simulation_consumer`; el resultado permanece
  marcado como modelo y no como hecho. No se clonaron ni instalaron repos
  candidatos; la licencia y la revisión humana siguen pendientes.
- La revision de procedencia P versus NP incorporó
  `knowledge/math_targets/p_vs_np_official_statement_capture_2026-08-20.json`,
  con la pagina oficial de Clay, hash de la nota canonica y estado `Unsolved`.
  El artefacto formal local tiene hash completo y ambos hashes se guardan en la
  capsula; la fidelidad semantica permanece `UNTRUSTED` y el kernel sigue
  bloqueando cualquier promocion de verdad.
- La base local ignorada `data/mak_knowledge.db` contiene ocho episodios
  elegibles en cuatro proyectos; incluye el fixture verificado, el probe del
  consumidor de tenis. La política medida es `abstain` con razón
  `no_independent_holdout`, `eligible_examples=8`, `train_count=8` y
  `holdout_count=0`. No se promovió ninguna regla.
- La contradicción detectada en el handoff fue eliminada: ya no se escribe un
  total fijo de tests ni se recicla el conteo antiguo del learner.
- Se declaró en `web/package.json`, `web/package-lock.json` y
  `web/README.md` el requisito real `Node >=20.19.0`; con el Node 24.19.0
  disponible en MAK los builds reproducibles pasan.
- Los cambios de esta tanda se publicaron en `main` mediante el commit
  `7674c49` y el push normal a `origin/main`; la evidencia generada dentro de
  `data/mak_knowledge.db` sigue siendo estado local ignorado. La
  evidencia generada dentro de `data/mak_knowledge.db` es estado local
  ignorado; los writes explícitos fueron el refresh de contratos y la
  ingestion verificada del caso de memoria descrito arriba.
- Se retiraron Watsonx, AWS y Azure de la superficie operativa activa. Se eliminaron
  sus adaptadores, alias, capacidades, rutas de fallback, opciones CLI, UI y
  políticas de proveedores en `cultura/mak_plataforma/providers.py`,
  `cultura/mak_research/research_lib.py`, `research.py`, `refutar.py`,
  `cultura/mak_codex/codex_lib.py`, `cultura/mak_plataforma/hub.py`,
  `iskvw/editor.html`, `src/flujo/autonomia.py` y `src/flujo/cli.py`.
  Research queda con Groq -> Gemini -> Ollama; Cerebras permanece solo como
  opcion explicita porque el probe real devuelve HTTP 402. Codex conserva
  NVIDIA NIM -> Ollama; vision del portafolio queda local con el lector
  Ollama existente.
- Las herramientas Watson exclusivas se movieron, sin borrarlas, a
  `/home/mak/_archive/watsonx-retired-20260820/`: cuatro sondas/benchmarks y
  copias protegidas de `n8n-local/research.env` y `research/research.env` antes
  de retirar sus líneas Watson/AWS. No se tocaron `/home/mak/WIN`, ledgers,
  productos ni resultados históricos.
- Se retiró `boto3` de `pyproject.toml` y `requirements.txt`. La matriz y el
  mapa ahora describen los proveedores retirados como evidencia histórica, no
  como capacidad disponible. `python3 -m compileall` terminó con exit 0,
  `./.venv/bin/python -m pytest -q` terminó con exit 0 (warnings existentes de
  Pillow), y `git diff --check` quedó limpio.
- Se verificó el reemplazo de proveedores en el runtime y sus espejos. El
  adaptador Gemini usa `gemini-3.6-flash`, carga solo `GEMINI_API_KEY` y
  `GEMINI_MODEL` desde el `.env` secundario, y devuelve texto y JSON válidos.
  Los probes foreground de Groq, Gemini y Ollama devolvieron texto no vacío;
  Firecrawl capturó `https://example.com` mediante el backend configurado
  (`167` caracteres). El probe explícito de Cerebras devolvió HTTP 402
  `payment_required`, por lo que no participa en la cadena automática.
  Azure no conserva llamadas ni configuración activa; las coincidencias que
  quedan son comentarios, vocabulario de arqueología o resultados históricos.
  La copia vieja de `research_lib.py` y el workflow n8n retirado siguen
  preservados en `/home/mak/_archive/provider-retirement-20260820/`.
- El adaptador estructurado de `cultura/mak_plataforma/providers.py` fue
  endurecido para no truncar JSON cuando el llamador pide un presupuesto muy
  pequeño; su probe Gemini devolvió un objeto JSON válido. La suite completa
  pasó después de actualizar el test que aún esperaba Cerebras al frente de
  la ruta de riesgo alto.
- Se probó la regla arquitectónica "salir del espacio de soluciones" con dos
  fallos reales. Primero, una respuesta Gemini simulada con
  `finishReason=MAX_TOKENS` y sin `content.parts` no obligó a reparar Gemini:
  `LLM.call` la clasificó como vacía y continuó con Ollama (`status=ok`).
  Segundo, Firecrawl capturó la documentación oficial de Gemini con `236737`
  caracteres de navegación y contenido; una selección acotada de ventanas
  relevantes redujo la evidencia a `3119` caracteres y Ollama identificó
  `MAX_TOKENS` y la decisión de rechazar el resultado truncado. La conclusión
  es que la captura funciona y la dependencia que debe cambiar es el paso de
  evidencia-a-análisis, no Firecrawl. Este experimento fue read-only y no
  cambió código ni datos.
- En el primer lote de apuestas predictivas se eligieron dos verificaciones de
  alto aprendizaje y bajo costo. El contrato de proveedores (`PROVIDER_ORDER`,
  `PROVIDER_CAPABILITIES`, `PROVIDER_ENV_KEY` y métodos `LLM._*`) quedó
  consistente (`all_provider_contracts_consistent=true`). La búsqueda de
  interfaces antiguas solo encontró un comentario de endpoint legacy,
  resultados históricos y tres copias bajo `/home/mak/rollback/`; no encontró
  un consumidor activo roto. Ambas predicciones se descartan sin parche.
  El lote confirma que la unidad útil es `prediccion -> prueba barata ->
  descarte o patron`, no volumen de archivos.
- Se compararon los enfoques externo y resiliente. En la ruta externa,
  Firecrawl capturó la página oficial de precios de Cerebras (`4053`
  caracteres; ventana relevante `1424`), pero el resumen Ollama inventó un
  crédito de `$5`; la salida fue rechazada por falta de evidencia. La fuente
  confirma solo tier Free `$0` y límites menores, mientras el probe local real
  sigue en HTTP 402. La conclusión es `captura externa -> evidencia acotada ->
  validación`, nunca `captura -> verdad`.
- En la ruta resiliente se encontró y corrigió un bug real en
  `cultura/mak_plataforma/providers.py`: `TASK_CAPABILITIES["research"]`
  pedía la capacidad inexistente `research`, por lo que el router devolvía
  `local_deterministic` aun con proveedores disponibles. Ahora Research usa
  la capacidad declarada `hypothesis` y enruta `Groq -> Gemini -> Ollama`.
  Se agregó `test_research_route_uses_declared_hypothesis_capability`; el test
  enfocado y la suite completa terminaron con exit 0, y `git diff --check`
  quedó limpio.
- Se inició el experimento dual de depuración sobre Research/proveedores
  reutilizando `src/flujo/diagnostics.py` y el comando `flujo diagnose`, sin
  crear otro framework. Para el agente externo se generaron dos paquetes
  `mak-diagnostic-v1` read-only: ambos rutearon a Research, redacted datos
  sensibles, excluyeron WIN y entregaron contrato, rutas existentes, gate y
  reproducción. El primer postprocesador falló con `python: command not found`;
  al repetirlo con `.venv/bin/python`, el diagnóstico terminó con exit 0.
- El mismo slice para MAK validó `route_task("research")` como
  `hypothesis`, `Groq -> Gemini -> Ollama`, y simuló una respuesta Gemini sin
  `content.parts`: la salida pasó a Ollama sin bloquearse. El paquete Research
  tenía además una ruta inexistente (`src/flujo/research`); se eliminó de
  `src/flujo/diagnostics.py` y `context/diagnostics/domains.json`, y se agregó
  una regresión que exige `missing_read_paths=[]`. Tests enfocados, suite
  completa y compileall terminaron con exit 0; no se inició ningún servicio.
- Se agregó `src/flujo/index/code_index.py` y el comando `flujo code-index`.
  Construye `mak-code-structure-v1` con AST, símbolos, imports, consumidores,
  entradas, efectos y hashes, sin guardar texto fuente. Excluye `WIN`,
  `.agents`, `.codex`, `.claude`, entornos, caches y builds. El índice real
  `context/code_structure_index.json` contiene 781 módulos Python, 8552
  símbolos, 186593 líneas declaradas y cero errores de sintaxis; ocupa
  2671255 bytes. `--query` devuelve un `mak-code-brief-v1` acotado para que
  un agente abra solo candidatos relevantes. Se agregó regresión para
  consumidores relativos y errores de sintaxis aislados, y se sincronizaron
  `MAPA.md`/`context/comandos.json` con el generador oficial.
- El primer push del índice expuso dos fallos de portabilidad en CI: una ruta
  histórica con el usuario Windows real y un test que exigía un artefacto
  formal guardado fuera del clon. Se anonimizó la ruta en
  `context/fases.migracion.md` y `tests/test_math_kernel.py` ahora valida el
  hash si el artefacto externo existe, pero hace `skip` explícito en clones
  limpios. `./.venv/bin/python -m flujo verify` y la privacidad local pasan;
  el commit `6743467` se publicó y CI #22/seguridad de ese SHA terminaron en
  `success`.

## Open integration items

| Item | Path | Status | Proof required |
| --- | --- | --- | --- |
| Python learning layer | `src/flujo/knowledge/learning_policy.py` | verified, published | full pytest exit 0; py_compile exit 0; diff check exit 0 |
| Web source | `web/` | verified, published | Node 24.19.0: `npm ci`, audit 0 vulnerabilities, typecheck and all three builds exit 0 |
| Documentation contract | `CAPACIDADES.md`, `docs/MAK_CURRENT_STATE.md`, this file | verified, published | docs hygiene included in full pytest exit 0 |
| Watson/AWS/Azure retirement and provider replacement | provider registries, research/codex chains, Hub/UI, env files, `pyproject.toml`, `requirements.txt`, `/home/mak/research/` | verified locally; not yet published | full pytest exit 0; compileall exit 0; Groq/Gemini/Ollama/Firecrawl probes pass; Cerebras HTTP 402; recoverable archive present |
| Operational status | `src/flujo/knowledge/system_status.py`, `cultura/mak_plataforma/hub.py`, `tools/mak_status.py`, `web/` | verified locally and active at 8900; lane registry now included read-only; publication pending | focused pytest; temporary/live `/api/status` HTTP 200; eleven components; read-only endpoint |
| Python structure index | `src/flujo/index/code_index.py`, `context/code_structure_index.json`, `tests/test_code_index.py` | verified locally; source-free AST index and query brief; publication pending | focused/full pytest exit 0; CLI probe; zero syntax errors; diff check exit 0 |
| Source learning bridge | `src/flujo/knowledge/source_learning.py`, `tools/source_learning_bridge.py`, `knowledge/learning_cases/`, `schemas/knowledge/source_learning_case.schema.json` | verified locally and recorded; published in `7674c49` | source roots/files/messages/claim boundaries pass; Project IR episode verified; no truth promotion |
| Cultural-first math kernel | `src/flujo/knowledge/math_kernel.py`, `tools/math_kernel.py`, `knowledge/math_targets/`, `schemas/knowledge/math_*.schema.json` | verified locally; one bounded metadata request queued; published in `7674c49` | capsule validation, common Project IR domains, sealed ResultCard guard and truth-promotion block |
| Cross-domain lane registry | `knowledge/lane_registry/`, `tools/project_lanes.py`, `schemas/knowledge/cross_domain_lane_registry.schema.json` | verified locally; 19 lanes, 3 priority-0 lanes, no new consumer claimed for proposals; publication pending | registry validation, common first-layer rule, evidence refs, guardrails and next gates |
| Tennis MCP first slice | `src/flujo/tennis/mcp.py`, `tools/tennis_mcp_ingest.py`, `tests/test_tennis_mcp.py` | verified locally; conservative parser and hash-linked JSONL projection; no external acquisition | focused pytest, syntax check, diff check; feeds the shot-event consumer |
| Tennis shot-event consumer | `src/flujo/tennis/shot_events.py`, `tools/tennis_shot_events.py`, `schemas/tennis/shot_event.schema.json` | verified locally; router-selected read-only consumer with explicit uncertainty and provenance; first episode recorded | schema validation, Project IR route test, focused pytest, verified episode; next is an independent second fixture |
| Tennis Project IR probe | `tools/project_gate.py`, `src/flujo/knowledge/episode_runner.py` | verified locally; route selects tennis consumer and probe status is `succeeded` without executing it | read-only project gate, recorded probe episode; next is independent evidence |
| Research source capture | `tools/research_source_capture.py`, `cultura/mak_research/source_pipeline.py` | verified locally; existing Research 4 capture linked, license remains pending, no broad crawl | 4 source hashes, verified capture/extract/interpret results; next is license review |
| Research simulation | `src/flujo/knowledge/research_simulation.py`, `tools/research_simulation.py`, `schemas/knowledge/research_simulation_manifest.schema.json` | verified locally; bounded symbolic trajectory, model-not-reality marker, no external calls | manifest schema, deterministic trajectory, budget abstention and Project IR route; next is human review |
| Deep-learning task gate | `src/flujo/knowledge/deep_learning_gate.py`, `tools/deep_learning_gate.py`, `schemas/knowledge/deep_learning_task_gate.schema.json` | verified locally; logo-clean episode abstains on 3-row/no-holdout evidence, training remains disabled | manifest schema, gate tests, Project IR episode; next is an independent holdout |
| Research learning | `/home/mak/research/jobs/4/` | captured/interpreted; bounded symbolic simulate consumer available; license review pending | review candidate grammar and license; no candidate install |
| Publication | `main` -> `origin/main` | verified at `7674c49` | `git rev-parse HEAD` equals `git ls-remote origin refs/heads/main` |

## Tool and dependency verification matrix

| Surface | Command | Current result |
| --- | --- | --- |
| Python suite | `./.venv/bin/python -m pytest -q` | exit 0; warnings only from existing Pillow deprecation |
| Learning policy | `./.venv/bin/python tools/project_learning.py --db data/mak_knowledge.db` | exit 0; abstain; 8 eligible in 4 projects; no independent holdout |
| Source learning | `PYTHONPATH=src ./.venv/bin/python tools/source_learning_bridge.py knowledge/learning_cases/mak_pnp_search_ecology_2026-08-19.json --db data/mak_knowledge.db --record` | exit 0; 2 roots, 9 artifacts, 9 messages, 5 learning units; verified ingestion only |
| Python syntax | `./.venv/bin/python -m py_compile ...` | exit 0 |
| Diff hygiene | `git diff --check` | exit 0 after code-index and map synchronization |
| Python structure index | `./.venv/bin/python -m flujo code-index --root . --output context/code_structure_index.json --query "research provider route" --format json` | exit 0; 781 modules, 8552 symbols, 0 syntax errors; source-free index; 20 bounded query matches |
| Python dependencies | `./.venv/bin/python -m pip check` | exit 0; no broken requirements |
| Provider replacement probes | foreground `LLM(groq|gemini|ollama)` + platform `providers.call(gemini, response_format=json)` | exit 0; all text responses non-empty; Gemini structured response parsed as JSON object |
| Firecrawl capture | foreground `capture_url("https://example.com", backend="firecrawl")` | exit 0; backend `firecrawl`; 167 captured characters |
| Cerebras availability | foreground explicit `LLM(cerebras)` probe | expected failure; HTTP 402 `payment_required`; excluded from automatic route |
| Azure runtime audit | `rg` over active provider/runtime surfaces | no active Azure call/configuration; remaining matches are historical/comments/vocabulary |
| Web typecheck/build | `NODE_BIN=.../node ./node_modules/typescript/bin/tsc --noEmit`; `NODE_BIN=.../node ./node_modules/vite/bin/vite.js build`; `NODE_BIN=.../node scripts/copy-context.mjs` | exit 0 with Node 24.19.0; 1840 modules; `dist/index.html` 777.98 kB |
| Math Kernel cycle | `PYTHONPATH=src ./.venv/bin/python tools/math_kernel.py cycle --db data/mak_knowledge.db --target knowledge/math_targets/p_vs_np_target_capsule_2026-08-19.json --iterations 1 --compute-units 1 --max-expanded-cost 100` | exit 0; `mak-math-ledger-v1`; target `UNTRUSTED`; one `METADATA_ONLY` request; truth promotion blocked |
| Lane registry | `PYTHONPATH=src ./.venv/bin/python tools/project_lanes.py validate` | exit 0; `mak-cross-domain-lane-registry-v1`; 19 lanes; common `cultural_research_first` layer; read-only |
| Tennis MCP slice | `PYTHONPATH=src ./.venv/bin/python -m pytest -q tests/test_tennis_mcp.py tests/test_project_lanes.py` | exit 0; parser preserves raw notation, unknown tokens, source hash and `ANNOTATED` status |
| Tennis shot-event route | `PYTHONPATH=src ./.venv/bin/python -m pytest -q tests/test_tennis_mcp.py tests/test_project_router.py tests/test_project_contracts.py` | exit 0; schema-shaped events, unknowns/provenance preserved, Project IR selects `tennis_shot_event_consumer` |
| Scraping/deep-learning/simulation gates | `PYTHONPATH=src ./.venv/bin/python -m pytest -q tests/test_research_source_capture.py tests/test_deep_learning_gate.py tests/test_research_simulation.py` | exit 0; default scraping is plan-only, deep-learning gate abstains without independent holdout, simulation is bounded/model-labelled |
| Unified status CLI | `./.venv/bin/python tools/mak_status.py --db data/mak_knowledge.db --json` | exit 0; `mak-system-status-v1`; 11 components, including valid 19-lane registry; `render=ready`, no Blender process; 2 actionable and 2 informational ledger items; read-only; 59 contracts audited |
| Unified status HTTP | temporary `ThreadingHTTPServer` + live `127.0.0.1:8900` -> `GET /api/status` | HTTP 200 in both; `mak-system-status-v1`; `read_only=true`; temporary server shut down; live Hub active |
| Catalog federation | `src/flujo/knowledge/catalog_federation.py`, `tests/test_catalog_federation.py`, `data/mak_knowledge.db` | verified locally and integrated additively; 7 read-only sources, 124 tables, 2,075,337 observed rows, 0 copied; integrity and FK checks pass |
| Operational DB bridge | `src/flujo/knowledge/operational_bridge.py`, `tests/test_operational_bridge.py`, `data/mak_knowledge.db` | verified locally and refreshed; 6,132 normalized records, 106,895 curation links, exact package/project/fund links; source rows copied 0; integrity and FK checks pass |
| Web/DB audit gate | `tools/repo_audit.py`, `tests/test_repo_audit.py`, `.github/workflows/ci.yml`, `Makefile` | verified locally; 36 web modules, 35 reachable, 0 dead, 0 stale active references; four DBs have resolved consumer paths and integrity `ok`; publication pending |
| RD live/standalone projection | `src/flujo/rd/panel.py`, `tools/gen_rd_standalone.py`, `web/src/data/rdDbEmbebida.json` | verified locally; generated and tracked JSON are equal (6 records, identical SHA-256); generator now accepts absolute output paths |
| SSD application intake | `tools/build_application_intake.py`, `/home/mak/labs/portable-ssd-index-20260813/archivo_index.sqlite` | verified in `/tmp`; 917 projects scanned, 3 bounded Fondart packages emitted, derived SQLite integrity `ok`; status remains `draft_with_evidence_gaps` |
| DB -> Research -> Curatoria -> Postulacion | temporary foreground pipeline using existing Research corpus, Curatoria diagnostic and `tools/build_application_intake.py` | exit 0; Research 5,179 applications/14 captures; Curatoria 917 projects/13,121 families/45,536 members; Postulacion emitted `drefgira-fondart` with explicit evidence gaps; source trees untouched |
| RD event fixture | read-only query over `operational_records` and `operational_curation_links` | exit 0; 7 events retain producer, raw date, venue and flyer/source evidence; 0 false ISO dates; 0 orphan curation links |
| Contract audit refresh | `PYTHONPATH=src ./.venv/bin/python -m flujo.knowledge.contract_registry --db data/mak_knowledge.db audit --root . --record --run-id simulation_consumer_20260820` | exit 0; 59/59 verified; Blender, source-learning bridge, math kernel, tennis, scraping, deep-learning and simulation consumers resolved |
| Hub smoke | `./.venv/bin/python scripts/hub_smoke.py --port 0 --timeout 20` | exit 0; temporary port 48545; no persistent hub |
| Remote parity | `git rev-parse HEAD` vs `git ls-remote origin refs/heads/main` | equal when the commands return the same value |

## Conflicts and risks

- `abstain` is intentional. Eight eligible episodes now span four projects, but
  the deterministic split still produced no independent holdout; promoting a
  general route policy would overstate the evidence.
- `data/mak_knowledge.db` and generated research SQLite/report files are local
  operational state and are not Git inventory. Their current state is noted,
  not copied into the web repo.
- Historical phase documents and recovered sessions remain evidence. They are
  not the current handoff and must not override this file.
- A green local check does not prove external GitHub Actions or provider
  credentials. The push completed normally and remote parity was checked;
  external CI remains an independent gate.
- The official P versus NP capture is a normalized curator note, not a
  verbatim source transcript or semantic-equivalence certificate. It supplies
  provenance and hashes but intentionally cannot change `UNTRUSTED`.
- The current `attention` state is intentional and concrete: two ledger
  evidence gaps plus two informational safety states. Do not silence it by
  deleting episodes or promoting same-project data. The Blender dependency is
  no longer an open gap; its fresh audit is verified.
- Watsonx, AWS and Azure historical labels remain in preserved ledgers, old
  visual records, comments and legacy triangulation filenames. They are data
  provenance, not executable integrations. Do not delete or reinterpret those
  records as current provider health. Cerebras remains configured only for
  explicit diagnostic use; its current billing response is HTTP 402 and it is
  not part of the default chain.

## Active cleanup audit — 2026-08-21

Se depuro la configuracion activa para que MAK Linux no presente superficies
Windows obsoletas como si fueran runtime. Se retiraron los lanzadores
`abrir_hub.bat`, `instalar.bat`, `launch-flujo.bat`, `launch-flujo.ps1`, el
puente `tools/bridge_issue_render.py`, sus helpers SendTo y su e2e, y el
workflow Claude deshabilitado. Sus copias historicas siguen en
`/home/mak/WIN` o en la evidencia recuperada. Se retiro solo el test que
ratcheaba esos lanzadores; se conservaron el mirror y los tests de seguridad
que aun tienen consumidores reales.

XIO fue corregido durante la auditoria: no es basura ni se elimina. Se
restauro `.github/workflows/build-xio-apk.yml` como build manual diferido y
se documento como integracion futura Chataigne/OSC para shows, venues y VJ.
No se ejecuta en cada CI ni se confunde con la ruta diaria de FLUJO/RD.

Tambien se actualizaron `CAPACIDADES.md`, `docs/MAK_CURRENT_STATE.md`,
`docs/FLUJO_AREAS_EVENTOS_SUPLEMENTOS.md`, `src/flujo/web/hub.py`, los
paneles web de automatizaciones/eventos, `Makefile`, `pyproject.toml` y los
tests afectados. Se regeneraron `tests/fixtures/idioma_baseline.txt`,
`context/code_structure_index.json` y los HTML de `context/`.

Validacion en primer plano:

- `./.venv/bin/python -m pytest -q` -> exit 0; suite completa, skips esperados.
- Tests focalizados de higiene, contratos Git/web, mirror, GPU, idioma,
  code-index y status -> exit 0.
- `npm run typecheck` en `web/` -> exit 0.
- `npm run build:context` -> exit 0; Node 18 emitio advertencia porque el
  requisito declarado es Node >=20.19, pero el bundle se genero.
- `git diff --check` -> exit 0.

Se agrego `tools/repo_audit.py` como gate read-only del arbol web y las cuatro
SQLite locales. La auditoria real devuelve 36 modulos, 35 alcanzables, 0
muertos, 0 referencias activas obsoletas; `data/rd.db` tiene 20 tablas/7,585
filas, `data/rd_datos.db` 3/0, `data/mak_knowledge.db` 30/369,157 y
`data/flujo.db` 1/6; las cuatro pasan `integrity_check` y todas sus rutas de
consumidor existen. Se corrigio el mapa para no declarar `src/flujo/rd/panel.py`
como lector de `data/rd.db`: el panel lee JSON/YAML canonicos y solo proyecta.

La validacion de `gen_rd_standalone.py` genero en `/tmp` los mismos 6 registros
que `web/src/data/rdDbEmbebida.json`, con SHA-256 identico; el unico fallo
encontrado era el reporte de una ruta absoluta externa y quedo corregido sin
alterar la salida. El intake real uso el indice fuente
`/home/mak/labs/portable-ssd-index-20260813/archivo_index.sqlite`, no el
`intake.sqlite` derivado: con limite 3 y fondo Fondart produjo tres paquetes
`drefgira-fondart`, `felina-logo-fondart` y
`descargas-hasta-rdflyer-2050-fondart` en `/tmp/mak-intake-audit-20260821`.
La salida queda correctamente en `draft_with_evidence_gaps`; no se escribio
la DB de aprendizaje ni se modifico la fuente del SSD.

Riesgos conservados deliberadamente: `tools/mak_ops/check_mak_mirror.py`
todavia contiene una ruta SSH historica y requiere una fase separada de
reemplazo local; `src/flujo/version.py` y `docs/recovered/` conservan
referencias de changelog/evidencia, no runtime. No se borraron `/home/mak/WIN`,
XIO, bases, artefactos ni cambios ajenos.

## Next concrete action

Inspeccionar el diff por grupos y separar los cambios propios de los ajenos
antes de cualquier commit. La verificacion global de esta tanda ya paso:
pytest completo, typecheck web, `repo_audit`, compileall y `git diff --check`.
El mirror SSH historico queda fuera de este slice: no es un consumidor web/DB
activo y no se debe convertir ni borrar sin una fase propia.

## Previous completed checkpoint

The operational DB bridge is complete for the current source contracts. The
master now carries a normalized projection without replacing source authority:
RD events/producers/venues, Fondart v5 applications, intake projects/funds/
packages, and the existing `mak_links` curation surface. The real bridge
returned exit 0, wrote 6,132 normalized records, transferred 106,895 curation
links, copied 0 source rows, and a foreground SQL check resolved
`SCD package -> SCD project -> Fondart -> 12 curation links`.

The foreground `DB -> Research -> Curatoria -> Postulacion` check is complete:
Research exposed 5,179 applications and 14 captures read-only; Curatoria
processed 917 projects, 13,121 families and 45,536 members in a temporary
SQLite copy; Postulacion generated `drefgira-fondart` with explicit evidence
gaps. Exit was 0 and source trees were untouched. Preserve unknown dates as
`date_raw`, accept exact source-key joins as exact, and retain candidate venue
links with confidence.

The DB pipeline and RD event fixture are green. The next action belongs to the
separate operational audit: run the next real consumer/event fixture only if
it represents a different path, and fix only a runtime blocker. Do not start
autonomy, deep learning, broad reindexing or another database until the
declared current consumers are green.

## Last verified

2026-08-21 America/Santiago — web/DB cleanup gate and bounded intake verified;
published in commit `69e7fba` and pushed to `origin/main`:
the active web graph has 36 modules, 35 reachable and 0 dead; stale active
references are 0; `rd.db`, `rd_datos.db`, `mak_knowledge.db` and `flujo.db`
pass read-only integrity checks with all declared consumers present. RD live
and standalone projections are equal by SHA-256. The source-index intake used
the physical SSD index, emitted three bounded Fondart packages in `/tmp`, and
left the source and learning DB untouched. The only runtime defect found was
the standalone generator's absolute-output display path; it was fixed and
focused tests passed. The remaining worktree changes are intentionally outside
that commit and must be handled by the next bounded slice.

2026-08-20 America/Santiago — Python structure index and dual debugging slice
verified: `flujo code-index` generated the source-free 781-module index,
consumer resolution and bounded query brief; focused and full pytest passed,
map synchronization passed, compileall and diff check passed. Watsonx/AWS/Azure
retirement and provider
replacement verified: active registries/chains/UI/configuration removed,
Gemini 3.6 Flash works in both LLM and structured platform adapters, Groq,
Ollama and Firecrawl probes pass, Cerebras returns HTTP 402 and is opt-in only,
four exclusive tools and two env snapshots archived, boto3 dependency removed,
compileall exit 0, full pytest exit 0, pip check exit 0 and diff check clean.
Historical WIN/ledgers/results preserved. Official
P versus NP source/formal hashes
recorded without changing `UNTRUSTED`, Research 4 capture and bounded
simulation were checked without biological claims, 59-contract audit refreshed,
source-learning case preserved, 19-lane cross-domain registry validated
locally, tennis MCP parser/shot-event route and fixture episode passed,
Research 4 capture and logo-clean abstention were linked to Project IR, live
status and full pytest rechecked, and the published baseline remains
`7674c49`/`17ccff7`. The cross-domain write set is not yet published.

2026-08-20 America/Santiago — catalog federation slice verified: focused
tests `3 passed`, py_compile exit 0, diff check exit 0; real metadata-only
federation exit 0; 7 sources, 124 tables, 2,075,337 observed rows, 0 copied;
master integrity `ok`, foreign-key issues `[]`, orphan tables/links `0`.
Added source/target contract files; full suite `./.venv/bin/python -m pytest -q`
completed at 100% with exit 0 (warnings only); no source database contents were
rewritten and no commit or push has been made for this slice.

2026-08-20 America/Santiago — operational bridge slice verified: focused
bridge tests `2 passed`, py_compile and diff check exit 0; real refresh exit 0;
6,132 normalized records and 106,895 curation links; source rows copied `0`;
master integrity `ok`, foreign-key issues `[]`; SQL pipeline sample resolved
application package `SCD` to project `SCD`, fund `Fondart` and 12 curation
links. Seven RD event records retain producer/venue/source payloads; non-ISO
date strings remain unnormalized. Full repository suite completed at 100% with
exit 0; only existing deprecation warnings were emitted.

2026-08-20 America/Santiago — foreground pipeline verified: Research read-only
source exposed 5,179 Fondart applications and 14 captures; Curatoria ran on a
temporary SQLite backup and produced 917 projects, 13,121 families and 45,536
members; Postulacion ran against the existing index and emitted
`drefgira-fondart` with status `draft_with_evidence_gaps`; all commands exit 0,
temporary outputs only, no source mutation. Operational closure comes before
the autonomy phase.

2026-08-20 America/Santiago — RD event fixture audit verified read-only: 7
events all retain producer, raw date, venue and flyer/source evidence; 0 were
forced into ISO dates and 0 curation links are orphaned. No source mutation or
new process remained.
