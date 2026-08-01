# CAPACIDADES.md

Inventario de arranque rapido. Objetivo: empezar un proyecto nuevo (dentro o
fuera de este repo) sin tener que leer/buscar por todo `flujo`. Verificado
contra el repo real el 2026-07-24 (comandos ejecutados, no memoria). Si algo
de aca no calza con lo que ves, el repo cambio despues -- confia en el repo,
no en este doc, y actualizalo en el mismo PR que lo detecte.

## 1. Mapa index del repo

CLI real (`py -m flujo --help`, v0.56.1), comandos principales:

- `app` / `serve` -- hub local (workspace pro). `hub` -- servidor + index/route del arbol de material ($FLUJO_RD_ROOT).
- `job`, `brief`, `intake` -- gestion de jobs y briefs (JSON 1.0).
- `cotizaciones`, `plano` -- cotizacion dual y plano SVG/rider/costos de stands.
- `suplementos` -- contraportadas RD (`svg/suplementos_rd/`).
- `rd-db`, `rd-datos` -- DB consultable RD (reactivos/packs/productoras/venues) + ingesta privacy-first.
- `eventos` -- automatizaciones (incluye `flyer-auto` desde link de Instagram).
- `resolume` -- automatizacion de shows Resolume/Chataigne por SMPTE/OSC (`.noisette`, schema validado contra fixtures reales).
- `laser` -- estetica vectorial para laser/plotter via vpype (externo, opcional): `hatched` (relleno->rayado), `flow` (imagen->campo de flujo, semilla determinista), `lote` (carpeta de material -> svgs + manifiesto que entra al archivo iskvw). Presupuesto de puntos 600-1000/frame integrado; restricciones duras y rig del usuario en `docs/laser/TOOLKIT_INDICE.md`.
- `render`, `analyze`, `export` -- render/validacion de piezas vectoriales, analisis de color/OCR, export ZIP.
- `tapiz` -- pipeline generativo Tapiz<->Psicosis<->Fungi (`tools/compete_engine.py`).
- `datadrop`, `index`, `flyer-import`, `flyer-list`, `ig-redownload` -- ingesta y catalogo de material real.
- `daily`, `handoff`, `portal`, `doctor`, `health`, `verify`, `version` -- operacion y diagnostico del repo.
- `airdrop`, `github-sync` -- entrega sin push directo / sync simple con GitHub.
- `delegate`, `ai-prompt`, `privacy`, `knowledge`, `package`, `init`, `clean`, `brand` (legacy) -- utilidades de soporte.

`tools/` (ejecutables sueltos, 1 linea cada uno):

| Tool | Proposito |
|---|---|
| `becas_calendario.py` | Informes research FOSIS -> calendario de postulaciones (fechas/montos, "no-especificado" si falta). |
| `bridge_issue_render.py` | Puente Windows: issue GitHub label "instagram" -> `flyer-auto` Blender -> drive/. |
| `compete_engine.py` | Pipeline monolitico del ecosistema Tapiz<->Psicosis<->Fungi. |
| `context_pack.py` | Empaqueta contexto minimo (archivos+fence) para pasar a Aider/Qwen/Claude, bajo consumo. |
| `comparar_cobertura_fichas.py` | Dos pasadas de percepcion comparadas campo a campo sobre los MISMOS archivos, filtrando por motor. |
| `consolidar_fichas.py` | Trae una pasada nueva al archivo vivo fusionando CAMPO A CAMPO (lo que la nueva no lleno lo hereda de la vieja); ensayo por defecto. |
| `ig_metadatos.py` | Saca del export de Instagram la FECHA exacta y el TEXTO que el artista escribio sobre cada obra, reparando el encoding. |
| `drenar_material.py` | Vacia la cola de trabajo de MAK en paralelo y cuenta lo que salio; se detiene solo si el buscador queda ciego. |
| `contexto_repo.py` | Digest mecanico del repo (0 tokens): arbol + archivos clave. `map` / `task "<keywords>"`. |
| `enviar_a_mak.py` | Puente WIN->MAK: envia carpeta a `~/curatoria_inbox/` via tar\|ssh, verifica conteo/bytes. |
| `gen_vinculos_iskvw.py` | Vinculos entre obras desde los conceptos de las fichas, con los conceptos compartidos como motivo. |
| `gen_mapa_comandos.py` | Genera la tabla de comandos de `MAPA.md` desde el `--help` real del CLI (`--check` falla si quedo desfasado). |
| `handoff.py` | Borrador de cierre de sesion desde git+pyproject (no sobreescribe). |
| `instalar_enviar_a_mak.py` | Instala integracion "Enviar a" -> MAK curatoria en el explorador de Windows. |
| `render_video_rd.py` | Mete un mp4 (reel) en `RD.paravideo.blend` y exporta H264 headless. |
| `system_map.py` | Blueprint de arquitectura del ecosistema Tapiz/Psicosis/Fungi (schema API_CONTRACT). |
| `tapiz_live_loop.py` | Daemon-poller que corre `compete_engine` en modo `--live` a intervalo fijo. |
| `tapiz_telemetry.py` | Construye el autorretrato en vivo del ecosistema (`system_status.json`). |
| `gen_animadas_obras.py` | Cada obra curada -> su pieza animada por el motor semantico, determinista desde el id (misma obra = misma pieza); escribe `iskvw/piel/animadas/*.svg` + `iskvw/datos/animadas.json`, que `contrato_archivo.desde_animadas` mete al archivo vinculada a su obra. `tests/test_gen_animadas_obras.py`. |
| `token_budget.py` | Estima tokens de un set de archivos antes de mandarlos a un modelo. |
| `venue.py` | Base abierta de venues para VJ/tecnica: `sembrar` (una linea por sala) -> JSON validado contra `schemas/venue.schema.json` con tier de `confianza` por dato, `validar`/`listar`/`sitio` (HTML autocontenido consultable desde telefono) y `geometria` (reporte numerico del bloque de polilineas: aristas por tier y por capa, bounding box, cierres, segmentos de largo cero, cota declarada vs dibujada). `tests/test_venue.py`. |
| `venue_geometria_scd.py` | Sala DEMO en polilineas 3D (bloque `geometria` del esquema) derivada del modelo radial del teatro SCD Plaza Egana -> `data/venues/scd-plaza-egana.json`, material por defecto del visor `iskvw/piel/venue/`. |
| `venue3d_smoke.mjs` | Corre el JS del visor de salas en node con stubs de DOM: geometria cargada, aristas realmente trazadas, la proyeccion se mueve al orbitar, el recorte por presupuesto se reporta en pantalla, la camara por URL llega, y la orbita de ejemplo (`data/orbitas/`, `schemas/orbita.schema.json`) reproduce la vuelta por defecto cuadro por cuadro. `tests/test_venue3d_smoke.py`. |
| `venue_secuencia.mjs` | Exporta la orbita de una sala como N SVGs de puras lineas desde la MISMA proyeccion del visor; `--orbita <archivo.json>` toma el recorrido de camara como dato (keyframes giro/alto/dist, validados numericamente antes de cortar un solo cuadro). |
| `verify_all.py` | Verificacion del repo en un comando: compileall + pytest + `flujo verify` (opcional `--web`). |

