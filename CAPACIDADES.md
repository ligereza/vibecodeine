# CAPACIDADES.md

Inventario de arranque rapido. Objetivo: empezar un proyecto nuevo (dentro o
fuera de este repo) sin tener que leer/buscar por todo `flujo`. Verificado
contra el repo real el 2026-07-24 (comandos ejecutados, no memoria). Si algo
de aca no calza con lo que ves, el repo cambio despues -- confia en el repo,
no en este doc, y actualizalo en el mismo PR que lo detecte.

## 1. Mapa index del repo

CLI real (`py -m flujo --help`, v0.56.1), comandos principales:

- `app` / `serve` -- hub local (workspace pro). `hub` -- servidor + index/route de C:\rd.
- `job`, `brief`, `intake` -- gestion de jobs y briefs (JSON 1.0).
- `cotizaciones`, `plano` -- cotizacion dual y plano SVG/rider/costos de stands.
- `suplementos` -- contraportadas RD (`svg/suplementos_rd/`).
- `rd-db`, `rd-datos` -- DB consultable RD (reactivos/packs/productoras/venues) + ingesta privacy-first.
- `eventos` -- automatizaciones (incluye `flyer-auto` desde link de Instagram).
- `resolume` -- automatizacion de shows Resolume/Chataigne por SMPTE/OSC (`.noisette`, schema validado contra fixtures reales).
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
| `contexto_repo.py` | Digest mecanico del repo (0 tokens): arbol + archivos clave. `map` / `task "<keywords>"`. |
| `crtdots.py` | Convertidor CRT phosphor dot-scanline / Rutt-Etra de imagenes. |
| `enviar_a_mak.py` | Puente WIN->MAK: envia carpeta a `~/curatoria_inbox/` via tar\|ssh, verifica conteo/bytes. |
| `handoff.py` | Borrador de cierre de sesion desde git+pyproject (no sobreescribe). |
| `instalar_enviar_a_mak.py` | Instala integracion "Enviar a" -> MAK curatoria en el explorador de Windows. |
| `render_video_rd.py` | Mete un mp4 (reel) en `RD.paravideo.blend` y exporta H264 headless. |
| `system_map.py` | Blueprint de arquitectura del ecosistema Tapiz/Psicosis/Fungi (schema API_CONTRACT). |
| `tapiz_live_loop.py` | Daemon-poller que corre `compete_engine` en modo `--live` a intervalo fijo. |
| `tapiz_telemetry.py` | Construye el autorretrato en vivo del ecosistema (`system_status.json`). |
| `token_budget.py` | Estima tokens de un set de archivos antes de mandarlos a un modelo. |
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
(diccionario 55k, senal tilde), `cultura/mak_curatoria/`.

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
| Arena (LMArena) | Frontier gratis on-demand para arquitectura dura, sin API | manual, sin config en repo; ver skill `toma-de-decisiones` |
| parth-dl (IG) | Descarga real de posts/reels de Instagram (via primaria desde 2026-07-22) | `pip install parth-dl`; usado en `src/flujo/eventos/flyer_auto.py` y `src/flujo/ig/download.py`; imginn.com solo fallback (403 Cloudflare), instaloader NO funciona (IG exige login), NO yt-dlp |
| Blender 4.5 | Render headless (flyer video, Chataigne prep) | WIN: `C:\Program Files\Blender Foundation\Blender 4.5\blender.exe` (OptiX, RTX 4070); MAK: `~/blender/` tarball portable 4.5.3 LTS (CUDA, GTX 1650) |
| Chataigne builder | Genera `.noisette` para Resolume/Chataigne | `src/flujo/resolume/automator.py::build_chataigne_noisette_experimental`; schema validado contra fixtures reales (`tests/fixtures/chataigne_1103_real*.noisette`, `tests/test_noisette_real_fixture.py`) -- nunca especular, la fixture manda |
| rclone / OneDrive en MAK | Entrega de renders (Drive de Google via `gdrive:` remote) | systemd `onedrive-rclone.service` en MAK; detalle en `context/LAST_HANDOFF.md` y `src/flujo/version.py` (changelog) |
| GitHub (gh CLI + runner self-hosted + workflows) | CI, gate de PRs, ordenes de curatoria, publicacion catalogo/portfolio | `gh` CLI local; runner self-hosted `mak` (online, labels `self-hosted,Linux,X64,mak,eventos`, verificado via `gh api repos/.../actions/runners`); workflows activos en `.github/workflows/`: `ci.yml`, `claude.yml`, `airdrop_gate.yml`, `issue_descarga_ig.yml`, `ordenes_curatoria.yml`, `portfolio.yml`, `publicar-catalogo.yml`, `render_piezas_vectoriales.yml`, `validar-piezas.yml`, `build-xio-apk.yml` |

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