`xio/` (server telefono + show kit): server Flask (`xio/actual/server.py`,
`xio/new/server.py`) corre ON-DEVICE en Termux (Shizuku/rish) en el Xiaomi,
puerto 5000 (`XIO_PORT`), 63 archivos de plugins (controlador Xiaomi, hotspot
router activo con auto-heal, FOH monitor). Runbook: `xio/RUNBOOK.md`,
`xio/FACES.md` (Face A hogar vs Face B show telefono-solo),
`xio/HOTSPOT_SHOW_RUNBOOK.md`, `xio/show_kit/`.

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

## 2. Modelos y APIs disponibles (sin llaves)

Solo existencia + donde se configura. Nunca el valor de una llave.

| Integracion | Que es | Donde vive la config |
|---|---|---|
| Claude / Anthropic | Director (Fable/Opus) + subagentes Sonnet/Haiku; tiers en tabla de `CLAUDE.md` | `ANTHROPIC_API_KEY` en `.env` (ver `.env.example`); ejecutado via Claude Code CLI, no en runtime del repo |
| ollama LOCAL en MAK | Modelos chicos, throughput-first, capa "barato" | corre en el runner MAK; consumido desde `cultura/mak_research/research_lib.py` (`_SLOTS`); modelos instalados verificados via `ssh mak@192.168.50.2 "ollama list"` (2026-07-24): `deepseek-coder:6.7b`, `nomic-embed-text:latest`, `gemma3:4b` |
| ollama en WIN (workship) | Instancia LAN en Windows, usada por MAK cuando conviene (`provider 'win'`) | `OLLAMA_HOST=192.168.50.1:11434`; ver `context/LAST_HANDOFF.md` para historial de arranque/persistencia |
| Groq | Proveedor rapido para roles `razonar`/`bulk` | `GROQ_API_KEY`, `GROQ_MODEL` en `cultura/mak_research/research_lib.py` (defaults linea 32) y `.env` |
| Cerebras | Proveedor rapido, `CEREBRAS_MODEL=gpt-oss-120b` | `CEREBRAS_API_KEY`, `CEREBRAS_MODEL` en `research_lib.py` (linea 33) y `.env` |
| Azure AI (gpt-5-mini) | Slot "capaz" para razonar/juzgar/sintesis en MAK research | `AZURE_ENDPOINT`, `AZURE_DEPLOYMENT`, `AZURE_API_KEY` en `research_lib.py` (lineas 34-35) y `.env` |
| DashScope / Qwen | Coder barato de volumen (gate, nunca directo a Claude) | `DASHSCOPE_API_KEY` / `QWEN_API_KEY` en `.env.example` |
| NVIDIA NIM | Alternativa barata (Qwen/DeepSeek/Nemotron) | `NVIDIA_API_KEY` / `NVIDIA_NIM_API_KEY` en `.env.example` |
| OpenRouter | Router/fallback de modelos | `OPENROUTER_API_KEY` en `.env.example` |
| Gemini | Voz (`tools/vibo_voz`) + vision flyer->productora; PARKED como asistente principal desde 2026-07-10 (429, MAK research lo reemplaza en ese rol) | `GEMINI_API_KEY` / `GEMINI_API_KEY_2` en `.env.example` |
| SearXNG (LAN, en la caja) | La busqueda de research. Sin llave, sin tope de creditos | `SEARXNG_BASE_URL` (default `http://127.0.0.1:8888`) y `SEARXNG_ENGINES` (vacio = los motores que tenga la instancia). **Medido 2026-08-01 y CORREGIDO el mismo dia.** Los cuatro motores generales (brave, duckduckgo, google cse, startpage) se tapan a la vez con CAPTCHA / "too many requests", y SearXNG contesta HTTP 200 con cero resultados. Es INTERMITENTE: la misma consulta dio 20 resultados en una ventana y 0 un minuto despues, con los cuatro caidos. Por eso la deteccion de ceguera (`ciego` + `motivo`) es el instrumento que corresponde: distingue las ventanas en vez de promediarlas. **Lo que NO sirve es fijar motores a mano.** El primer intento de este mismo dia puso `SEARXNG_ENGINES=bing,mojeek,wikipedia` porque contaba RESULTADOS; contando RELEVANCIA, `bing` devolvia basura no relacionada y distinta en cada llamada para la misma consulta (mulching en Charlotte, defensemirror, robertsspaceindustries), aunque funciona bien para consultas simples tipo "gato negro". Con esa lista fija, `refutar` produjo un informe con 5 fuentes que hablaban todas de Google Gemini: peor que ciego, porque parece documentado. Revertido en la caja. La variable existe y se puede usar, pero NO hay lista por defecto y el que la ponga tiene que mirar los resultados, no contarlos |
| Tavily | Respaldo de busqueda cuando SearXNG no devuelve nada | `TAVILY_API_KEY`; **no esta puesta en la caja** (verificado 2026-08-01), asi que hoy no hay respaldo: si SearXNG queda ciego, la cadena entera queda sin ojos y `refutar` se detiene con un muro en vez de firmar un informe sin fuentes |
| Arena (LMArena) | Frontier gratis on-demand para arquitectura dura, sin API | manual, sin config en repo; ver skill `toma-de-decisiones` |
| parth-dl (IG) | Descarga real de posts/reels de Instagram (via primaria desde 2026-07-22) | `pip install parth-dl`; usado en `src/flujo/eventos/flyer_auto.py` y `src/flujo/ig/download.py`; imginn.com solo fallback (403 Cloudflare), instaloader NO funciona (IG exige login), NO yt-dlp |
| Blender 4.5 | Render headless (flyer video, Chataigne prep) | WIN: `C:\Program Files\Blender Foundation\Blender 4.5\blender.exe` (OptiX, RTX 4070); MAK: `~/blender/` tarball portable 4.5.3 LTS (CUDA, GTX 1650) |
| Chataigne builder | Genera `.noisette` para Resolume/Chataigne | `src/flujo/resolume/automator.py::build_chataigne_noisette_experimental`; schema validado contra fixtures reales (`tests/fixtures/chataigne_1103_real*.noisette`, `tests/test_noisette_real_fixture.py`) -- nunca especular, la fixture manda |
| rclone / OneDrive en MAK | Entrega de renders (Drive de Google via `gdrive:` remote) | systemd `onedrive-rclone.service` en MAK; detalle en `context/LAST_HANDOFF.md` y `src/flujo/version.py` (changelog) |
| GitHub (gh CLI + runner self-hosted + workflows) | CI, gate de PRs, ordenes de curatoria, publicacion catalogo/portfolio | `gh` CLI local; runner self-hosted `mak` (online, labels `self-hosted,Linux,X64,mak,eventos`, verificado via `gh api repos/.../actions/runners`); workflows activos en `.github/workflows/`: `ci.yml`, `claude.yml`, `airdrop_gate.yml`, `issue_descarga_ig.yml`, `ordenes_curatoria.yml`, `render_piezas_vectoriales.yml`, `validar-piezas.yml`, `build-xio-apk.yml` |

Vtracer / curl_cffi / imageio_ffmpeg: usados puntualmente en pipelines de
render/vectorizacion cuando hace falta, instalados ad-hoc (`pip install
<paquete>`) -- no son dependencias fijas de `pyproject.toml`/`requirements.txt`
(esas listan solo el core: matplotlib, pyyaml, pydantic, typer, rich,
jsonschema, requests).

## 3. Infraestructura

| Nodo | Rol | Detalle |
|---|---|---|
| WIN (este equipo) | Desarrollo, GPU OptiX (RTX 4070), Blender 4.5, Python via `py` | Repo principal `C:\IA\flujo`; ollama opcional en `192.168.50.1:11434` |
| MAK (dell-11m) | Organismo autonomo, GPU GTX 1650 (CUDA), ollama residente, runner self-hosted GitHub, crons del organismo | `ssh mak@192.168.50.2` (llave autorizada, verificado en vivo); `~/plataforma/` = espejo de `cultura/mak_plataforma/`; Blender 4.5.3 LTS portable en `~/blender/` |
| xio (Xiaomi, HyperOS) | Server Termux 63 plugins, hotspot router activo (32 clientes, sin AP isolation), FOH monitor show | on-device Shizuku/rish, puerto 5000; ver `xio/RUNBOOK.md` |
| OneDrive / Google Drive | Storage de entrega de renders | rclone en MAK (`onedrive-rclone.service`), remote `gdrive:` |

## 4. Como arrancar proyecto nuevo (receta)

1. Leer `CLAUDE.md` + este `CAPACIDADES.md` + `context/LAST_HANDOFF.md`. Nada mas antes de empezar.
2. Clasificar la ruta destino: nucleo vivo / operacion diaria / historico / generado (ver mapa de `CLAUDE.md`) antes de tocar nada.
3. Elegir linea de trabajo: `rd` (ONG/datos/becas), `portafolio` (curatoria/iskvw), `mejoras` (repo/MAK/infra). Nunca contra `main` directo.
4. Si toca produccion aislada: worktree propio (`EnterWorktree`/`git worktree add`), rama desde `origin/<linea>`.
5. Elegir el modelo mas barato que resuelva la tarea (tabla seccion 2 + `CLAUDE.md` "Regulacion de gasto"); escala solo si aplica un trigger.
6. Si es pieza cultural nueva: aplicar motor-omega (Omega11 declarada + fracaso no se reinterpreta) antes de exponer.
7. Cambios minimos, completos, verificables -- nada a medias, nada de TODO/placeholder.
8. Verificacion minima segun area tocada (Python: compileall+pytest+`flujo verify`; Web: typecheck+build:context; Airdrop: validate_airdrop+run_airdrop_checks).
9. Entregables (datos/docs/piezas) en espanol correcto UTF-8; `CLAUDE.md`/`context/*.md` operativos en ASCII.
10. PR contra la linea correspondiente, CI verde obligatorio -- promocion a `main` la hace el director via PR curado.

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
| `cultura/mak_vigia/vigia.py` | VIVO | cron `MAK-VIGIA` (`vigia_guardia.sh`, cada hora, lock propio `.vigia.lock`); notifica por ntfy a `VIGIA_NTFY_TOPIC` y, para las fuentes `tipo: enfermeria`, a `VIGIA_NTFY_TOPIC_ENFERMERIA`. Es un DIFF, no un LLM: descarga -> normaliza -> sha256 -> compara contra `estado/vistos.jsonl` -> notifica solo lo nuevo; cero tokens, cero GPU, ningun modelo. Regla de oro: una fuente que pasa a parsear CERO items, o que lleva 4 dias sin nada nuevo, dispara notificacion de ERROR en prioridad alta -- el silencio no puede parecerse a "funciona". Corrida real 2026-07-30 sobre las 6 fuentes de `fuentes.json`: 430 items, segunda corrida 0 nuevos y 2 fuentes en 304. `tests/test_vigia.py` (32 tests) | 2026-07-30 |
| `becas_calendario.py` | VIVO | RD becas, area operativa | 2026-07 |
| (las 33 utilidades del buzon `mak`) | LEIDAS 2026-08-01, NO ENTRAN | Llevaban dias en la rama `mak` sin que nadie las abriera, porque el muro que las describia decia que main ya las habia rechazado y era falso (ver `context/LAST_HANDOFF.md`). Leidas una por una: **9 invocan `subprocess`** para ejecutar `backlog_codex`, tocar `/etc` o instalar cron jobs -- son ORDENES OPERATIVAS disfrazadas de utilidad, justo lo que el clasificador de rutas de #406 salio a frenar. **~10 son de sandbox** por debajo de 1 KB ("Script de ejemplo para el sandbox", 406 bytes). **3 traen surrogates invalidos** (\udc81, \udc8f): no son UTF-8 y revientan al leerlas, pero PASARON el gate de MAK porque `revisor.gate_compila` compila el texto ya decodificado en la caja -- ese gate es ciego al encoding, y ese es el hallazgo que deja la lectura. Y **4 sirven** (OSC 1.0 con `struct`, verificador de puertos TCP, estadistica de columna CSV, validador JSON), probadas corriendo. Se trajeron al repo y se devolvieron el mismo dia: renombrarlas rompio `test_capataz_enrutamiento`, que usa los NOMBRES de esa carpeta como fixture de los pedidos reales que causaron el defecto, y sus comentarios en castellano encienden el ratchet de idioma. Sin consumidor no compensaban ninguna de las dos cosas. Lo que valia era saber que hay adentro, y eso queda escrito aca | 2026-08-01 |
| `idioma.py` | VIVO | measures the language of comments/docstrings in every tracked `*.py` (es/en/mixed/none, transparent stdlib heuristic, `git ls-files` only, archive and vendorized zones excluded); measured consumer: `tests/test_idioma_ratchet.py`, the ratchet that pins `tests/fixtures/idioma_baseline.txt` so no NEW file adds Spanish comments while renames are never demanded; real run 2026-07-31: 581 files = 388 es + 96 en + 38 mixed + 59 none; also prints a soft FYI of widespread Spanish identifiers missing from `docs/GLOSSARY.md` | 2026-07-31 |
| `bridge_issue_render.py` | VIVO | puente issue -> render WIN | 2026-07 |
| `compete_engine.py` | VIVO | proyecto tapiz (cultura) | 2026-07 |
| `context_pack.py` | REVISAR | AI Op Layer 2026-07-25, recien creado, consumidor pendiente | 2026-07-25 |
| `comparar_cobertura_fichas.py` | VIVO | compara dos pasadas de `percepcion.py` campo a campo SOBRE LOS MISMOS ids (lo que no esta en ambas no se cuenta) y filtra por `medicion.vision.motor`, para que una pasada con fallback no le acredite a watsonx lo que respondio ollama; corrida real 2026-08-01 sobre 923 fichas ig, v1 gemma3 vs v4 watsonx: `tipo_obra` 51.9%->100%, `materiales` 68.7%->99.6%, `colores` 95%->100%, y la unica caida real `oportunidad_codigo` 99.1%->75.9% (watsonx omite la clave en 225 imagenes; ninguna de las dos pasadas era plantilla: 1258 y 640 valores distintos) | 2026-08-01 |
| `consolidar_fichas.py` | VIVO | mete una pasada nueva de `percepcion.py` en el `fichas.jsonl` vivo sin perder lo que la vieja sabia: la fusion es CAMPO A CAMPO porque el reemplazo por fila destruye datos medidos -- la pasada de watsonx llena `tipo_obra` del 67% al 100% pero deja `oportunidad_codigo` vacio en 225 imagenes donde el modelo chico habia escrito una. La mezcla se DECLARA en `medicion.vision.heredado` + `motor_heredado`: una ficha con campos de dos motores y sin registro de cual vino de cual es peor que cualquiera de las dos pasadas sola. Ensayo por defecto; `--aplicar` respalda con sello de tiempo, escribe a un temporal y lo valida ANTES de pisar el vivo. Ensayo real 2026-08-01 sobre 3.138 fichas: 1.354 fichas reemplazadas, 1.482 campos mejorados, 397 heredados, **9.348 pisados (4.595 de ellos quedando MAS CHICOS)** y 0 que queden vacios habiendo tenido valor. Ese cuarto numero es el que faltaba: la primera version contaba tres casos sobre un test de PRESENCIA y cubria 1.879 de 17.602 decisiones, imprimiendo `campos perdidos: 0` como compuerta -- un cero que solo podia dar cero. Lo encontro una revision adversarial midiendo el archivo real, no un fixture. La atribucion es POR CAMPO (`heredado: {campo: motor}`) porque un motor por ficha pierde el rastro en la segunda fusion, y `comparar_cobertura_fichas.py` ya no cuenta como llenos los campos heredados: sin eso, medir el archivo fusionado le acreditaba a watsonx el 100% de `oportunidad_codigo` cuando lo real es 77,9%. Escribir exige que NO haya percepcion corriendo (`pgrep`) y toma `flock`: una ficha apendeada en la ventana desaparece del vivo y queda marcada en `procesados.txt`, que es lo unico irreversible de la operacion | 2026-08-01 |
| `ig_metadatos.py` | VIVO | consumidor medido: `percepcion.py correr --meta-ig`, que mete el texto del artista en el prompt de vision. Saca del export de Instagram el mapa archivo -> {fecha, texto}. Medido sobre el export real 2026-08-01: 1.125 archivos mapeados, 1.014 con texto propio (90%), 1.125 con fecha exacta, rango 2018-11-29 a 2026-06-16; casan 1.124 de las 1.401 fichas ig (80%). Repara el mojibake del export (Instagram escribe UTF-8 y el export lo decodifica como latin-1: `coleccion` llega como `colecciA3n`) quedandose con la version de MENOS marcas, y lo que no pudo recuperar lo marca en vez de entregarlo como si estuviera bien. Lee SOLO `your_instagram_activity/media/`: al lado viven mensajes privados, likes e interacciones de historias, y toda ruta que pase por ahi se rechaza por nombre; `tests/test_ig_metadatos.py` | 2026-08-01 |
| `contexto_repo.py` | VIVO | referenciado en `CLAUDE.md` ("Ahorro de contexto") | 2026-07-25 |
| `conversacion.py` | VIVO | tercer hermano de `arqueologia.py` (historial de git) y `esfuerzo.py` (costo de un informe): lee las transcripciones de `~/.claude/projects/` como corpus. Nadie las escribio para eso, y contienen lo unico que el repo no tiene -- lo que el usuario decidio, ordeno y tuvo que repetir. Consumidor medido: `clasificar` manda los lotes a watsonx y `citar` recupera la cita TEXTUAL por indice, porque una decision parafraseada deja de ser la decision. Corrida real 2026-08-01 sobre 126 sesiones: 17.629 turnos con texto, de los cuales **3.094 escritos por un humano** (0,7 MB) contra 12.197 del asistente (5,6 MB); 39,2 MB del corpus son `tool_result` y no entran. Dos defectos propios encontrados MIDIENDO, no leyendo: (1) la primera version decidia por una lista de prefijos escrita a mano quien era humano, la lista dejo de coincidir con la realidad y los resumenes de compactacion se comieron los 30 primeros puestos -- ahora lo dice `origin.kind`, que el registro ya trae; (2) los lotes se dimensionaban por la ventana de ENTRADA (95k) y los 3 primeros lotes agotaron los 8.000 tokens de SALIDA devolviendo JSON cortado, asi que el tope real es la salida. Un lote sin JSON legible se cuenta como FALLO y nunca como lista vacia. El hallazgo que no cuesta un token es la repeticion entre sesiones DISTINTAS: `users issvk downloads` en 13, `claude teleport session` en 9, `compileall src flujo`/`pytest tests`/`flujo verify` en 6, `api key nvidia` en 6 -- constantes que hay que re-pegar cada sesion porque no estan escritas | 2026-08-01 |
| `drenar_material.py` | VIVO | vacia `~/plataforma/material.jsonl` en paralelo mientras dure la ventana pagada -- `trabajo.py` saca UNA tarea por invocacion y corre por cron, o sea meses para 2.730 tareas. Escribe a su propio directorio y NO a la base de RD: una productora identificada por un modelo es un candidato, no un cliente. Lo pausado o fallido VUELVE a pendiente (una cola que se vacia sin haber trabajado es la peor forma de decir que termino) y aborta el lote entero si se acumulan pausas por ceguera. Informa la DISTRIBUCION, no un total: "412 hechas" no dice nada, "412 hechas, 180 con productora y fuente, 190 NO SE ENCONTRO, 42 pausadas ciegas" si. Corrida real 2026-08-01: 8 tareas, 7,6 s cada una con 4 hilos | 2026-08-01 |
| `gen_archivo_iskvw.py` | VIVO | genera `iskvw/datos/archivo.json`, el contrato piezas+vinculos; consumidor confirmado 2026-08-01 via `curl https://iskvw.cl/datos/archivo.json` (HTTP 200, 479 piezas, 269 vinculos) -- lo sirve `.github/workflows/publicar_iskvw.yml`. La conversion micelio->contrato vive en `cultura/mak_plataforma/contrato_archivo.py` desde 2026-07-29, compartida con `GET /api/archivo` del hub de MAK. Ese workflow corre en `ubuntu-latest` y nunca alcanza la caja (LAN privada) -- medido el mismo dia sobre lo publicado: 0 de los 269 vinculos eran `clase: "semantico"`, todos tag-derivados o declarados a mano. Desde 2026-08-01 `--fuente todo` cae a `iskvw/datos/micelio.json` cuando el micelio en vivo no responde: un snapshot ya convertido que empuja `cultura/mak_plataforma/entregar_micelio.py` corriendo EN la caja (mismo patron de `entregar.py` -- git + `gh pr create` contra la rama `mak`), porque solo ella puede alcanzarse a si misma; hard-falla (exit 1, nada escrito, ningun PR) si el micelio no responde o devuelve 0 vinculos -- una ausencia nunca se vuelve un cero plausible. `tests/test_contrato_archivo.py`, `tests/test_gen_archivo_iskvw.py`, `tests/test_entregar_micelio.py` | 2026-08-01 |
| `gen_propuestas_rd.py` | VIVO | el ultimo salto a la base RD: alimenta el escritor de borradores de `mineria_rd.py` desde `docs/rd/candidatos_curatoria/candidatos_db.jsonl` (ya digerido por `extraccion_db`), sin OCR ni GPU; re-matchea contra los catalogos ACTUALES, reporta dudosos sin proponerlos y exige evidencia >= 2; los borradores salen a una carpeta aparte y entran solo por PR humano; `tests/test_gen_propuestas_rd.py` | 2026-07-29 |
| `gen_rd_standalone.py` | VIVO | hornea la base RD en `herramientas_rd.html` (bundle sin servidor), `npm run build:rd` | 2026-07-27 |
| `enviar_a_mak.py` | VIVO | SendTo WIN -> MAK, probado e2e 2026-07-23 | 2026-07-23 |
| `gen_dashboard_productoras.py` | VIVO | genera `db_productoras.html`; documentado en `docs/rd/DB_PRODUCTORAS_ESTADO.md`; consume la salida de `triangular_fichas.py` | 2026-07-25 (llega a main con la promocion de `rd`, PR #303) |
| `gen_presentacion_db.py` | VIVO | genera `docs/rd/presentacion_db.html`, la pieza formal para la directiva RD; documentado en `docs/rd/DB_PRODUCTORAS_ESTADO.md` | 2026-07-25 (llega a main con la promocion de `rd`, PR #303) |
| `gen_propuesta_directiva.py` | VIVO | genera `docs/rd/propuesta_directiva.html`, la propuesta a la directiva (que ofrece RD, con que cuenta, como protege los datos y que necesita aprobar); lee `data/rd.db`, asi que ninguna cifra se escribe a mano | 2026-07-26 |
| `vendorizar_iskvw.py` | VIVO | empaqueta librerias npm como modulos ESM autocontenidos + su README al lado, para paginas estaticas que no pueden depender de un CDN ni de un build. DOS manifiestos: `data/iskvw_librerias.json` -> `iskvw/piel/lib/` (4 de thi.ng) y `data/motor_librerias.json` -> `docs/cultura/lib/` (hiccup, hiccup-svg, color, para el compilador de navegador del motor semantico). `tests/test_iskvw_librerias.py` las importa en node y les pide trabajo; `tests/test_thing_registro.py` cruza los manifiestos con la seccion 6. Dos arreglos 2026-07-30: `--destino` se resuelve absoluto (esbuild corre en un temporal y perdia el bundle) y el chequeo de huerfanos solo mira bundles vendorizados (los `.js` escritos a mano en el destino se reportaban como sobrantes) | 2026-07-30 |
| `iskvw_piel_smoke.mjs` | VIVO | ejecuta el JS real de la piel del campo en node con stubs de DOM, recorre el campo para que el codigo por-nodo corra de verdad, y sale distinto de cero ante cualquier error (incluidos los async); existe porque #403 dejo `destino`/`dy` fuera de scope y todo pytest siguio verde con el portafolio muerto en el primer frame; consumido por `tests/test_iskvw_piel_smoke.py`. Desde el patch de efectos tambien lo MIDE: arranca la piel tres veces -- sin `datos/tablero.json`, con el tablero publicado (llave maestra apagada) y con la llave encendida -- y exige que las dos primeras dibujen marca por marca lo mismo y que la tercera deforme de verdad (posiciones desplazadas, colores corridos, la lectura arrastrada por la gravedad). Ademas corre cada llave por-efecto A SOLAS y exige la firma que solo ese efecto deja, y verifica que la capa de sala (`mejoras.venue3d`, mismo fetch del tablero) aparezca exactamente cuando la llave lo dice. Una llave que se publica apagada es codigo que nadie mira: por eso se mide en CI y no se declara | 2026-07-31 |
| `validar_curaduria.py` | VIVO | valida `iskvw/datos/curaduria.json` (y `tablero.json`) contra el esquema que lee `aplicar_curaduria()` y contra el archivo real en disco: ids desconocidos o duplicados, campos invalidos, svg firmado ausente, diacriticos mutilados (la clase de defecto "reduciendo ano") -- todo lo que el consumidor traga en silencio, dicho en voz alta antes de commitear. Salida medida (ERROR/AVISO), exit 1 con errores: sirve en CI. Consumido por `tests/test_validar_curaduria.py` (que ademas corre el CLI sobre los archivos reales del repo) y `tests/test_curaduria_roundtrip.py` | 2026-07-31 |
| `gen_vinculos_iskvw.py` | VIVO | vinculos entre obras CON EL MOTIVO adentro, sacados de los conceptos que la percepcion extrajo y que nadie usaba (7.985 menciones). `gen_archivo_iskvw.py` vincula por etiqueta compartida y lo declara: "nadie midio que se parezcan, comparten una palabra"; esto declara `clase: concepto` y lista los conceptos compartidos en `porque`, asi que el vinculo se puede refutar. Medido antes de escribirlo: 1 concepto compartido da 31.992 pares sobre 1.359 obras (una maraña), 2 dan 1.851 vinculos que alcanzan 863 obras (64%). Tres exclusiones, todas CONTADAS y reportadas -- conceptos en una sola obra (819, no vinculan nada), los mas frecuentes (uno en 305 obras es una CATEGORIA) y los que pasan `--tope-obras`. El pliegue de plural/tilde es para AGRUPAR: `porque` muestra la grafia que el modelo escribio, porque `patrone geometrico` es una llave y no una palabra. `tests/test_vinculos_iskvw.py` | 2026-08-01 |
| `gen_capas_iskvw.py` | VIVO | corre las capas de `data/iskvw_capas.json` sobre `iskvw/datos/campo.json` y deja un dato medido por obra (hoy `tilde`, el residuo diacritico de lo percibido via `tools/tilde_meter.py`, y `trazo`, la densidad del vector); sumar una capa es una entrada mas y una funcion, sin tocar la piel; `tests/test_capas_iskvw.py` | 2026-07-27 |
| `gen_campo_iskvw.py` | VIVO | genera `iskvw/datos/campo.json`, las posiciones del campo de iskvw; proyecta los embeddings del micelio de MAK con t-SNE (48.9% de vecindad conservada, medido contra PCA 3.8% y fuerzas 16.4%) y toma que tipos entran de `data/iskvw_campo_filtro.json`; consumido por `iskvw/piel/campo/index.html` | 2026-07-27 |
| `gen_iskvw_prototipo.py` | VIVO | genera `docs/iskvw/prototipo.html`, el prototipo del portafolio ISKVW; lee `tools/portfolio/proyectos.json` y mide el repo al generar, sin telemetria decorativa | 2026-07-26 |
| `triangular_fichas.py` | VIVO | triangula `fichas.jsonl` de MAK en eventos + productoras candidatas; consumido por `gen_dashboard_productoras.py` y `gen_presentacion_db.py` | 2026-07-25 (llega a main con la promocion de `rd`, PR #303) |
| `gen_mapa_comandos.py` | VIVO | genera el bloque de comandos de `MAPA.md`; `tests/test_mapa_completo.py` exige que el mapa cubra todo el CLI | 2026-07-25 |
| `watsonx_smoke.py` | VIVO | verificador de solo lectura de IBM watsonx: cambia la API key por bearer IAM, lista modelos, hace UNA llamada de chat real y calcula el costo. Consumidor medido: `cultura/mak_research/research_lib.py` `_watsonx` -- el metodo se pego DESPUES de que esto diera 4/4 contra la cuenta real (2026-07-30: bearer 460 ms, 24 modelos, chat 681 ms, 58 tokens = $0.000044), y esa es la regla: no se agrega un proveedor que no se probo. Sin `WATSONX_API_KEY` en el entorno no hace nada y lo dice | 2026-07-30 |
| `watsonx_coder_bench.py` | VIVO | decide QUE modelo de watsonx encabeza la cadena de coder, ejecutando la respuesta de cada candidato contra seis casos en vez de leer su ficha. Consumidor medido: `cultura/mak_codex/codex_lib.py` `_CODER_CHAIN_DEFAULT`, cuyo orden sale de esta corrida y lo dice en su comentario. Hallazgo de la primera corrida real (2026-07-31, cuenta del usuario): de cinco candidatos el UNICO etiquetado `code` (`granite-8b-code-instruct`) fue el UNICO que fallo un caso -- no descarta el tramo invalido. Elegir por el nombre habria puesto el peor primero. Sin `WATSONX_API_KEY` no hace nada y lo dice | 2026-07-31 |
| `watsonx_vision_smoke.py` | VIVO | sonda de solo lectura: manda UNA imagen real del corpus con el prompt real de percepcion y muestra la respuesta CRUDA. Existe porque la capacidad de vision de los modelos de la cuenta se habia inferido del NOMBRE -- `task_ids` no declara tarea de vision -- y aca no se cablea un proveedor que no se probo (misma regla que `watsonx_smoke.py`). Corrida real 2026-07-31 sobre un flyer de Club Hipico: los TRES candidatos aceptaron la imagen (36-44 s) y sacaron venue, fecha y 4 headliners del propio flyer. Consumidor medido: decide si `watsonx_vision()` se escribe o si el plan de re-percepcion cambia entero | 2026-07-31 |
| `watsonx_vision_bench.py` | VIVO | decide QUE modelo de vision lee el archivo, con dos verdades de referencia que ya estaban en disco y nadie usaba: el OCR de tesseract (no vacio en el 24% de las fichas) y la ficha que hizo `gemma3:4b`. Muestra ESTRATIFICADA -- mitad con OCR, mitad de las que hoy vuelven vacias, que son el 76% y el motivo entero. La invencion cuenta EN CONTRA: un campo lleno solo puntua si su valor aparece en el OCR o en la ficha de hoy. Consumidor medido: el default de `WATSONX_VISION_MODEL` en `research_lib.watsonx_vision`. Corrida real 2026-07-31: el unico modelo llamado `vision` fue el PEOR (solape 0.414, 3 inventados, 40k tokens) contra mistral-small (0.807, 0 inventados, 7.7k) -- ese numero salio con `--muestras 8` y con el banco reescalando a 1024, que NO era lo que corre produccion. Corrida 2026-08-01 con `--lado`, misma muestra determinista de 12 y mismo modelo: 1024 -> solape 0.642 / 12.2k tokens; 1280 -> solape **0.761** / 16.4k tokens; misma latencia (2.2 s) y 0 inventados en ambos. Los 256 px extra compran +18.5% de lectura por +34% de tokens: produccion se queda en 1280 | 2026-08-01 |
| `verificar_piel_honesta.mjs` | VIVO | sonda de navegador real (headless, nunca una ventana) para las cuatro afirmaciones de la piel campo que el 2026-07-30 se vendieron mas fuertes que su evidencia: el gesto de quedarse quieto nunca se ejercito de verdad, las letras doublecup nunca se VIERON, el regimen industrial nunca se manejo desde el ARCHIVO, y los fps nunca se tomaron en el estandar declarado (viewport de telefono, CPU x4). Consumidor: el operador antes de afirmar cualquiera de las cuatro; no es test de CI porque necesita el sitio servido. `playwright-core` NO es dependencia del repo -- se resuelve por `PLAYWRIGHT_CORE` o instalacion normal, y sin el la herramienta dice como instalarlo en vez de morir | 2026-07-31 |
| `handoff.py` | VIVO | genera/actualiza `docs/handoffs/` + `context/LAST_HANDOFF.md` | 2026-07 |
| `iconos_conjunto.py` | VIVO | valida y construye la galeria de un CONJUNTO de iconos (`--raiz`, sirve a cualquiera, no solo al del ensayo rave); consumidor medido: `docs/cultura/ensayos/rave/` (16 iconos, 0 errores) y el anexo iconografico que exige `docs/cultura/FORMATO_ENSAYO.md`; `tests/test_iconos_conjunto.py` | 2026-07-30 |
| `gen_vocabulario_motor.py` | VIVO | exporta el vocabulario del motor semantico (22 figuras/12 gestos/9 tonos) a `docs/cultura/lib/vocabulario.json` para que el MISMO spec compile en el navegador sin re-portar la geometria a mano; consumidor: `docs/cultura/lib/compilador.js` + el taller de la galeria; `--verificar` falla si quedo viejo respecto de `vocabulario.py`; `tests/test_compilador_navegador.py` | 2026-07-30 |
| `instalar_enviar_a_mak.py` | VIVO | instalador del SendTo de `enviar_a_mak.py` | 2026-07-23 |
| `render_video_rd.py` | VIVO | pipeline video RD, 4 ejes, semana 2026-07-21 | 2026-07-21 |
| `system_map.py` | VIVO | mapa mecanico del repo (soporte de `contexto_repo.py`) | 2026-07 |
| `tapiz_live_loop.py` | REVISAR | cultura, decision de uso pendiente del usuario | sin fecha medida |
| `tapiz_telemetry.py` | REVISAR | cultura, decision de uso pendiente del usuario | sin fecha medida |
| `tilde_meter.py` | VIVO | `projects/cultura/tilde_paridad.py` + `tests/test_tilde_meter.py` + `tests/test_tilde_render.py`; area Cultura de CLAUDE.md | 2026-07-25 (movido de desktop/ en la poda de stack muerto) |
| `token_budget.py` | REVISAR | AI Op Layer 2026-07-25, recien creado, consumidor pendiente | 2026-07-25 |
| `venue_geometria_scd.py` | VIVO | genera la sala DEMO `data/venues/scd-plaza-egana.json` (derivada del modelo radial de `projects/plano/referencia_plano_teatro.py`) que abre por defecto el visor `iskvw/piel/venue/`; `tests/test_venue.py` verifica que el archivo del repo sea lo que imprime el generador | 2026-07-30 |
| `verify_all.py` | REVISAR | AI Op Layer 2026-07-25, recien creado, consumidor pendiente | 2026-07-25 |

Nota: el director listo tambien `render_flyer_mak.py` (VIVO, mak_ops) en
su mensaje de spec, pero ese archivo NO existe en `tools/` de este
worktree (ni en ninguna ruta del repo, verificado con busqueda global) --
omitido de la tabla, ver desvio reportado en el cierre de sesion.

## 6. thi.ng: LEER ANTES de escribir un generador, un pipeline o un grafo

Regla 2026-07-30 (causa: el usuario pidio thi.ng en varias sesiones seguidas y
al medirlo habia UNA sola libreria viva de cuatro vendorizadas, mientras la
sesion siguiente mandaba a escribir la misma capacidad desde cero. Retiro:
cuando cada fila EN USO tenga su test y ninguna quede en `candidata`).

thi.ng son ~350 paquetes de Karsten Schmidt (`https://thi.ng/#tags`), en
TypeScript. Hay una recomendacion externa priorizada de 15 para este repo. Esta
tabla es el estado REAL, medido, no la recomendacion:

| paquete | estado | donde, y que retira | senal |
|---|---|---|---|
| `@thi.ng/rstream-gestures` | **EN USO** | `iskvw/piel/campo/index.html` la carga con `import('../lib/gestos.js')`; trajo el pellizco multi-touch (antes: cuatro listeners y un solo dedo). Degrada a los listeners si no carga | 2026-07-27 |
| `@thi.ng/hiccup` + `@thi.ng/hiccup-svg` | **EN USO** | `docs/cultura/lib/compilador.js`: el gemelo de navegador del motor semantico arma el arbol SVG con `svg/group/rect/text` + `serialize`, en vez de concatenar strings. El taller de `docs/cultura/ensayos/rave/galeria.html` compila una spec sin Python y sin PC | 2026-07-30 |
| `@thi.ng/color` | **EN USO** | mismo compilador: el contraste WCAG lo calcula la libreria en vez de repetir la formula de luminancia a mano | 2026-07-30 |
| `@thi.ng/tsne` | **descartada con medicion** | no puede bajar 768 dimensiones a 2 (dim de salida = dim de entrada), asi que `tools/gen_campo_iskvw.py` sigue con sklearn. `tests/test_iskvw_librerias.py` fija el limite para que nadie lo reintente | 2026-07-27 |
| `@thi.ng/geom-trace-bitmap` | vendorizada, sin consumidor | imagen a vector de linea. El trazador vive en Python y ya esta afinado; solo paga si trazar se mueve al navegador | 2026-07-27 |
| `@thi.ng/distance-transform` | vendorizada, sin consumidor | campo de distancia, paso previo para engrosar/erosionar un trazo. Ninguna piel llego a ese paso | 2026-07-27 |
| `@thi.ng/graph` + `@thi.ng/rstream-graph` | **candidata, prioridad 1** | el micelio: `cultura/mak_plataforma/contrato_archivo.py` ya entrega 1004 piezas y 3188 vinculos como funcion pura. El grafo de thi.ng NO reemplaza el almacenamiento: entra como capa de analisis en memoria sobre lo ya indexado | sin medir |
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

Lo que la recomendacion externa pide NO priorizar todavia: WebGL, shaders,
fisica, particulas, audio, simulacion, hardware, fabricacion digital.
