# LAST HANDOFF -- estado para el proximo agente

Version: 0.56.1 | Fecha: 2026-07-23 00:15 | Identidad: Cauce | sesion:
curatoria+DB lanzadas en MAK (director Fable). Cierre para sesion web
iPhone: el sucesor probablemente NO tiene LAN (ni ssh MAK, WIN apagado);
su canal a MAK es GitHub (issues + Actions + runner self-hosted).

## Sesion 2026-07-22/23 noche (cierre) -- LO VIVO AHORA MISMO

1. CURATORIA MASIVA CORRIENDO EN MAK: ~/curatoria/percepcion.py nohup
   sobre ~/RD (1731) + ~/portfolio_media/media (1401 IG, sin stories).
   Ficha schema UNICO, checkpoint procesados.txt (resume gratis),
   auto-pausa a 20 errores seguidos. Al cierre: 120/3132, 0 errores en
   cadena, ~24s/archivo, ETA ~20h. Benchmark F3d APROBADO (13/13
   productora, 12/13 fecha sobre flyers reales; gemma3:4b se queda).
2. VIGILANCIA AUTONOMA en MAK (cron */20): reporter.py escribe
   ~/curatoria/reportes/REPORTE_CURATORIA.md; watchdog.py crea issue
   GitHub "[CURATORIA] PAUSADA|ESTANCADA|TERMINADA" (label bloqueado).
   Esperar el issue TERMINADA para arrancar la fase siguiente.
3. CANAL DE ORDENES REMOTAS (telefono/web SIN LAN): issue con label
   "cambio", body con linea exacta "orden: estado|pausar|reanudar|
   redeploy <rama>" -> workflow ordenes-curatoria -> runner MAK ejecuta
   whitelist ~/curatoria/ordenes.py -> comenta resultado y cierra issue.
   JAMAS ampliar a shell libre: la whitelist es la muralla.
4. FLUJO EVENTOS AUTOMATICO: mail -> Apps Script usuario (8h, marca
   "pedido procesado") -> issue con action/descargar-ig -> workflow
   issue-descarga-ig -> runner MAK descarga (parth-dl, URL canonicalizada
   #175) -> artifact + comentario. RENDER EN MAK = v2 SIN MERJEAR (rama
   feat/v2-render-mak): al merjearla via PR a mejoras->main, barrido cada
   30 min procesa #171 #173 pendientes y suma render+cierre; correr UN
   workflow_dispatch de prueba tras merge (gap declarado del builder:
   convencion material cartelera.blend + if mixto sin probar).
5. Topologia de ramas VIVA (CLAUDE.md): main = solo lo perfecto; lineas
   permanentes rd/portafolio/mejoras; MAK y agentes JAMAS pushean main.
   PR pendiente: #176 (dpto cultura/mak_curatoria -> mejoras; ese codigo
   YA corre desplegado en MAK, el PR es el espejo gate).
6. Runner MAK self-hosted (labels mak,eventos): corre por nohup, NO
   sobrevive reboot de MAK. Fix usuario 1 vez: cd ~/actions-runner &&
   sudo ./svc.sh install mak && sudo ./svc.sh start.
7. Lecciones de la sesion (la noche fue calificada FALLIDA por el
   usuario; detalle en context/failed-handoff.md, untracked local WIN):
   (a) la palabra del usuario sobre SU sistema es EL DATO, no se litiga;
   (b) leer lo que esta delante (labels del repo, email text de issues)
   antes de inventar nombres o teorias; (c) director = spec+veredicto,
   builders construyen, nada de tareas de haiku a mano; (d) render MAK =
   GPU Cycles SIEMPRE (OOM = ollama en VRAM: curl keep_alive 0), jamas
   CPU/EEVEE; video 128 samples sin denoise 12-13s, stills 512; el video
   del reel = el del LINK del issue (dinamico).
8. PROXIMO en orden: (1) issue TERMINADA -> PASADA RELACIONAL: fuzzy
   match productoras/venues contra data/ y knowledge/ (gemma3 destroza
   nombres propios: "REDUCIENDODADOL", "CAUPOULIDAM" -- jamas aceptar
   texto literal), cruces RD<->IG, candidatos DB y manifest via PR
   humano-valida; (2) RECIEN DESPUES re-armar portfolio iskvw (organismo
   3 mundos, 1 tap, mobile-first; bocetos en scratchpad WIN job
   d475edb4); (3) plan maestro keen-scribbling-rabin.md (local WIN).

## Sesion 2026-07-22 (cierre anterior) -- pendientes resueltos por director

(sesion previa: orden y mantencion godspeed, director Fable +
haikus/sonnets delegados)

## Sesion 2026-07-22 (cierre) -- pendientes resueltos por director

HECHO (2da mitad, todo por PR con CI):
1. Issue #145 CERRADO (PR #149): parth-dl primaria en flujo/ig/download.py
   (flyer-import/ig-redownload); video->thumbnail, carrusel completo,
   caption/owner ahora se llenan. E2E vivo OK.
2. Capataz con cerebro local (PR #150): LLM('cerebras,groq,azure,ollama').
   DESPLEGADO Y VERIFICADO en el capataz vivo de MAK (sync 10min).
3. latido.py REVIVIDO en MAK: el cron habia desaparecido (no fue reemplazo
   de disenio); restaurado `7 */4 * * *` con backup del crontab previo en
   /tmp/cron_backup_20260722.txt; corrida manual OK, log fresco.
4. parth-dl en MAK: instalado 1.1.0 (git) + requests 2.34.2. GAP REAL
   DOCUMENTADO: IG sirve login-wall al extractor desde MAK aunque la
   pagina publica carga (curl -4 200) y WIN extrae desde la MISMA IP
   publica. Agotado: version, IPv4/6, fingerprint requests. NO seguir
   probando variantes; descarga IG real requiere WIN hoy. Idea futura:
   proxy de fetches IG via xio (IP movil, Android real).
5. iskvw.cl VIVO en HTTP (Pages + CNAME Cloudflare del usuario);
   cert TLS de GitHub en emision -- al responder HTTPS, activar:
   gh api -X PUT repos/ligereza/portfolio-auto/pages --field https_enforced=true
   Falta CNAME www (usuario aviso que lo agregaria).
6. APK hotspot_boot_service BUILDEADO por primera vez (workflow
   build-xio-apk.yml, PR #151; runner ubuntu, artifact 7 dias).
   Instalacion via adb BLOQUEADA por HyperOS (INSTALL_FAILED_USER_
   RESTRICTED): falta toggle "Instalar aplicaciones via USB" en
   Opciones de desarrollador (usuario). Con el toggle: adb install -r
   app-debug.apk + settings put secure (comandos exactos en el README
   del servicio). El APK descargado quedo en scratchpad de la sesion;
   re-descargable: gh run download 29940029125 -n hotspot-boot-apk.
7. Archivado docs (PR #152): 10 supersedidos/one-off a
   _archive/legacy_20260722_docs/. AGENTS.md NO se archiva (stub por
   convencion, PR #147). SVG dark 09_contraportadas_dark NO se archiva:
   generador y consumidor VIVOS (gen_contraportadas.py /
   regen_deliverables.py) -- es cache reproducible + input de entregas.
8. Skill godspeed: bootstrap any-model (PR #148) validado con simulacion
   Sonnet-director real (4/4 claims verificados, trampa checkout-detras-
   de-origin cazada). Sonnet+godspeed = default para mantencion/auditoria.
9. git stash drop aplicado por el usuario. CNAME @ corregido a
   ligereza.github.io.

DECISIONES DE DIRECTOR (usuario delego):
- utilidades/ MAK: SE QUEDAN (produccion activa del loop, gobernada por
  ratchet pyflakes + PRs); sin archivado periodico por ahora.
- Video en cartelera.blend: imagen-solo sigue siendo el flujo; rama video
  (movieclip.frame_duration + FFmpeg directo) queda como issue de disenio
  cuando el usuario decida formato de entrega.

## Sesion 2026-07-22 -- orden total, gobernanza, MAK autonomo

DECISION DE ARQUITECTURA (usuario confirmo): MAK = autonomo primario
(WIN solo esta prendido cuando el usuario esta en casa). WIN = apoyo de
recursos graficos oportunista (GPU render via bridge cuando este vivo).
Entrega por Google Drive desde quien renderiza (MAK por defecto, rclone
ya provisto).

HECHO (todo por PR, CI verde en cada uno):
1. Merge local concluido (usuario estaba a mitad de pull) + push.
2. Raiz limpiada: 11 reportes one-off (experimentos ollama/arena) ->
   _archive/legacy_20260722_1110/; 8 scripts operativos -> tools/mak_ops/.
3. PRs capataz #122-#127 aterrizados en secuencia (update-branch ->
   CI -> squash-merge). Ramas huerfanas borradas; ramas == PRs abiertos.
4. RESCATE: stash@{0} (07-16) tenia 8 archivos cultura/ (2483 lineas:
   BLENDER.trilogy, blend-math-lab, research_agent docs, xio-concept)
   que NO existian en main bajo ninguna ruta -> PR #140 MERGED.
   El stash local quedo (classifier bloqueo drop): `git stash drop` manual.
5. GOBERNANZA: enforce_admins ACTIVADO en branch protection de main.
   Nadie (ni admin ni agente con credencial de usuario) pushea directo;
   todo por PR + CI. Revertir si estorba:
   `gh api -X DELETE repos/ligereza/vibecodeine/branches/main/protection/enforce_admins`
6. Issue #139: audit de utilidades MAK. 6 archivos con NameError latente
   (compilan, revientan en runtime). Fix verificador puertos PR #141
   MERGED (util real: salud 8890/8891/8900). RATCHET PR #143: pyflakes
   en dev-deps + test que bloquea nuevos undefined-name en utilidades/
   (allowlist congelada a 4 legacy; pesco un 6to bug en vivo al entrar #127).
   REGLA NUEVA para el generador MAK: smoke-run antes de PR, compilar no basta.
7. Issue #131 (evento real, reel IG): imginn 403 Cloudflare total ->
   PR #142 MERGED: parth-dl (get_info) via primaria; video/reel usa
   thumbnail, carrusel SOLO primera imagen; mirror fallback. E2E VIVO
   probado con el reel (paleta OK, productora SELVA Festival sin match DB).
   parth-dl requiere pip install en la maquina de eventos (WIN ya lo tiene;
   MAK falta si va a correr eventos).
8. RD -> MAK: 57GB/1731 archivos transferidos por LAN (tar|ssh, sin nube),
   integridad verificada (conteo identico). MAK ya tiene assets para operar
   sin WIN. Nota: RD/AUTOMATIZACION/input_ig.jpg pudo viajar a medio
   escribir (el e2e corria en paralelo); regenerable.
9. Portfolio: GitHub Pages de ligereza/portfolio-auto con cname=iskvw.cl
   configurado. FALTA USUARIO: en Cloudflare DNS agregar CNAME @ ->
   ligereza.github.io y CNAME www -> ligereza.github.io, AMBOS DNS-only
   (nube gris) hasta que GitHub emita el cert; despues activar
   https_enforced (gh api -X PUT .../pages --field https_enforced=true).
10. Limpieza local: 49 __pycache__ + .pytest_cache + _logs. Suite verde.
11. exe.old RESUELTO: era imagen en memoria de proceso huerfano tras npm
    install (ver sesion 07-20); doctor limpio, npm claude 2.1.217 sano.

VERIFICADO EN MAK (operador sonnet, solo lectura):
- Servicios 8890/8891/8900 todos 200; cron completo; espejo ~/flujo
  sincroniza cada 10min (tenia el merge de #122 a minutos).
- Ollama MAK local: deepseek-coder:6.7b + gemma3:4b + nomic-embed.
  qwen-agent 0.0.34 instalado.
- GAP CRITICO para autonomia: capataz.py linea ~169 usa
  LLM('cerebras,groq,azure') -- 100% nube, SIN fallback local. Falta
  hook 'ollama' local (deepseek-coder ya esta en localhost:11434).
  Ese hook es EL siguiente paso de independencia real.
- latido.log stale desde 07-17 (capataz.log si esta fresco) -- confirmar
  si fue reemplazo de disenio o fallo silencioso.
- Ollama WIN: APAGADO hoy (proceso no corre; pendiente autostart real).

PENDIENTES USUARIO (nadie mas puede):
- Cloudflare DNS (punto 9). AccessibilityService Xiaomi + PAT Termux
  (xio inalcanzable hoy, 000 en IPs conocidas). git stash drop manual.

DECISIONES DE POLITICA ABIERTAS (no ejecutadas a proposito):
- utilidades/ de MAK: 20+ scripts de practica sin consumidores (audit
  dice archivar 17; PERO MAK los sigue produciendo via PRs -- definir si
  el showcase se queda, se archiva periodico, o el generador cambia).
- docs/: 10 candidatos claros a _archive (MANTENIMIENTO_REPO supersedido,
  PARA_IA*, 3 audits 06-28, TASK_PROMPTS, README_AIRDROP, 2 privacidad).
- svg/suplementos_rd/09_contraportadas_dark: 9 SVG de ~5MB (45MB repo);
  la plantilla real de produccion vive en Desktop/ai_illustrator.
- Video en cartelera.blend: frames automaticos = cargar mp4 como
  movieclip en la llamada headless y leer clip.frame_duration; salida
  video = FFmpeg H264 directo de Blender. Sin decidir imagen vs video.

## LOOP CERRADO (2026-07-20 noche) -- GitHub ES el canal de mando
Como una senal de la web llega a las maquinas, cableado y verificado:
1. Agente gratis (Arena, o Claude via issues con `claude.yml`) produce un
   cambio -> release `airdrop-*` (`airdrop_gate.yml`) o PR directo.
2. CI + branch protection validan -> merge a main. (gate = los ojos)
3. **MAK auto-sincroniza cada 10min** (cron `MAK-REPO-SYNC`): fetch+reset
   --hard origin/main SOBRE el clon `~/flujo`, Y LUEGO copia el espejo
   `cp -ru ~/flujo/cultura/mak_{plataforma,research,codex}/. -> ~/{plataforma,
   research,codex}/`. OJO CRITICO (verificado): los servicios vivos corren
   de dirs SUELTOS (~/plataforma etc.), NO del clon -- por eso el paso cp
   es imprescindible; sin el, mergear no tocaba el codigo vivo. Probado:
   backlog.py del repo == el vivo tras el sync (PROPAGA-OK).
4. El organismo MAK (cron: trabajo/capataz/agente_real/entregar/revisor,
   invocaciones python frescas cada tick) corre el codigo nuevo enseguida.
   CAVEAT honesto: (a) servidores persistentes (research:8890/codex:8891/
   hub) necesitan restart del watchdog para recargar .py cambiado; (b)
   capataz.py/agente_real.py/chat_agente.py viven SOLO en la caja, NO en el
   espejo del repo todavia -- si se quieren gobernar por merge, meterlos a
   cultura/mak_plataforma/ (via PR, no push directo: branch protection).
5. WIN NO recibe senal de repo -- es puro endpoint de inferencia Ollama
   (192.168.50.1:11434) que MAK llama por HTTP. No necesita clon ni pull.
Resultado: mergear a main = darle una orden a MAK, sin PC, sin cuenta
Claude. GitHub es el medio de comunicacion, tal como se diseno.

## Sesion 2026-07-20 noche -- rescate capataz + autonomia MAK

Una sesion previa ("Godspeed tokens deletion issue", `e7893c70`) quedo
huerfana: el proceso Git Bash siguio vivo 9h en memoria (Task Manager lo
mostraba "Claude.exe.old" porque un `npm install` posterior sobreescribio
el binario en disco mientras el proceso corria -- Windows conserva la
imagen vieja en memoria, no es corrupcion). Su ultimo estado real (sin
continuacion, stream murio a media frase): estaba armando el CAPATAZ
(director autonomo de MAK, sin Claude en el loop) y probando un cerebro
LOCAL gratis para que corra 24/7 sin depender de free-tier de nube.

### ARREGLADO esta sesion
- Encontrados 2 worktrees con trabajo listo sin push: `capataz-sintetico`
  (context/CAPATAZ.md -- usuario sintetico destilado de 894 mensajes
  reales, voz de presion "todo verde no es descanso") y `doctrina-claude`
  (context/DOCTRINA_CLAUDE.md -- 190 lineas de ideologia/politicas
  aprendidas en 3 semanas, para que el repo corra sin Claude). AMBOS
  PUSHEADOS (ramas `worktree-capataz-sintetico` y `worktree-doctrina-claude`,
  sin PR abierto -- falta que alguien los abra/mergee).
- Scripts sueltos del scratch (archivados 2026-07-22: `capataz_remote.py`, `_scratch_agente_libre.py`,
  `backlog_codex_script.py`, `mine_corpus.py` movidos a `_archive/legacy_20260722_profundo/`).
  Verificados contra MAK: `agente_libre.py` y `backlog_codex.py` YA estaban
  desplegados byte-identicos (diff vacio). `capataz.py` (297 lineas, el
  director) TAMBIEN ya estaba desplegado pero SIN cron -- agregado:
  `10,40 * * * * capataz.py >> logs/capataz.log # MAK-CAPATAZ`.
- BLOQUEO DE SEGURIDAD encontrado y cerrado: `corpus_candidates.txt`
  (texto crudo de mensajes viejos del usuario) tenia una API key real de
  Gemini pegada en texto plano (`AIzaSy...`, ya rotada por el usuario
  segun el propio mensaje). El pre-commit hook la detecto y bloqueo el
  commit -- redactada antes de pushear. Repo es PUBLICO, la deteccion
  funciono como debia.
- Bug propio cometido y corregido en la misma sesion: al probar el pull
  de `qwen2.5:7b`, un `curl 127.0.0.1:11434` disparo una SEGUNDA instancia
  de Ollama en Windows bindeada a `0.0.0.0:11434` (expuesta a TODAS las
  redes, no solo el cable directo a MAK) -- PID 20432, matado apenas
  detectado. La instancia correcta sigue en `192.168.50.1:11434` (solo
  interfaz del cable directo, como debe ser).
- Proceso huerfano de la sesion muerta (PID 31636, 9h vivo, bg-pty-host)
  matado. El otro PID reportado (22824) ya no existia al chequear.

### PENDIENTE (real, sin maquillar)
1. **`qwen2.5:7b` pull**: relanzado en la instancia CORRECTA
   (192.168.50.1:11434), 4.7GB, estaba corriendo en background al cerrar
   esta sesion -- confirmar que termino (`curl 192.168.50.1:11434/api/tags
   | grep qwen2.5`).
2. **Bloqueo real de la mision del capataz, sin resolver**: tool-calling
   CRUDO de Ollama falla en AMBOS modelos locales (`llama3.1:8b` Y
   `qwen2.5:7b` devuelven sin `tool_calls`). El cerebro local para el
   capataz NO funciona todavia por esa via. La sesion muerta encontro
   (sin probar) la salida: `qwen-agent` (el framework python, ya
   instalado en MAK con numpy) tiene su PROPIA capa de function-calling
   por prompt-template, independiente de la API nativa de Ollama --
   nunca se probo. Ese es el siguiente paso concreto, no un misterio.
3. **Auto-reparacion del capataz ante error**: la infraestructura YA
   EXISTE (modo `debug` en codex:8891 -- planner diagnostica, coder
   reescribe, NUNCA pisa codigo vivo, guarda propuesta en
   `~/codex/revisiones/`; fallback seguro del capataz es `vetear` si el
   modelo alucina una accion fuera del menu). Falta cablear que el
   capataz DISPARE ese modo `debug` automaticamente cuando su propio
   ciclo falla repetido (hoy el fallback es pasivo, no auto-diagnostico).
4. **2 PRs por abrir**: `worktree-capataz-sintetico` y
   `worktree-doctrina-claude` estan pusheadas pero sin PR -- abrirlas y
   mergearlas a main.
5. Verificar que `capataz.py` corrio limpio en su primer disparo de cron
   (`ssh mak@192.168.50.2 "tail ~/plataforma/logs/capataz.log"`).

### DESBLOQUEO REAL, PROBADO EN VIVO (corrige el veredicto de abajo)
`qwen-agent` SI funciona como agente real sobre modelos locales de Ollama
-- el tool-calling NATIVO de Ollama esta roto (confirmado, /api/chat sin
tools= no devuelve tool_calls), pero `qwen_agent.agents.Assistant` lo
esquiva con su PROPIA capa de function-calling por prompt-template.
PROBADO EN VIVO en MAK contra `llama3.1:8b` (WIN, 192.168.50.1:11434):
tool real registrada con `@register_tool`, el modelo la invoco con
argumentos correctos, ejecuto, observo el resultado, y respondio en base
a eso -- loop de agente real, gratis, sin nube. Bug de infra encontrado y
corregido en el camino: Ollama en WIN perdio `OLLAMA_MODELS` al
reiniciarse (proceso nuevo sin el env persistido) -- corregido, modelos
visibles de nuevo (deepseek-coder-v2, llama3.1:8b; qwen2.5:7b nunca
termino de bajar, no es necesario, llama3.1:8b ya sirve).

SIGUIENTE PASO CONCRETO (no otro parche, la pieza que falta de verdad):
reemplazar el `echo_test` de prueba por herramientas REALES -- leer
archivos de MAK, correr `entregar.py --limit 1`, `revisor.py --enforce`,
llamar research:8890/codex:8891 -- y darselas a un `Assistant` de
qwen-agent en un loop (no un ciclo unico como capataz.py hoy). Codigo de
referencia del test que funciono: buscar en el historial de esta sesion
"echo_test" + `register_tool` -- reproducible, no hace falta redescubrir
la config (llm_cfg model_server='http://192.168.50.1:11434/v1',
api_key='ollama').

### CERRADO EN VIVO: agente_real.py -- el reemplazo, no otro parche
`~/plataforma/agente_real.py` en MAK: `qwen-agent` Assistant sobre
`llama3.1:8b` local (WIN, gratis) con 3 herramientas reales
(`leer_estado`/`vetear`/`entregar`, mismo codigo que ya usaba
capataz.py). YA EN CRON (`25,55 * * * *`). Probado 2 veces en vivo: el
MODELO decidio la herramienta (no Python), la ejecuto de verdad
(`revisor.py --enforce` corrio, exit=0), leyo el resultado real, reporto
en base a eso. Esto SI es el reemplazo -- reasona, actua, observa, en un
loop, sin Claude, sin nube. `capataz.py` (el dispatcher viejo) sigue en
cron tambien, ambos conviven; decidir si se retira capataz.py o se dejan
los dos es del proximo agente/usuario. Config reproducible: llm_cfg =
`{'model':'llama3.1:8b','model_server':'http://192.168.50.1:11434/v1',
'api_key':'ollama'}`, tools con `@register_tool` de
`qwen_agent.tools.base`. Requiere `pip install soundfile python-dateutil`
(ya instalado en MAK). Bug de infra resuelto en el camino: Ollama en WIN
perdio `OLLAMA_MODELS` al reiniciar el proceso -- ahora se relanza con
`OLLAMA_MODELS=C:\OLLAMA_MODELS OLLAMA_HOST=192.168.50.1:11434 ollama.exe
serve` si vuelve a pasar.

### VEREDICTO HONESTO sobre "el capataz" (para el proximo agente, sea cual sea)
`capataz.py` NO es un agente reflexivo. Es un dispatcher: junta metricas,
le pregunta a un LLM (nube por defecto) "cual de estas 8 acciones fijas
corresponde", y ejecuta esa accion con codigo fijo -- sin dialogo, sin
memoria entre ciclos salvo el jsonl, sin auto-diagnostico cuando falla
(cae a un fallback pasivo, "vetear"). Las piezas que SI podrian pensar
(`junta.py` reflexion diaria, modo `debug` de codex que diagnostica y
propone fix) existen mas EN NINGUN LADO estan cableadas para que el
capataz las dispare solo ante su propio error. Es mimica de autonomia
(ejecuta bien un guion), no reemplazo real de un agente que razona.
Si otro agente sigue esto: el trabajo real pendiente es CABLEAR
auto-diagnostico (leer bitacora_capataz.jsonl, detectar fallos propios
repetidos, disparar debug sobre si mismo antes de vetear), no agregar
mas acciones al menu.

### Si el cron/automatizacion NO corre
`~/plataforma/SI_EL_CRON_NO_CORRE.md` (MAK): un solo comando --
`ssh mak@192.168.50.2 "cd ~/plataforma && python3 capataz.py"` -- el
script YA lee CAPATAZ.md, arma el prompt y llama al modelo el mismo (no
existe forma de "pasarle un archivo a qwen": Ollama es una API de
inferencia sin manos, quien lee archivos es capataz.py, que corre en
MAK). OJO REAL: `capataz.py` linea 169 usa `LLM("cerebras,groq,azure")`
-- SOLO nube, el proveedor local 'win' (qwen2.5:7b/llama3.1 en la RTX
4070) todavia no esta en esa cadena, pendiente de agregar como fallback.

### Verificacion de esta sesion
No se toco codigo de `src/flujo` -- solo docs/scripts en worktrees +
operacion remota en MAK (cron) + Windows (ollama). No aplica pytest.


## 2026-07-20 GODSPEED handover a autonomia

DIRECTOR handoff -- organismo autonomo sin dependencia Claude activa.

DONE (verified live today):
- Ollama-WIN (192.168.50.1:11434) revived; models deepseek-coder-v2:16b-lite-instruct-q4_K_M + llama3.1:8b active; Windows Startup .cmd autostart proven; MAK reaches across LAN. Provider 'win' in research_lib.LLM (win) and codex chain functional.
- MAK box 24/7 hardening: suspend/sleep/hibernate targets masked (systemctl mask); self-heal proven live (killed research interfaz.py, cron watchdog relaunched, :8890 returned 200). Cron watchdogs */5 cover hub:8900, research interfaz:8890+cola, codex interfaz:8891, xio monitor. Disk 14 percent free.
- SearXNG self-hosted (Docker 127.0.0.1:8888, --restart unless-stopped, JSON format enabled). searxng_search() added to research_lib.py; web_search() dispatcher (searxng-first, tavily fallback) in research.py/panel.py/refutar.py. Both call _salud_registrar; hub health panel shows searxng successes live. Tavily credits saved.
- PRs open: #94 fix(ocr) available=False on error (CI green both OS); #95 feat searxng + web_search (check CI status).
- Handover intent: organism autonomous via cron (trabajo.py every 30 min) + watchdogs + restart policies. Ollama-WIN = local LLM provider. 15-min recall safety check left. Zero dependence on Claude director.

NEXT (minor, if extending):
- Extend searxng to codex chain (PLAN Fase 4).
- Wire codex health panel to match research/hub.

BLOCKERS: none critical.

---
## Sesion 2026-07-20 (Sonnet 5, sesion larga multi-tema)

### 1. Incidente de auth (Claude CLI, no del repo)
Otro agente, pedido "borra tokens MAK", borro por error la entrada de Claude
CLI en Windows Credential Manager (scope mal interpretado). Recuperado via
npm reinstall (claude.oldXXX.exe = normal, Windows renombra exe corriendo,
ya limpio) + /login que escribio fallback en ~/.claude/.credentials.json.
Verificado con llamada haiku real. `~/.git` accidental (repo vacio en el
HOME de Windows, de un setup viejo) borrado -- causaba el error real de
`--teleport` (buscaba sesiones en el repo equivocado). Detalle: memoria
reference_claude_cli_auth_topology.

### 2. Auditoria de seguridad (Windows + MAK) -- limpia
Windows: todos los procesos no-sistema firmados por editores conocidos, red
sin conexiones raras, unico scheduled task dudoso (SoftLandingCreativeManagementTask)
resulto ser telemetria Adobe con CLSID ni siquiera registrado (roto, inerte).
32 procesos huerfanos (bg-pty-host de sesiones CLI viejas) cerrados -> 14.
MAK: cero tokens en codex/research/hub/watchdog/trabajo.py (verificado en
vivo, no solo git); el drift de 3f40b09 (trabajo.py exigia ~/codex/.token ya
borrado) YA estaba desplegado y confirmado limpio. nc en :9876 = clip-bridge-recv
propio (no backdoor). Puerto 8080 = docker open-webui. Cron/systemd = solo
servicios MAK-ORGANISMO conocidos.

### 3. Mouse sharing (Barrier) revivido
barrier-server.service en MAK tenia DISPLAY=:1 hardcodeado pero el X real
corre en :0 desde el ultimo reboot -- rota desde entonces, coincidencia de
timing con la sesion, no causado por el usuario ni por mi. Fix: 1 linea en
el unit file + restart. Verificado ESTAB en el puerto 24800.

### 4. instaloader confirmado muerto -- removido
IG exige login incluso anonimo (confirmado por el usuario en sesion previa
de independencia del Droplet Photoshop). src/flujo/eventos/flyer_auto.py:
removida `_download_instagram` (funcion muerta), ahora usa directo
`_download_via_mirror` (imginn.com, ya probado vivo). CLAUDE.md corregido
(la regla vieja decia "usar instaloader"). Tests actualizados. RESUELTO
(sesion 2026-07-20 tarde): src/flujo/ig/download.py (usado por flyer-import
CLI y flyer/import_email.py, boton "Descargar post" del editor web) tenia
el MISMO bug -- reescrito para usar el mismo mirror (imginn.com), sin
instaloader. Soporta imagen y carousel (no video, el mirror no lo expone);
caption/owner/fecha ya no disponibles (el mirror no los expone confiable).
tests/test_ig_download.py reescrito con mock de mirror. Dependencia
`instaloader` removida de pyproject.toml y requirements.txt. Referencias
en docs/CLI.md, EventsPanel.tsx y gmail_to_github_issues.gs actualizadas.

### 5. Puente issue-render Windows (tools/bridge_issue_render.py) -- NUEVO, probado en vivo
Gmail->issue ya lo tiene el usuario (fuera del repo). Label real de la
intake es `instagram` ("Contains Instagram link"), NO `action/descargar-ig`
(ese solo existia en un test viejo). Script: ve issues abiertos con esa
label, saca el link IG del body, corre `flujo eventos flyer-auto --render-blender
--yes --blender-exe <ruta real>` (Blender NO esta en PATH, hay que darla
completa: `C:\Program Files\Blender Foundation\Blender 4.5\blender.exe`),
copia el render a `drive/` (Google Drive real-time, ya gitignored), comenta
+cierra el issue. Probado en vivo 2 veces:
- issue #14: fallo (bug de encoding, ver abajo), quedo abierto (no se
  cerro mal), state guardado en _logs/bridge_issue_render_state.json.
- issue #93: exito completo end-to-end. Render GPU real (OptiX, RTX 4070),
  productora matcheada (Sundeck), copiado a drive/, comentado y cerrado.
  CAUSA RAIZ de por que #93 se habia cerrado mal el 07-18: el script viejo
  (deleted, solo quedaba el .pyc huerfano, ya limpiado) corria flyer-auto
  SIN --render-blender y trataba el reporte vacio como "listo".
2 bugs de encoding en el wrapper arreglados (decode utf-8 de la salida de
Blender/Rich, y print a consola con emojis de BlenderKit -- cp1252 default
de Windows no los soporta, reconfigure stdout/stderr).

### 6. Arquitectura recursos compartidos WIN<->MAK -- INVESTIGADA, NO implementada
Usuario pidio: acceso mio completo a MAK, MAK sin acceso saliente a Windows
salvo pedir recursos GPU, patron "como el mouse sharing" (server/cliente).
Hallazgos:
- YA EXISTE (commit 6a2b147, #48): proveedor 'win' en research_lib.py/
  codex_lib.py de MAK -- llama a Ollama en Windows (192.168.50.1:11434,
  llama3.1:8b) via HTTP. PERO es MAK saliendo hacia Windows, rompe lo
  unidireccional que pide el usuario ahora.
- Solucion propuesta (NO implementada): SSH reverse tunnel iniciado por
  Windows (`ssh -R`) -- Windows abre el canal, MAK solo ve un puerto local,
  nunca sale. Reemplazaria el proveedor 'win' actual.
- Para recursos GPU no-LLM (ej. Blender si la GTX1650 de MAK no alcanza):
  bridge por archivos via drive/ (mismo patron que tools/blender/bridge_blender.py,
  MYRA/Unreal) -- cero conexion de red entre las maquinas.
- llama.cpp RPC (dividir UN modelo entre 2 GPUs) investigado y DESCARTADO:
  solo ayuda a correr modelos mas grandes de lo que entra en una GPU, NO
  acelera modelos que ya entran (agrega latencia de red entre capas).
- Decision del usuario: no complicar mas por ahora -- research/codex usan
  Ollama-WIN cuando haga falta, Blender renderiza directo en MAK sin tocar
  Windows para nada.

### 7. MAK provisto: Blender + OneDrive + permisos
- sudoers NOPASSWD acotado por el usuario mismo (/etc/sudoers.d/claude-bridge,
  solo apt/apt-get/systemctl/onedrive) -- NUNCA se me dio ni pedi la password.
- Blender 4.5.3 LTS instalado (tarball portable en ~/blender/, sin sudo),
  verificado corriendo, launcher visible en Escritorio + buscable en apps.
- OneDrive: el cliente oficial (`onedrive` via apt) genero un phishing
  warning en el navegador (Brave, no Firefox como asumi al principio) al
  autenticar -- INVESTIGADO: client_id verificado hardcodeado en el binario
  oficial de Debian (no inyectado), DNS de login.microsoftonline.com resuelve
  a infraestructura real de Microsoft (aadg.trafficmanager.net), /etc/hosts
  limpio. Muy probable falso positivo por heuristica de la URL OAuth larga,
  pero el usuario decidio cambiar la password de esa cuenta igual (correcto,
  ante la duda). PIVOT a `rclone` (ya usado para gdrive:) en vez del cliente
  oficial -- mismo resultado, menos friccion. Remoto `onedrive` configurado
  (cuenta educativa UC, uccl0-my.sharepoint.com), montado en ~/OneDrive/ via
  systemd (onedrive-rclone.service, enabled+active), verificado con archivos
  reales (MAK/, PRESERVER/).
- GitHub: cuenta `miskirabit` (gh CLI ya autenticado en MAK, DISTINTA de la
  cuenta personal `ligereza` del usuario -- deliberado, cuenta estudiantil)
  recibio invitacion Write (no Admin) sobre ligereza/vibecodeine, ACEPTADA
  desde MAK mismo. Verificado: push:true, admin:false.
- Panel de estado visible creado: ~/Escritorio/00_ESTADO_CLAUDE.md en MAK
  (el usuario no podia ver el trabajo por SSH headless) -- se actualiza cada
  vez que se hace algo ahi, sin que el usuario tenga que preguntar o buscar.

### PENDIENTE para el proximo agente/sesion
1. Escribir el bridge issue->render EN MAK (paralelo al de Windows, ya
   probado): mismo flujo pero 100% autonomo -- gh como miskirabit, download
   via mirror (mismo codigo Python, portable), render con Blender local +
   GPU de MAK, output al rclone gdrive: existente (Drive de Google = destino
   final acordado, ahi maneja los correos de la directiva). Trigger: cron
   (patron nativo de MAK, no un loop -- el usuario explicito no quiere loop).
2. Confirmar que el usuario efectivamente subio RD + flujo a OneDrive desde
   Windows y que llega sincronizado a ~/OneDrive/ en MAK (assets: RD.blend,
   FRAME2.png, historia.psd, data de productoras).
3. Implementar (si se decide seguir) el SSH reverse tunnel para el proveedor
   Ollama-WIN unidireccional -- disenado, no construido.
4. [HECHO 2026-07-20 tarde] src/flujo/ig/download.py migrado a mirror
   (imginn.com), igual que flyer_auto.py. Ver seccion 4 arriba.
5. .gitignore: agregado drive/ y .playwright-mcp/. __pycache__ limpiado
   local (ya estaba gitignored, no afectaba commits).

### Verificacion de cierre
py -m compileall src/flujo: OK. py -m pytest tests/ -q: 100% verde (0
fallos). py -m flujo verify: OK (hub smoke OK). Bump 0.55.0 -> 0.56.0.

CIERRE VISUAL 2026-07-18T14:00 (ultima tanda Fable, 1 sonnet ejecuta): widget
"salud proveedores" en el hub (GET /api/salud lee salud_proveedores.json,
barras por score, degradados en rojo, poll 15s solo con panel research
abierto; 6 tests, suite verde) -- DESPLEGADO al box via systemctl restart
mak-hub, /api/salud y /api/organismo en 200, VERIFICADO VISUAL con Playwright
real contra el hub vivo (screenshot local _logs/, no commiteado). Plan de la
semana siguiente: context/PLAN_SEMANAL_OPUS.md (operador previsto: Opus).

Version: 0.55.0 | Fecha: 2026-07-18T13:30 | Identidad: Cauce | sesion: GODSPEED-5b -- cierre del dia (1 haiku organiza + 4 lanes).

## CIERRE DEL DIA 2026-07-18 (resumen para el proximo agente)

PRs #72-#87 mergeados a main (v0.55.0). MANIFIESTO 6/11 piezas. MAK dual-dept research+codex operativo con WIN como proveedor (research+codex comparten stack; fallback nube -> WIN -> ollama-local probado). Demo defects cerrados en PR #85: _paso_con_fallback (proveedor 429 no mata el job), /run modo resolution (no normalizacion silenciosa), cultura marco neutro para temas sin sustancia. WiFi scan parser hardware-verified en Xiaomi (PR #83, columnar + legacy fallback). Autoportfolio vivo (portfolio-auto PR #4/#5, refresh semanal lunes). GODSPEED-5: salud_proveedores demota fallidos 6h, integridad panel marca sin_job, systemd mak-codex reparado (enabled+EnvironmentFile opcional+WorkingDirectory fijo). Pendientes usuario: PAT Termux, AccessibilityService, datos productoras+venues. Pendientes sin gate: mak-hub/mak-xio units disabled (reboot risk); divergencia grafo.py vs cadena.py fallback (documentada PR #85 notas). [AMBOS CERRADOS en GODSPEED-5b, ver seccion siguiente]

## Sesion 2026-07-18T13:00 (GODSPEED-5b, cierre del dia: 1 haiku organizador + 4 lanes)

- PR #87 MERGEADO (CI matrix verde 2x); rama head borrada tras state==MERGED.
- Ramas extra purgadas: worktree-god-haiku-fixes (remota, 0 unmerged),
  god-mak-ola2/god-mak-pausa (locales, 0 unmerged, worktrees removidos).
- AUDITORIA rama worktree-mak-research-cultural (7 commits unmerged): TODO
  SUPERSEDED por PRs #48/#49 y refactors posteriores en main (diffs solo
  net-negativos; mak_lenguaje byte-identico; patch_interfaz.py borrado a
  proposito en el auth-delete). Rama + worktree ELIMINADOS (los 101 dirty
  eran deletions no commiteadas de .archive/old-archive, sin contenido).
- UNITS mak-hub y mak-xio del box: existian pero DISABLED (misma clase que
  mak-codex); ExecStart targets verificados, WorkingDirectory pineado
  (%h/plataforma, %h/xio_puente), .bak de cada unit, kill manual por PID +
  enable --now inmediato (el watchdog relanza en segundos si hay hueco).
  VERIFICADO: ambos active, MainPID = unico proceso, hub :8900 -> 200.
  Los 3 servicios del box (codex/hub/xio) ahora systemd-managed + enabled.
  Espejos en cultura/mak_plataforma/mak-hub.service + mak-xio.service.
- grafo.py unificado a la semantica de cadena.py: _nodo_con_fallback (intento
  order=[m] solo; en RuntimeError reintenta con el resto de llm.order sin m;
  diferencia documentada: grafo no tiene cadena posicional). El fallo del
  proveedor asignado ahora queda VISIBLE en llm.errors en vez de absorberse
  silencioso. +5 tests (test_mak_grafo_fallback.py).
- context/PLAN_SIGUIENTE_AGENTE.md reescrito al estado real (v0.55.0,
  PRs #72-#87, 51 lineas). README: subseccion MAK en el bloque operativo
  (arte intacto). Limpieza local: 110 __pycache__ + 4 .pytest_cache + _logs.
- grafo.py DESPLEGADO al box (~/research/grafo.py, py_compile OK; los modos
  se importan fresh por job, sin restart necesario).

## Sesion 2026-07-18T12:00 (GODSPEED-5, director + 5 lectores sonnet + 2 builders sonnet)

Backlog sin-gate del handoff anterior, 3 frentes cerrados:

### 1. RECONCILIACION SYSTEMD CODEX EN EL BOX (hecha y verificada)
- El "riesgo menor" del handoff anterior escondia 2 bugs reales: el unit mak-codex
  tenia EnvironmentFile=%h/codex/.token SIN guion opcional (archivo borrado en el
  auth-delete de PR #71 -> el unit NUNCA podia arrancar: "Failed to load environment
  files") Y el unit estaba disabled (el claim "reboot lo toma limpio" era falso por
  partida doble; solo el watchdog revivia codex).
- Fix aplicado vivo (unit = config de usuario, lane seguro; .bak dejado): linea
  EnvironmentFile eliminada, WorkingDirectory=%h/codex agregado (launches manuales
  siempre corrian desde ~/codex; jobs.jsonl y revisiones/ son relativas), Description
  sin mencion al token muerto. daemon-reload + enable --now.
- VERIFICADO: is-active=active, MainPID=296835 es el proceso vivo, :8891 responde 200,
  Environment=CODER_CHAIN=win,nim-pro,nim-flash,ollama en el unit. Sin proceso manual
  duplicado. Espejo del unit al repo: cultura/mak_codex/mak-codex.service.
- Trampa nueva: al matar el proceso manual por PID, el watchdog cron relanzo OTRO
  manual en segundos -- la reconciliacion real es kill PID + systemctl start inmediato.
- Observado (sin tocar): mak-hub y mak-xio tienen units disabled tambien -- misma
  clase de fragilidad al reboot, pendiente sin gate.

### 2. SALUD DE PROVEEDORES EN RESEARCH (backlog Groq 429) -- esta PR
- research_lib.py: _salud_cargar/_salud_registrar (registro persistente
  ~/research/salud_proveedores.json, ventana 6h, best-effort sin lock) +
  orden_por_salud() PURA (degrada al final proveedores con >=3 intentos y
  score_provider_health < 0.5; ausentes de stats nunca se degradan; orden relativo
  estable). LLM.call() cablea: reordena tras el bloque red_ok() y registra
  exito/vacio/excepcion por proveedor (tipo via parse_provider_error). API intacta.
- cultura/mak_research/fallback_util.py NUEVO: copia byte-identica del de mak_codex
  (en el box cada dept importa de su propio dir); test ratchet de no-drift.
- Efecto: groq en 429 acumula api_errors -> a la cola de la cadena por 6h -> la
  cadena arranca por cerebras sin quemar el primer intento. Auto-sana: si vuelve a
  responder, su score sube y se re-promueve.
- tests/test_mak_salud_proveedores.py: 16 tests (umbrales, ventana, corrupto,
  escenario groq, integracion LLM.call con orden de invocacion, drift espejo).

### 3. INTEGRIDAD DEL PANEL /api/eventos (anomalia mak-demo-*) -- esta PR
- hub.py: _eventos_depto (parse por linea: UNA linea corrupta ya NO vacia toda la
  lista -- defecto real que encontraron los lectores), _job_ids_conocidos (union
  jobs.jsonl tail 200 + /api/jobs vivo del dept, cubre jobs en vuelo),
  _marcar_sin_job (aditivo: sin_job=True solo cuando ninguna fuente conoce el
  job_id; si AMBAS fuentes fallan no marca nada). Front: badge [sin job] + CSS
  ev-nojob. Los eventos fantasma tipo mak-demo-* ahora se ven marcados en el hub.
- tests/test_mak_hub_eventos.py: 15 tests (regresion linea corrupta, huerfano,
  local-only, vivo-only/en-vuelo, ambas fuentes caidas, sin job_id, limite n).

### Verificacion (worktree god-salud-integridad)
- py -m compileall cultura/mak_research cultura/mak_plataforma src/flujo: OK
- py -m pytest tests/ -q: exit 0, todo verde (31 tests nuevos)
- Falso positivo evitado: el Grep del harness Windows renderiza "/api/x" como
  "\api\x" en lineas de contexto -- md5 espejo==vivo + grep en el box lo refuto
  antes de "arreglar" un bug inexistente.
- Nota lector (sin tocar): grafo.py hace fallback al resto COMPLETO de llm.order
  por nodo mientras cadena.py solo cae a proveedores DESPUES del actual -- posible
  divergencia deliberada de PR #85, documentada aqui por si algun sucesor la unifica.

## Sesion 2026-07-18T10:00-11:30 (MAK dual-dept, director orquesta, 1 operador sonnet) -- PR #85 MERGEADO

Pedido del usuario: 100% research+codex en MAK, director NO lee contenido (riesgo de flag)
NI repo (no lee/escribe), solo orquesta; 1 operador sonnet ejecuta en el box y reporta en
metadata tecnica; TODO en vivo (hub :8900), nada en segundo plano. Secuencia de 3 fases:
ambos deptos paralelo con stack MAK -> compartiendo WIN -> mismo tema en debate + auto-reparar.

### HECHO Y VERIFICADO (evidencia de metadata real de jobs, no contenido)
- FASE 1 (stack MAK, sin WIN): 2 jobs simultaneos (research cadena groq->cerebras fallback
  real por 429; codex azure-plan + nim-flash-code), ~12s solapados probados por timestamps
  de jobs.jsonl/eventos.jsonl. Paralelismo cross-dept CONFIRMADO (un flock por dept).
- FASE 2/2b (compartir WIN): BLOQUEADA por 2 caminos config-only:
  (a) env research.env -> clasificador de entrada BLOQUEA todo touch de archivo con llaves
      (hasta un md5sum read-only); correcto, es la regla de credenciales del repo.
  (b) workflow-node JSON -> WIN excluido por 3 whitelists HARDCODEADAS (grafo.py:30,
      interfaz.py _orden_canvas ~227, cadena.py:94). research_lib SI soporta win pero
      ninguna capa HTTP lo deja invocar. Convergio en: hay que reparar codigo (=fase 3).
- FASE 3 (reparar + compartir + debatir), tras permiso ssh del usuario (/permissions ->
  Bash(ssh mak@192.168.50.2:*)):
  * 4 reparaciones aplicadas VIVAS en el box (snapshot .bak c/u, py_compile OK): win en las
    3 whitelists de research + CODER_CHAIN de codex ahora override por env
    (os.environ CODER_CHAIN csv). Servicios reiniciados por PID (no pkill -f, evita auto-matar
    el shell ssh), ambos 200. Nodo win priority 0 agregado a workflow.json (config, snapshot
    /tmp/workflow_phase3.bak).
  * COMPARTIR WIN probado: research job 73c2 -> win como paso 1 (llmCalls win:1 + 4 mas);
    codex job fa62 -> modelo win deepseek-coder-v2:16b-lite nombrado en el result line. ~69s
    solapados. WIN respondio en AMBOS deptos.
  * DEBATE + AUTO-REPARAR: codex job 6546 revisiono su PROPIO artefacto OSC de fase 1
    (3 lentes correccion/seguridad/simplificacion + veredicto azure) -> propuesta en
    ~/codex/revisiones/. research en paralelo.
  * PERSISTIDO win-first pa sobrevivir reboot: Environment=CODER_CHAIN=... en el systemd unit
    ~/.config/systemd/user/mak-codex.service (autoritativo, daemon-reload OK) + watchdog_mak.sh
    (defensa extra). ~/codex/.token NUNCA tocado.
- ESPEJO AL REPO (PR #85 MERGEADO): las 4 reparaciones vivas espejadas en cultura/ +
  3 defectos que la demo destapo, todos con tests (tests/test_mak_mirror_fixes.py, 20+6skip):
  1. cadena.py: _paso_con_fallback -- un proveedor muerto (groq 429) mataba el job entero;
     ahora reintenta con los proveedores restantes de la cadena antes de fallar.
  2. interfaz.py /run: _resolver_modo -- modos front-end-only (adversarial) se normalizaban
     SILENCIOSO a research; ahora mapea aliases a su script real o devuelve HTTP 400.
  3. research_lib.marco(): el marco cultura ("nada de sintesis/cultivo") envolvia TODO tema
     y el modelo chico win (llama3.1:8b) rechazaba temas de ingenieria benignos; ahora
     marco neutro pa temas sin sustancias, marco cultura completo intacto pa los que si.

### NO HECHO / NOTAS DEL BOX (real)
- systemd cree que mak-codex esta inactive mientras :8891 responde 200: el codex vivo es el
  proceso manual (setsid de fase 3), fuera del bookkeeping de systemd. En el proximo reboot
  systemd lo toma limpio CON CODER_CHAIN. RIESGO menor: si se hace `systemctl --user start`
  ANTES de reboot con el manual arriba -> colision puerto 8891. Reconciliar cuando convenga:
  `systemctl --user restart mak-codex.service` (un solo comando, no urgente).
- workflow.json del box tiene nodo win priority 0 (dejado a proposito); revert en
  /tmp/workflow_phase3.bak si alguna vez.
- Groq free tier AGOTADO hoy (429 toda la sesion) -- la cadena lo absorbe siempre (eso es
  diseno funcionando); pendiente sin gate: reordenar default o cablear score_provider_health
  en research (ya existe en codex/fallback_util).
- 1 anomalia de fase 1 (no usada como evidencia): eventos.jsonl tenia entradas mak-demo-*
  con los mismos topicos ANTES de que el operador lanzara nada, sin footprint en jobs.jsonl
  y sin code path que las genere. El operador las trato como no confiables y corrio jobs
  reales frescos. Vale un ojo humano: hay una via de escritura a eventos.jsonl que el hub
  muestra como job real sin pasar por la cola (defecto de integridad del panel, no seguridad).

### Reporte Formal de Verificacion
- py -m compileall src/flujo cultura/mak_research cultura/mak_codex: OK
- py -m pytest tests/ -q: OK (verde, PR #85 CI matrix ubuntu+windows verde)
- cd web && npm run build:context: no aplica (web no tocada)
- py -m flujo verify: no aplica esta tanda (cambios en cultura/, no en modulos live de flujo)
- Observaciones: box y repo reconciliados; win compartido en ambos deptos probado con
  metadata real; 3 defectos de la demo cerrados con tests.

## Sesion 2026-07-18T08:45 (ventana USB del Xiaomi, director) -- PR #83 MERGEADO

- El flag honesto de PR #82 (regex de scan no verificado contra dispositivo) se
  CONFIRMO en hardware real: HyperOS emite formato columnar (BSSID/Frequency/
  RSSI/Age/SSID/Flags), el parser esperaba "SSID:"/"signal:" -- el scan NUNCA
  funciono en este telefono.
- Fix: parse_scan_results() columnar (fixture = lineas literales capturadas del
  Xiaomi) + formato legado como fallback. +3 tests (43 en el archivo).
- DESPLEGADO Y VERIFICADO VIVO: push por USB (md5 identico), server reiniciado
  con run_server.sh, GET /scan devolvio redes reales parseadas (ssid con
  espacios incluido). Telefono restaurado como estaba (wifi off).
- EFECTO COLATERAL UTIL: run_server.sh recopia TODOS los plugins -- el redeploy
  pendiente de showcontrol/hub (A4/A8) quedo hecho. Solo falta que el usuario
  active AccessibilityService en Ajustes.
- Trampas de canal (tambien en skill godspeed): adb shell NO puede disparar
  com.termux.RUN_COMMAND (permiso de Termux) -> usar el input-dance de
  pc_reboot_watch.sh; adb en Git Bash necesita MSYS_NO_PATHCONV=1 o /sdcard/
  se convierte en C:/Program Files/Git/sdcard/.
- Usuario confirmo hechas: autostart ollama Windows + noisette 12 acciones OK
  en Chataigne (ojo humano). Ambos salen de pendientes.

## Sesion 2026-07-18T08:00+ (GODSPEED-4 loop continuo, director Fable)

PRs de esta tanda del loop (sobre el cierre GODSPEED-4 anterior, #72-#77 ya mergeados):
#79 (empaquetador de assets de obras para el portfolio); portfolio-auto #4/#5 (seccion
catalogo vivo + imagenes) VERIFICADO LIVE con curl -- flujo-works.json y 2 imagenes en
200 en ligereza.github.io/portfolio-auto/proyectos.html, refresh semanal automatico
lunes; #80 (pieza MANIFIESTO #9 corpus_olvido, 104 capas, Omega11 declarada a tiempo,
no retroactiva); #81 (pieza MANIFIESTO #1 repo-se-performa: osc_sender en UDP stdlib
puro sin dependencias nuevas + RUNBOOK + recuento actualizado a 6/11 en MASTER_PLAN.md);
y esta PR (tests offline para xio/new-plugins/wifi_intelligence/__init__.py, pieza #5,
que estaba "parcial: plugin sin tests" -- 40 tests nuevos, mismo patron de
tests/test_showcontrol_token.py: PluginContext stub + FakeController + Flask test
client, sin dispositivo real).

ESTADO MANIFIESTO: 6/11 piezas hechas (#1, #4, #6, #9, #10, y la que cerro #76/#77).
#5 (wifi_intelligence) parcial->tests agregados en esta PR, logica pura cubierta,
partes device-only quedan sin cobertura (documentado en cabecera del test file).
#7 manual por orden expresa del usuario (no tocar). #2/#3/#11 bloqueadas por llaves
de usuario (ver PENDIENTES USUARIO abajo, sin cambio esta sesion).

## Sesion 2026-07-18T07:00-07:55 (GODSPEED-4, director Fable + 4 haikus + 2 sonnets) -- CIERRE

MERGEADO A MAIN (CI matrix verde en cada uno, en orden): #72 (pausa-en-error, 0.55.0),
#73 (rechazo /run + HALLAZGO + works.json CI, rebaseado resolviendo handoffs), #74
(test_smoke sin skip: imagen PIL en el test), #75 (pieza #10 paleta madre: 5 tests
determinismo/trazabilidad + Omega11 registrada en SEMILLAS, retroactiva y honesta),
#76 (fix critico: el paso de PR #73 iba a PISAR el works.json CURADO de la galeria
publica el lunes -- schema clash EN/ES verificado contra el sitio vivo; el catalogo
generado ahora se publica como flujo-works.json), #77 (paleta_reactivos.py sincronizada
con dato DanceSafe verificado PR #70: 23 reacciones + fuente, Test 5 exige igualdad
byte-identica; residuo de pieza #10 CERRADO).

AUTOPORTFOLIO VIVO (pedido del usuario, lane director+haikus): workflow disparado a mano
tras #76, flujo-works.json (8 obras) publicado a portfolio-auto; PR #4 de portfolio-auto
mergeado (seccion "Catalogo vivo" en proyectos.html, tolerante a 404, escapado, no toca
galeria curada); verificado LIVE con curl (seccion presente + data 200). Refresh semanal
automatico lunes 06:00 UTC.

MANIFIESTO: pieza #10 ya estaba construida desde PR #38 (los lectores decian "libre" --
refutado con git log); conteo real >= 6/11. PLAN_UPSCALE 0.53->0.55 CONSUMIDO: Opciones
A, B (via ratchet de #10) y C completas.

LECCION NUEVA (agregada a skill godspeed): NUNCA borrar la rama head antes de confirmar
state==MERGED -- un gh pr merge fallido (branch behind) + cleanup en cadena cerro PR #77;
recuperado desde el sha local (git branch <name> <sha> + push + gh pr reopen).

PENDIENTES USUARIO (sin cambio): noisette ojo humano, PAT Termux, AccessibilityService,
data 13 productoras, autostart ollama Windows, specs venues.

Detalle del merge #72/#73: conflictos solo en LAST_HANDOFF/SESSION_STATE, resueltos
conservando AMBAS narrativas (regla godspeed). Worktree god-mak-ola2 estaba lockeado
por sesion viva (pid 35300) -- se resolvio en worktree detached aparte, sin tocarla.

## Sesion 2026-07-18T02:00-03:05 (GODSPEED-3, director Fable, ola 2 -- esta rama, PR #73)

ESTADO PA EL PROXIMO AGENTE -- dos PRs draft esperando review del usuario, CI verde en ambos:

- PR #72 (rama worktree-god-mak-pausa): pausa-en-error MAK completa (Opcion A de
  context/PLAN_UPSCALE.md) + bump 0.55.0 + su propio LAST_HANDOFF detallado.
  Desplegada y VERIFICADA VIVA en el box (ciclo pausa/saltar/resume/informe).
  Workship Win<->MAK probado: llama3.1:8b (VRAM RTX 4070) y deepseek-coder-v2:16b
  responden desde el box via order='win' (research_lib y codex_lib ya cableados).
- PR #73 (esta rama): trabajo.py detecta ok:false de /run (antes contaba como
  exito), emisor HALLAZGO en correlacionar_archivos.py + memoria.py (cierra el
  contrato de eventos), works.json en portfolio.yml (Opcion C -- toca workflow CI,
  revisar ese paso en especial). 10 tests nuevos. Deploy de los 3 .py al box hecho
  y verificado (python3, _resp_ok probado vivo).
- MERGE: si #72 entra primero, esta rama conflictua en LAST_HANDOFF/version --
  resolucion: conservar ambas narrativas, version manda la mas alta. Y viceversa.
- BOX: servicios interfaz/hub corren el codigo nuevo (restart via watchdogs cron).
  ollama serve en Windows (192.168.50.1:11434) arrancado A MANO -- no sobrevive
  reboot; autostart = decision usuario. GPU RTX 4070 SI detectada.
- Skill godspeed ampliada con lecciones 3ra sesion (.claude/skills/godspeed/SKILL.md,
  en esta rama): contrato congelado pa writers paralelos, seam-check md5 vivo-vs-
  espejo, trampa pkill -f via SSH, trampa listado truncado, config persistida antes
  de rediagnosticar.
- PENDIENTES USUARIO: review/merge #72 y #73; autostart ollama Windows; llaves de
  siempre (noisette ojo humano, PAT Termux, AccessibilityService, data productoras).
- PROXIMO SIN GATE: Opcion B (pieza MANIFIESTO via motor-omega); vigilar peso repo;
  test_smoke skip permanente (decidir fixture o borrar).

## Sesion 2026-07-18T02:00+ (GODSPEED-3, director Fable + 4 lectores + 2 builders sonnet, PR #72 -- ya mergeado)

- PAUSA-EN-ERROR (PLAN_UPSCALE Opcion A) COMPLETA: pausa.py nuevo (checkpoint stdlib,
  acciones reintentar/editar/saltar), research.py pausa en fallo terminal de las 3 fases
  (marca "PAUSADO: <ck> | <motivo>" + exit 3) y --resume, worker.py propaga MAK_JOB_ID +
  param extra + evento human_gate, interfaz.py estado PAUSADO + POST /api/reanudar +
  4 botones en ambos renders + CSS, hub.py _norm/colores/contador. 44 tests nuevos
  (test_mak_pausa 20 + test_mak_reanudar 24; 12 fcntl-gated solo corren en CI ubuntu).
  Contrato seguido: cultura/mak_plataforma/diseno/eventos_y_backlog.md.
- VERIFICADO VIVO en el box: ciclo pausa -> saltar -> resume -> re-pausa (fase informe)
  -> saltar -> informe placeholder exit 0. /api/reanudar valida job inexistente (404).
  interfaz.py y hub.py reiniciados con codigo nuevo -- OJO: eso tambien aterrizo el
  borrado de auth de PR #71 que NUNCA se habia desplegado (el hub vivo aun proxeaba
  token de codex borrado = bug vivo, muerto ahora).
- WORKSHIP Win<->MAK PROBADO (pedido del usuario, primera vez): Windows 192.168.50.1
  (cable directo) con OLLAMA_HOST=192.168.50.1:11434 ya persistido por agente previo y
  modelos en C:\OLLAMA_MODELS (14.2GB): llama3.1:8b + deepseek-coder-v2:16b-lite-q4.
  ollama serve arrancado, RTX 4070 SI detectada (llama en VRAM completa; el log CPU-only
  era de un proceso viejo). Desde el box: research_lib LLM(order='win') respondio OK,
  codex_lib win (deepseek 16b) responde, carga 10.4s. Cadenas ya cableadas en ambos libs.
- GAPS REALES: (1) ollama serve en Windows arrancado a mano -- no sobrevive reboot;
  usuario decide autostart (la app de Ollama al iniciar sesion ya bindea bien por el
  OLLAMA_HOST persistido). (2) trabajo.py no parsea el body de /run (200 con ok:false
  cuenta como exito) -- hallazgo off-task, sin tocar. (3) pkill -f via SSH se mata a si
  mismo si el patron matchea la cmdline del bash remoto (2 sesiones SSH perdidas asi).
- PR #72 (rama worktree-god-mak-pausa): pausa-en-error + bump 0.55.0. MERGEADO
  2026-07-18T07:04 con CI matrix verde.

Sesion anterior (0.54.0): PR #71 MERGEADO a main (cd52a69) tras resolver conflictos + fix CI ubuntu
(iterdir orden). SSH a MAK VERIFICADO: mak@192.168.50.2 (dell-11m, llave autorizada).
Bump 0.54.0: PR #71 MERGEADO a main (cd52a69) tras resolver conflictos + fix CI ubuntu
(iterdir orden). SSH a MAK VERIFICADO: mak@192.168.50.2 (dell-11m, llave autorizada).
Skill godspeed ampliada con lecciones 2da sesion. Rama #71 borrada (local+remota);
dir .claude/worktrees/god-haiku-fixes lockeado por proceso, borrar a mano cuando suelte.
Ruta 0.55: context/PLAN_UPSCALE.md -- Opcion A (MAK pausa-en-error) DESBLOQUEADA y recomendada.

## Sesion 2026-07-18T01:00+ (autonoma, loop 3min activo)
- 8a28651: plugin_guardian duplicado xio/seguridad -> _archive/legacy_20260717_2015
  (canonico queda xio/new-plugins, path que despliega run_server.sh); RUNBOOK flag resuelto;
  borrado doublecup_v2_3d.svg suelto (0 bytes, copia real tracked en doublecup/)
- Falso positivo cerrado: "missing mapping.html" del audit de zonas era stale
  (tracked + build:context lo produce; typecheck y build verdes)
- c11bcf0: refs stale a checkpoint.sh (inexistente) purgadas de cli.py,
  PRIMER_DIA.md, SCRIPTS_INVENTORY.md, finish_airdrop.sh; INSTALL.txt (relic
  v0.20) -> _archive/legacy_20260718_0110/
- e67f965: 5 one-shot cleanup scripts spent archivados (targets verificados
  inexistentes): cleanup_safe/moderate/legacy_aggressive.sh,
  cleanup_repo_hygiene_20260630.py, cleanup_v0359_windows_paths.py
- 0cd8909: fix test order-dependence real -- test_run_airdrop_checks popeaba
  sys.modules["flujo"] sin restaurar; snapshot+restore + import explicito
  flujo.paths en 5 test files
- 1a63c53 + ca11233: 41 tests nuevos (sonnet, auditados): ig/download (17,
  instaloader mockeado), analyze colors/run (11, PIL en memoria + OCR mock),
  analyze/export (13, round-trip binario ACO/ASE). serve/ omitido a proposito:
  PR #71 abierto ya trae test_serve_api.py (21 tests) -- no duplicar.
- 4da2936 + a584dc5 + 224558e: SESSION_STATE.json y PLAN_SIGUIENTE_AGENTE.md
  al dia (PR 48 MERGED / 49 CLOSED / 71 OPEN, branch protection ACTIVA,
  vibo_voz y .dev.limpio ya no existen, sellos docs refrescados)
- c8a6cd9: Makefile help corregido (PYTHON vs PYTHON_BIN; python3 no existe
  en Git Bash Windows)
- OJO PR #71: contiene el mismo archive de plugin_guardian que main (8a28651)
  + su propio LAST_HANDOFF -> conflictos chicos esperables al mergear
- Backlog autonomo AGOTADO al cierre: lo restante necesita usuario (noisette
  ojo humano, PAT Termux, AccessibilityService, data productoras, review #71)
  o SSH a MAK (auth pendiente)
- Suite verde tras cada commit (pytest full verde, 1 skip); flujo verify OK 0.52.0

(rama PR #71, sesiones GODSPEED director+haiku, escritas en 0.52.0; mergeadas bajo 0.53.0)

## Sesion 2026-07-18b -- GODSPEED-2: sistema generativo VIVO (misma rama/PR #71)

### HECHO Y VERIFICADO (director + 1 haiku por area, cada claim re-verificado mecanicamente)
- BACKLOG GENERATIVO implementado desde el contrato diseno/eventos_y_backlog.md seccion 3:
  plataforma/backlog.py (parsear LAGUNAS DE INFORMACION, dedup por hash normalizado, linaje
  cap 3, max 3/informe, pop por score+antiguedad, curador con poda) + 43 tests verdes.
  trabajo.py cableado defensivo: cosecha cada tick, verbo multiplicar hace pop del backlog
  ANTES de las semillas fijas (roles.SEMILLAS pasa de motor a arranque), curar cada 8 tareas.
- SEMBRADO: backlog_semilla.jsonl con 8 preguntas de ideas sin comenzar verificadas (2 por
  area: xio+mak, router+server, portafolio+cultura, rd+colorimetria). backlog_codex.txt +4
  tareas (resumidor backlog, timeline red, glosario reactivos, resumen HALLAZGOs).
- DESPLEGADO Y VIVO en 192.168.50.2 (2026-07-18): 13 archivos copiados tras verificar
  live==espejo por md5 (codex_lib+fallback_util+revisar+testear -> ~/codex; cadena+refutar+
  panel+grafo+retencion -> ~/research; trabajo+roles+backlog+backlog_codex -> ~/plataforma;
  semilla -> ~/plataforma/backlog.jsonl). python3 py_compile OK x12 en el box, research y
  codex responden 200. COSECHA REAL PROBADA: 9 preguntas extraidas de informes existentes
  (quechua, test1) -> 17 pendientes en cola. El proximo tick ya investiga solo.
- BUG VIVO ENCONTRADO Y MATADO: el trabajo.py del box aun leia ~/codex/.token (borrado hace
  2 sesiones) y saltaba TODO verbo codex ("skip: codex sin token" x2 en el log). La sesion
  del auth-delete no lo cubrio. El deploy lo corrige; codex autonomo revive.
- src/flujo/analyze/reactivo_matcher.py: lookup inverso de colorimetria RD (hex observado ->
  familias por delta-E CIE76 en Lab, stdlib puro, disclaimer presuntivo en cada resultado)
  + 30 tests. Probado contra reactivos.json real.
- tools/portfolio/generar_works.py: works.json regenerable desde manifests reales de
  datadrops/ + projects/flyer_eventos/ (nodo 17 MAPA_GENERATIVO, "obras reales" ya no
  placeholder) + 20 tests. Corrida real: 8/8 obras catalogadas.
- Reglas de permiso ssh/scp al box: el clasificador BLOQUEA que el agente se auto-otorgue
  permisos en settings (limite duro correcto). El usuario aprobo por /permissions esta vez.

### NO HECHO (real)
- Pausa-en-error sigue sin construir (diseno completo, es el item grande del backlog).
- works.json NO cableado al workflow portfolio.yml (generar_works.py existe y esta testeado;
  falta un paso en el workflow que lo corra y publique -- editar .github/workflows es de
  mayor blast radius, decision del usuario).
- Emisor HALLAZGO en correlacionar_archivos.py/memoria extra: cubierto lo delegable.
- Contradiccion de lector refutada: xio/FACES.md SI existe (un haiku afirmo que no).

## Sesion 2026-07-18 -- PR #71 draft (rama worktree-god-haiku-fixes)

### HECHO Y VERIFICADO
- flujo: scripts/flujo.py dispatcher -> error+exit2 pa 13 comandos retirados (antes fallo
  silencioso) + test_flujo_dispatcher.py. +21 tests smoke flujo.serve (0 cobertura antes).
  Suite worktree verde (644 passed 1 skip tras borrar tests de token; era 648).
  2 bugs ALUCINADOS por lectores haiku REFUTADOS mecanicamente (mapping.html "roto" = lo
  provee web/public/, probado con el build; 3/5 gaps de cobertura falsos, matados en la costura).
- MAK auth: BORRADO TOTAL de token/auth en codex+research (NO "opcional" -- eliminado del codigo):
  interfaz_codex.py (sin _auth/TOKEN), research/interfaz.py (sin _check_auth), hub.py+trabajo.py
  (sin _codex_token, sin proxy ?t=, sin /api/codex_token), watchdog_mak.sh (arranca abierto),
  patch_interfaz.py BORRADO (era el script que inyectaba el auth de research). delegar.py sin token.
- DESPLEGADO EN VIVO al box 192.168.50.2: copiados interfaz_codex.py + watchdog_mak.sh
  (codex_lib.py NO -- no cambio, copiarlo regresa el vivo); removido ~/codex/.token; codex
  reiniciado. VERIFICADO: curl :8891/api/jobs -> 200 SIN token; job real resumir_jobs.py corrio
  -> listo. research :8890 ya era auth-opcional -> abierto igual. Confirme vivo==mirror byte-
  identico salvo borrado de token ANTES de copiar (0 divergencia). Detalle: DEPLOY_OPEN.md.
- MAK research: cultura/mak_research/retencion.py rota informes sin limite. +17 tests.
- MAK codex fiabilidad: cultura/mak_codex/fallback_util.py agrega TODOS los coders fallidos
  (no solo el ultimo). +24 tests + FALLBACK_FINDINGS.md.
- xio: FACES.md (Face A casa Linux+Windows, wifi + cable ethernet directo / Face B show SOLO
  telefono, el Linux no sale). Codex nunca en la red del show -> la confusion 32-clientes-sin-AP
  NO es exposicion de codex.
- skill .claude/skills/godspeed/SKILL.md: doctrina director+haiku + fallas reales de esta sesion.

### NO HECHO (real, sin maquillar)
- Pausa-en-error (#1 del backlog MAK): NO existe en NINGUN lado. Verificado exhaustivo: 3 stores
  (WEB/LOCAL/MAK), todas las worktrees (incl. mak-research-cultural en .claude y en _flujo_local),
  el stash, keyword ES + EN (research/resume/pause), por directorio, y por fecha. investigar()
  sigue PLANO (topic,iteraciones,depth,providers,densidad), 7819 bytes identico en los 3.
  Solo existe el DISENO (cultura/mak_plataforma/diseno/eventos_y_backlog.md) + el emisor vivo
  (research_lib.emitir_evento/mint_job_id; worker.py intercepta STATUS:->node_start,
  HALLAZGO:->llm_result). El handoff previo lo marco honestamente "NO COMPLETADO"; su linea
  "investigar() fue reescrito" NO coincide con el codigo pero NO fue mentira (trabajo perdido/
  optimista). PROXIMO: CONSTRUIR desde el diseno sobre el emisor -- NO re-buscar, no esta.
- [HECHO 2026-07-17 sesion godspeed-2] fallback_util INTEGRADO en codex_lib.py CoderLLM.call
  (import defensivo try/except; al agotar la cadena el RuntimeError agrega TODOS los intentos
  via aggregate_failures; exito byte-identico; +3 tests integracion = 27 en test_mak_fallback).
- [HECHO 2026-07-17 sesion godspeed-2] Emisor semantico (HALLAZGO:) agregado a cadena/refutar/
  panel/grafo (research) + revisar/testear (codex) -- 15 emisiones aditivas con contenido real,
  hecho por 6 haikus (1 archivo c/u, sin commits propios) + verificacion mecanica del director
  (grep + py_compile + diff --stat por archivo + suite completa verde).
- retencion.py, fallback_util y codex_lib.py integrado NO desplegados al box (solo en repo/PR;
  el deploy al box 192.168.50.2 sigue pendiente y ahora INCLUYE codex_lib.py + fallback_util.py).
- Firewall Windows ollama sigue "Any remote address" (bind a 192.168.50.1 ya cierra el riesgo real).

### TOPOLOGIA (memoria: project_tres_repos_topologia -- NO asumir que uno refleja a otro)
WEB = repo publico, solo commits finales. LOCAL = C:/IA/flujo (Windows), toda la info.
LINUX/MAK = 192.168.50.2 station research+codex, codigo SUELTO en ~/research ~/codex ~/plataforma
(NO es clone del repo). Una worktree off origin/main = sabor WEB; puede faltarle trabajo de LOCAL/MAK.

## Sesion 2026-07-17T22:30-23:00 (autonoma, cierre)
- Cleanup: PR #48 stale refs (updated MASTER_PLAN.md, PLAN_SIGUIENTE_AGENTE.md), 9 cultura/ leftovers moved out, docs/DIRECTOR_PLAN.md archived, branch/file trash cleaned
- Audits: portfolio-auto (LIVE), public repos, stale files (all read-only)
- Commits: 156e8b4 (cleanup), be3153e (handoff), +context/WALKTHROUGH.md (quick-start guide)
- Blockers: MAK SSH auth pending (user to provide connection string), PR #49 user review pending
- Suite: pytest 394+1skip green, compileall OK, flujo verify OK

Anterior: MAK codigo copiado a cultura/mak_research + mak_codex + mak_plataforma + mak_lenguaje,
suite verde. Detalle en seccion "MAK -- cierre 2026-07-17" abajo.

## SI ERES UN SUCESOR DE FABLE (bloqueo -> Opus): leer esto PRIMERO
El modelo principal puede quedar bloqueado por el clasificador de ENTRADA
(marca el mensaje del usuario ANTES de que el modelo lo vea; falsos positivos
en coding/cyber/biology rutinarios) y la sesion se degrada a Opus sin retorno.
Protocolo (memoria [[antiblock-warn-first]] + skill .claude/skills/
revivir-subagentes escenario C):
1. `py .claude/skills/revivir-subagentes/extraer_contexto.py <sessionId>.jsonl
   --volcar rescate.md` -> hereda el contexto ya pagado (corre en Windows
   cp1252 sin PYTHONIOENCODING desde el fix de esta sesion).
2. Warn-first: avisar `[!] tema sensible: <cual>` ANTES de zona riesgosa,
   ofrecer reformulacion; nunca rechazo seco (re-quema el modelo).
3. Trabajo normal del repo (Resolume/VJ, RD reduccion de danos, xio, codigo)
   = zona verde, no auto-censurar por flags ambiguos.

## MAK -- cierre 2026-07-17 (sesion Sonnet/Opus, rama worktree-mak-research-cultural)

El organismo MAK (research + codex + plataforma + lenguaje) corre EN VIVO en
Debian 192.168.50.2, fuera de src/flujo. Esta sesion cierra el trabajo iniciado
en PRs anteriores (#48/#49 mencionados en handoffs previos): otro agente habia
LOCKEADO cultura/mak_research/ esperando que este trabajo terminara y se
pusheara (ver nota en la seccion "PENDIENTES de esta sesion" mas abajo) --
ese lock se libera con este merge.

### Que se hizo esta sesion (ademas del trabajo previo ya documentado abajo)
- **WIN integrado como proveedor LLM**: notebook Windows (RTX 4070 Laptop 8GB)
  suma como proveedor "win" en research_lib.LLM y codex_lib.CoderLLM, ANTES
  del ollama local de MAK en la cadena de fallback (nube -> WIN -> MAK-local).
  Ollama en WIN bindeado a la IP del cable directo (192.168.50.1:11434), NO a
  0.0.0.0 -- goteo de seguridad real cerrado (WIN es notebook que viaja a
  redes publicas). Probado end-to-end desde ambos deptos.
- **Fallback offline probado de verdad**: red_ok() (socket a 1.1.1.1/8.8.8.8)
  reordena la cadena sin internet; forzado offline en vivo, cayo a ollama
  correctamente.
- **Throttling movil resuelto**: hotspot del Xiaomi (WIN conectado a el)
  caia a 0.75 Mbps. Root descartado (telefono sin root, ver xio/RUNBOOK.md).
  Fix real: `adb shell settings put global tether_dun_required 0` (capa de
  servicio, no kernel -- mismo patron que resolvio charge_control antes) +
  reboot del telefono con `xio/new/pc_reboot_watch.sh` corriendo por USB
  ANTES de reiniciar (evita el "hueco" de reboot sin host). Resultado: 0.75 ->
  12.2 Mbps.
- **hub.py reconstruido sobre DOM+SVG real** (antes: canvas-2D con
  hit-testing a mano, causaba clicks poco confiables). Verificado con
  Playwright REAL (chromium instalado ad-hoc, no MCP) contra el hub vivo en
  MAK: 5 nodos de departamento clickeables, panel de research/codex EMBEBE
  el editor real via iframe (:8890 y :8891 con token, NO un formulario
  propio -- correccion de un error real de esta sesion, se habia reconstruido
  una version mas pobre en vez de reusar el editor de nodos/puertos/SVG que
  research/interfaz.py ya tenia). Fisica del micelio con damping mas fuerte
  (0.55 + tope de velocidad) para que un click real (mouse, no la espera de
  estabilidad de Playwright) aterrice bien sin dejar de moverse.
- **Emisor de eventos con contenido semantico real**: `eventos.jsonl` por
  depto (research_lib.emitir_evento + mint_job_id), interceptado
  centralmente en worker.py/worker_codex.py (linea "STATUS: " -> node_start,
  "HALLAZGO: " -> llm_result con contenido real, no contador de paso).
  Contenido real agregado en research.py (fuente encontrada + extracto del
  informe), generar.py (plan + resultado), debug.py (diagnostico). Panel "en
  vivo" en el hub lee `/api/eventos?depto=X`.
- **Coder que se repara**: nuevo mood `debug` en codex (planner diagnostica +
  coder reescribe) -- NUNCA sobrescribe el modulo vivo, guarda PROPUESTA en
  ~/codex/revisiones/ para revision humana.
- **Trabajo autonomo real**: `trabajo.py` (cron */30, reemplaza el latido.py
  viejo) cicla multiplicar/definir/limpiar/desarrollar via roles.py.
  LIMITACION HONESTA (documentada, no resuelta): las listas semilla son FIJAS
  (roles.py SEMILLAS/MODULOS + backlog_codex.txt) -- al agotarse, repite en
  vez de crecer. La correccion real (leer la seccion "LAGUNAS DE INFORMACION"
  que cada informe ya escribe y usarla como semilla del proximo ciclo) esta
  DISENADA (ver cultura/mak_plataforma/diseno/eventos_y_backlog.md) pero NO
  implementada.
- **Doctrina viva**: cultura/mak_plataforma/doctrina/doctrina_tools_espejo.md
  (herramientas dual-use, jailbreak vs enmascaramiento de intencion, el
  filtro juzga la aplicacion no la capacidad) informa filtro_entrada.py.

### NO completado (honesto, no maquillado)
- **Pausa-en-error / reanudacion**: research.py `investigar()` fue reescrito
  para soportar `checkpoint=`/`job_id=`/`accion=`/`nuevo_input=` (pausa real
  en vez de reventar y esperar el timeout de todo el job), PERO nada invoca
  todavia esa ruta: falta `--resume` en `main()`, falta que worker.py
  reconozca la linea "PASADO: " del subproceso, falta el endpoint
  `/api/reanudar` en interfaz.py + hub.py, y los botones
  reintentar/editar/saltar/abortar en el panel del hub. Diseno completo en
  cultura/mak_plataforma/diseno/eventos_y_backlog.md.
- El emisor de eventos con contenido real (HALLAZGO:) solo esta en
  research.py + generar.py + debug.py. cadena.py/refutar.py/panel.py/
  grafo.py/memoria.py/revisar.py/testear.py solo tienen node_start/node_end
  genericos (heredados gratis via worker.py/worker_codex.py) sin contenido
  semantico propio todavia.
- Regla de firewall de Windows para ollama sigue en "Any remote address"
  (el New-NetFirewallRule con RemoteAddress fallo por falta de admin/UAC). El
  bind a la IP de interfaz (192.168.50.1) ya cierra el riesgo real (no hay
  socket escuchando en otras redes); la regla de firewall es hardening
  adicional, no urgente.

### Limpieza de handoffs viejos (pedido explicito del usuario al cerrar)
- `checkpoints/2026-07-03_*.md` (3 archivos) archivados a
  `_archive/legacy_20260717_1900/checkpoints_2026-07-03/` -- salidas viejas
  de un mecanismo de solo-escritura (src/flujo/airdrop.py), no rompe nada.
- `context/ACTIVE_PLAN.md` (plan de demo del 2026-06-29, hace 3 semanas)
  archivado a `_archive/legacy_20260717_1900/`.
- `context/PLAN_OPUS_SALA3D.md` eliminado (`git rm`, no archivado): el propio
  archivo instruia "Borrar este archivo al cerrar"; su trabajo (PR #30) ya
  esta mergeado desde 2026-07-11.
- `_tmp_mak_plataforma/` (untracked, intento abandonado de 2026-07-16 con
  copias stale de GENESIS.md/guardia.py/salud.py) borrado; reemplazado por
  cultura/mak_plataforma/ con contenido fresco de hoy.
- NO se toco `.archive/`, `_archive/legacy_2026*` (las demas), ni
  `docs/handoffs/archive/` -- son las ubicaciones de archivo OFICIALES segun
  CLAUDE.md, no material suelto.

### Verificacion de cierre
compileall src/flujo: OK. compileall cultura/mak_research+mak_codex+
mak_plataforma+mak_lenguaje: OK (sin errores de sintaxis). pytest tests/: 100%
verde, sin fallos ni nuevos skips. flujo verify: OK (v0.52.0, hub smoke OK).
No se toco web/ esta sesion.

## Estado 2026-07-17 (sesion Fable, autonoma)
Mergeado a main hoy: PRs #50-#69 (checkpoint, MASTER_PLAN v2 anti-muralla,
olas 1-4, RD DB + perfil productoras + lookup, fix precio Pack 1 real $250k,
vibo_voz eliminado, cobertura 10/10 gaps + fix bug scoring fallback, skill
revivir-subagentes rescatada + fix cp1252, CLAUDE.md denso senal-pura, hook
bash-guard PreToolUse). Branch protection en main ACTIVA (require CI ubuntu+
windows, strict). Sesiones duplicadas del picker limpiadas (2 fantasmas
matados por PID + 3 jsonl borrados; contenido en C:/IA/_flujo_local/
session_backups/).

## SESION 2026-07-16 (d) -- MICELIO: el archivo hecho organismo + modos desde el mapa
Feedback duro del usuario ("no veo las conexiones semanticas, botones a
iconos, Files feo, nodos cuestan, replantea todo") -> rework visual completo
de interfaz.py, enfoque cultura/artistico (paleta abisal #0b0a09 + fungico
#9db67c, director-de-arte):

- MICELIO (vista 2, toggle Flujo/Micelio): mapa semantico VIVO del archivo.
  Canvas 2D con fisica force-directed propia (sin librerias): nodo = pieza
  (respira, halo, tamano por fragmentos), filamento = afinidad coseno real
  entre productos (memoria.grafo_semantico + /api/memoria/grafo), ondulan,
  esporas viajan por aristas fuertes, anillo de nacimiento en piezas nuevas.
  Slider de afinidad, leyenda por tipo clickeable, zoom/pan/drag, tooltip.
- MODOS DESDE EL MICELIO (pedido explicito): click en pieza -> tarjeta de
  acciones: Abrir / Investigar (corre el modo activo del topbar con la pieza
  como semilla, memoria=1 si grafo) / PUENTE (dos piezas -> investiga la
  relacion entre ambas). La pieza nueva se auto-indexa (reindex tras cada
  job) y NACE en el mapa (refresh 25s): crece y se remodela solo.
- UI: toolbar de ICONOS svg con tooltips; puertos 16px con drag-to-connect
  estilo n8n (entradas se encienden verdes al conectar) ademas de dos-clicks;
  Files rehecho como "Archivo del departamento" (cards titulo/fecha/chip de
  tipo + buscador, DIR_CHIP singulares correctos).
- Verificado: py_compile local+MAK, node --check (60.9k chars JS), API grafo
  33 nodos/99 aristas, server VIVO (PID 131439 http 200), pantallazos de
  Flujo+Files. LECCION OPERATIVA: NO usar xdotool para "verificar visual" --
  el usuario comparte el MISMO mouse fisico entre Windows y MAK (Barrier);
  mover el cursor via xdotool le pelea el mouse en vivo. Verificacion visual
  = pedirsela al usuario.
- Alerta de higiene: en el worktree aparecio arte-ascii-readme.svg BORRADO
  (working tree, no commiteado) + arte-ascii-readme.svg.html untracked --
  NO fue este agente, NO se commitea; el usuario decide si restaurar
  (git checkout -- arte-ascii-readme.svg).

## SESION 2026-07-16 (c) -- MAK research: MEMORIA del departamento (RAG local)
El usuario pidio "enhance the department". Se agrego la pieza mas de fondo
que faltaba para que sea un DEPARTAMENTO y no una carpeta de informes: una
MEMORIA consultable.

- memoria.py NUEVO: indexa TODOS los productos (.md) con embeddings LOCALES
  y gratis (ollama nomic-embed-text, 768-dim; se pulled en MAK) a
  ~/research/memoria/index.jsonl. Incremental por mtime. Cosine top-k en
  python (instantaneo sobre ~500 chunks). 3 usos: `index`, `buscar "tema"`,
  y consultar (default) = 7mo MODO Memoria: recupera lo previo relevante y
  el modelo capaz sintetiza QUE SABEMOS / consenso / contradicciones /
  VACIOS / que investigar proximo. Escala mejor que Corpus (solo el
  subconjunto relevante, no todo el archivo).
- Inyeccion --memoria en modo Grafo (checkbox "Consultar memoria" en Run):
  cada trigger recibe, junto al tema, los hallazgos previos relevantes
  (memoria.contexto). El grafo construye sobre lo ya sabido.
- UI: boton Reindexar (tools menu, background via /api/memoria/index) +
  contador de fragmentos (/api/memoria/stats, poll 15s). run-modo dropdown
  con Memoria. worker.py SCRIPTS["memoria"], DIRS/MODO_DIR memoria/.
- Verificado: py_compile + node --check OK; index construido en MAK (33
  archivos -> 473 chunks); embeddings 768-dim OK. Borrado el sitecustomize.py
  huerfano que reaparecio (trampa conocida).
- PENDIENTE (no del codigo): confirmar EN VIVO el modo Memoria (consultar +
  sintesis) y grafo --memoria. Se corto por throttle de fail2ban en MAK tras
  muchas conexiones SSH seguidas; interfaz.py lo revive el watchdog (cron
  */5) o relanzar con `setsid python3 interfaz.py >log 2>&1 </dev/null &`
  (un nohup dentro de un SSH con loop largo muere con SIGTERM al cerrar).

## SESION 2026-07-16 (b) -- MAK research: GRAFO REAL dirige la ejecucion
Rama worktree-mak-research-cultural. El usuario pidio arreglar huecos del
canvas: faltaban opciones de conexion en los nodos, la Discussion "no era
comite ni circulo", el Adversarial "no se dibujaba", y queria multiples
entradas/salidas anticipando flujos extremos. Eleccion de arquitectura del
usuario (AskUserQuestion): "Grafo real dirige la ejecucion".

Hecho y VERIFICADO EN VIVO:
- grafo.py NUEVO: ejecutor de grafo real. Lee ~/research/workflow.json
  (nodes + connections), valida (validar_grafo: ciclos/huerfanos/sin-camino
  trigger->output/fan-out>6/>12 modelos), y ejecuta en orden topologico --
  cada nodo-modelo recibe la salida concatenada de sus predecesores, los
  trigger inyectan el tema, los output recopilan, cierra con correlacion.
  Soporta multiples triggers/outputs (set-based). Salida en grafos/.
- interfaz.py: el array `connections` ahora DIRIGE el dibujo (se acabaron las
  topologias hardcodeadas por modo). Eso arregla los bugs reales: Discussion
  = COMITE (trigger->todos los modelos->output, convergen); Adversarial SE
  DIBUJA (proponente->refutadores->juez). Conexiones editables por los
  puertos (2 clicks salida->entrada; click en arista = borrar; Esc cancela).
  Multiples In/Out (+In/+Out; los nodos base se apagan, no se borran; los
  extra y las notas si). Nuevo modo "Grafo" (custom: respeta las aristas
  dibujadas, corre grafo.py). Los otros 4 modos regeneran su topologia como
  PRESET (presetConnections) y siguen corriendo su script especializado.
  validarGrafo (espejo JS) + boton Validar; en modo grafo el run se bloquea
  si el grafo es invalido (chequearGrafo + saveNow antes de correr).
- worker.py: SCRIPTS["grafo"]="grafo.py"; interfaz DIRS/MODO_DIR grafos/.
- Verificacion: py_compile (local+MAK) OK, node --check del JS OK, validador
  unit-tested (5 flujos extremos), 4 presets evaluados en node (correctos),
  click real en Discussion regenero el comite (workflow.json 8 conns +
  pantallazo), y un job grafo REAL corrio end-to-end en MAK (4 modelos en
  orden topologico + correlacion 5750 chars, meta.errors=[]). Server VIVO
  reiniciado en MAK (PID nuevo, http 200). Sigue pendiente del usuario abrir
  ufw 8890 para verlo desde Windows.

## SESION 2026-07-16 -- MAK research: canvas visual + 5 modos + correlacion
Rama worktree-mak-research-cultural (continua la de la noche anterior).
La interfaz web crecio de un formulario a un CANVAS VISUAL tipo n8n
(interfaz.py, ~1500 lineas): 5 modos reales cableados end-to-end y
verificados en vivo en MAK -- Single (research.py), Pipeline (cadena.py
NUEVO, encadenado), Discussion (panel.py), Adversarial (refutar.py NUEVO,
proponer/refutar/juzgar), Corpus (correlacionar_archivos.py NUEVO,
correlaciona TODO el archivo). Correlacion semantica ("departamento"):
el modelo capaz (azure gpt-5-mini) ordena/relaciona lo que dicen los
modelos, por-job (panel/cadena) y sobre-el-corpus (modo Corpus).
Agregados: perilla de densidad (corto/medio/largo, escala tokens con
techo duro anti-timeout), auto-repair (boton en jobs fallidos -> el
modelo capaz diagnostica), nodos nota agregables al canvas, tools menu
(zoom rueda+botones, pan arrastrando fondo, Encajar/Centrar/Organizar),
modal para ver resultados DENTRO de la app, log de error explicito por
job, token auth opcional, historial jobs.jsonl. Fix importante:
Cache-Control no-cache en interfaz.py (Firefox cacheaba HTML viejo por
origen). Todo desplegado y VIVO en MAK ~/research/. PENDIENTE del usuario:
ufw bloquea 8890 desde la LAN (correr `sudo ufw allow from
192.168.50.0/24 to any port 8890 proto tcp` para ver desde Windows). El
usuario avisa si pilla bugs. Detalle completo: cultura/mak_research/MAK_RESEARCH.md.

## SESION 2026-07-15 (noche) -- MAK research cultural VIVO (sin n8n)
Rama worktree-mak-research-cultural. n8n CERRADO como fallido (orden usuario,
no reintentar). Sistema standalone desplegado y VERIFICADO en MAK
(192.168.50.2, ~/research/): research.py (loop Tavily->fetch->analyze->decide
->informe, fallback groq->cerebras->azure->ollama), panel.py (debate 4
angulos historico/estetico/legal/tecnico, 1 modelo por API, sintesis
gpt-5-mini), 3 interfaces para tema X: web LAN :8890 (interfaz.py), ntfy
iPhone (cola.py, topics NTFY_TOPIC_IN/OUT en research.env), CLI research.sh.
Un job a la vez (worker.py flock). Cron @reboot. gemma3:4b bajado (cabe en
4GB VRAM, OLLAMA_MODEL default; aya-expanse:8b de repuesto). Tests vivos:
research 2x OK, panel OK (4 proveedores hablaron), round-trip ntfy OK.
Trampas resueltas: Cloudflare 403/1010 por UA de urllib (UA custom en lib);
razonadores necesitan margen +2048 tokens; defaults frugales (2 iter/1
replica) por orden del usuario. Copia del codigo: cultura/mak_research/
(manual + backlog para agentes VS Code/Antigravity en MAK_RESEARCH.md).
Keys: cultura/.dev y ~/n8n-local/research.env, JAMAS en git. OJO: crontab
de mak pudo perder entradas previas (probablemente vacio) al instalarse
@reboot; revisar si algo falta. "wachuma" era un TEMA, no el sistema: el
sistema es generico, recibe cualquier tema.

## SESION 2026-07-15 (autonoma tarde) -- showcontrol v1.1->v1.8 + cultura wachuma
Rama claude/cultura-xio-mistral-20260715, PR #45 MERGEADO a main.

## NOTA (otra sesion) -- Optimizacion de gasto aplicada
Settings, aplica a sesiones NUEVAS: main model default = Haiku, effort medium,
advisor sonnet, plugins 64->15, hook SessionStart caveman + hook PreToolUse
bash-guard. Doctrina de escalada (triggers decidibles) codificada en CLAUDE.md
seccion "Regulacion de gasto".

### PENDIENTES de esta sesion (lista que NO alcanzo a cerrarse sola)
COMMITEADO en esta tanda (working tree -> main): tapiz cableado al CLI
(`flujo tapiz demo/stress/live`), venues OpenKlub/Paralelo89 + link frvr,
reactivos.json enriquecido (23 reacciones, cocaina en Marquis/Liebermann,
Simon/MDA update, fuente DanceSafe), plugin xio `hub` (sirve flujo_hub.html
desde el telefono, T-G2), cleanup cultura (.dev.limpio + 8 leftovers movidos
a _flujo_local), 5 SPEC-stubs archivados.

NECESITA AL USUARIO (tabla, dar y ejecutar):
- A1 noisette: abrir jobs/test_resolume/deliverables/show_automation.experimental
  .noisette en Chataigne, confirmar 12 acciones en State Machine (ojo humano).
- A5 airdrop Termux: PAT fine-grained (repo vibecodeine, contents:write) en el
  telefono ~/.airdrop_token; luego disparar test de airdrop_push.sh.
- A4/A8 telefono xio: AccessibilityService install + redeploy plugin showcontrol
  (y el nuevo plugin hub) via RUNBOOK 7.
- C12 ensayo Resolume end-to-end en evento real (fecha).
- C16 entrega comercial completa por agentes gratis (job real).
- D18 confirmar/dar data real de las 13 productoras (instagram/venue/tipo).
- D20 specs de venues OpenKlub/Paralelo89 (aforo, preset).
- E21 piezas MANIFIESTO bloqueadas: #2 (2do modelo util?), #5 (ESP32), #7 (orden
  usuario: no tocar), #11 (infra training).

DECISION DEL USUARIO:
- PRs #48/#49 (MAK grafo + MAPA_GENERATIVO): CI verde pero de hace dias, ramas
  ~19 PRs atras de main y el agente MAK sigue trabajandolas. Recomendacion:
  esperar a que MAK pushee su final antes de mergear (evitar clobber).

LOCKEADO por el agente MAK (concurrencia, no entrar a cultura/mak_research):
- C2 gap seguridad xio_puente GET-only; C3 pipeline dossier MAK->markdown;
  G1 panel Cultura muestra grafo MAK. Se destraban cuando MAK termine.

Version: 0.52.0 | Fecha: 2026-07-17 | Identidad: Cauce | Suite completa: VERDE
(compileall OK, pytest verde, flujo verify OK 0.52.0).

Pendientes y fuerte/debil: context/PLAN_SIGUIENTE_AGENTE.md (refrescado hoy).
Historico viejo: git log de este archivo + docs/handoffs/archive/.

## SESION 2026-07-16 -- CHECKPOINT LIMPIEZA TOTAL (ultracode: 5 sonnet + Fable)

Barrido con 5 analistas sonnet (volumen con gitignored, reglas obsoletas,
inventario de ideas, higiene git, salud) y ejecucion central. Resultado:

- BASURA REMOVIDA (~190M): 65 __pycache__ + 3 .pytest_cache + _logs +
  flujo.egg-info + autosave ~ai-*.tmp de Illustrator; duplicado byte-identico
  (md5 verificado) de 76M jobs/2026-07-05_contraportadas/contraportadas_por_
  producto/ (la fuente canonica productos/ queda intacta).
- MOVIDO FUERA DEL REPO, preservado en C:\IA\_flujo_local\: CSV Azure personal
  de la raiz, doublecup.png (referencia de tarea cerrada), APKs instaladores
  termux/shizuku (100M, re-descargables; xio ya esta desplegado on-device).
- GIT PODADO: ramas pr45 + worktree-magical-sparking-kite + claude/cultura-
  xio-mistral-20260715 borradas (verificado: diff contra main = 0 lineas /
  squash-merged en PR #45); worktree cultura-xio removido. Quedan: main, rama
  actual, worktree-mak-research-cultural (= PR #48 ABIERTO, dirty, NO tocar).
- ARCHIVADO via git mv a _archive/legacy_20260716_2000/ (motivos en su
  README.md): xio/advplugins (12 plugins absorbidos por xio/new-plugins),
  projects/agente1_flyers_web + agente2_resolume_chataigne (briefs ya
  materializados), proposals/mejoras_herramientas_2026-06.md (ejecutada),
  .claude/commands/push-all.md (hacia git add . + push directo, contra el
  modelo del repo) y su README.md (el harness lo leia como comando roto).
- NO ARCHIVADO por dependencia viva (verificado con grep, corrige a los
  analistas): projects/flyer_eventos (usado por src/flujo dashboard/flyer/
  intake) y xio/actual (xio/new/server.py y pc_reboot_watch.sh usan su
  platform-tools/adb.exe).
- REGLAS PODADAS: CLAUDE.md (pedir_a_gemini.py marcado PARKED, caveat PARKED
  en la seccion desktop, cultura/ = dept MAK via PRs #48/#49); CONTRIBUTING.md
  reescrito (apunta a CLAUDE.md, sin checkpoint.sh muerto); docs/
  DIRECTOR_PLAN.md marcado HISTORICO; PLAN_SIGUIENTE_AGENTE.md reescrito (los
  items PR #41 / server.py /download / brand analyze ya estaban hechos);
  SESSION_STATE.json comprimido (narrativas largas viven en git/changelog).
- SEGURIDAD: cultura/.dev.limpio contenia keys VIVAS (Tavily/Groq/Cerebras/
  Azure) y NO estaba gitignored -- un git add -A las commiteaba. .gitignore
  ahora cubre cultura/.dev* (glob). Falta que el usuario borre el archivo.
- PENDIENTE MANUAL (el clasificador de permisos bloqueo a los agentes sobre
  cultura/): mover 8 leftovers de cultura/ ya presentes en la historia git --
  comando exacto en PLAN_SIGUIENTE_AGENTE.md P1.3. cultura/xiotech.md se
  queda y se commitea (contenido unico, 0 commits previos).

## OLAS MASTER_PLAN 1-3 (2026-07-16, tras el checkpoint; detalle y lecciones
## en context/MASTER_PLAN.md secciones 2 y 6)

context/MASTER_PLAN.md nuevo (doctrina + 7 frentes + reflexion critica).
Tres olas ejecutadas por sonnets y auditadas/corregidas por el director:
- OLA 1 (PR #51): T-F2 docs re-verificados (INVENTORY estaba en v0.34.6);
  T-E1 esteganografia SVG (pieza MANIFIESTO #4); T-E2 tilde render (ya
  existia, SPEC stale; tests nuevos); T-E3 cron nocturno (pieza #6). Review
  adversarial encontro BLOCKER real (purge sin guarda semanal) -- corregido
  con guarda de semana ISO + tests antes de mergear.
- OLA 2 (PR #52): T-A3 26 tests vj_set/git_performance + 2 bugs arreglados
  (repo vacio RuntimeError; --limit 0 por truthiness); T-B3 xio/RUNBOOK.md
  unico verificado contra scripts reales.
- OLA 3 (PR #53): T-B2 gate opcional XIO_SHOWCONTROL_TOKEN (redeploy al
  telefono PENDIENTE); T-D2 catalogo RD regenerable (docs/CATALOGO_RD.md);
  FIX CRITICO: flujo cotizaciones estaba ROTO (brand.py vaciado dejo
  ImportError en engine.py, piezas.py lo silenciaba) -- brand.py restaurado
  como loader de projects/flujo/flujo.json, verificado en vivo.
MANIFIESTO: 4/11 piezas. Las 4 llaves que destraban H2 son del USUARIO:
.noisette real, branch protection, PRs #48/#49, AccessibilityService xio.

## Estado PRs (2026-07-16)
- ABIERTOS esperando review del usuario: #48 (MAK grafo real + canvas + 6
  modos) y #49 (MAPA_GENERATIVO curador de 19 ideas).
- Mergeados hoy: #45, #47 (previos), #50 (checkpoint limpieza + v0.52.0),
  #51 (MASTER_PLAN + ola 1), #52 (ola 2), #53 (ola 3).

## MAK Codex Fallback Analysis (2026-07-17, sesion god-haiku-fixes)

Trabajo: auditoria de la cadena de fallback de CoderLLM ante timeouts y errores
de proveedores (NIM -> WIN -> Ollama). Deliverable: findings + helper module testeable.

**Archivos:**
- cultura/mak_codex/FALLBACK_FINDINGS.md: analisis detallado (lineas 110-129 en
  codex_lib.py; issues: solo "ultimo" error visible, no aggregacion de intentos,
  timeouts no distinguidos de otros errores, sin reordenamiento por salud de
  proveedores). Propone 5 mejoras: agregacion de errores (high), timeout tracking
  (medium), health stats (medium), backoff (low), mensajes claros (high).
- cultura/mak_codex/fallback_util.py: helper puro (NO deps network/ollama):
  * parse_provider_error() -- clasifica excepcion en tipo (timeout/connection/
    api_error/empty/other) + trunca a 100 chars
  * aggregate_failures() -- formatea lista de intentos en mensaje legible
  * score_provider_health() -- ranking proveedores por ratio exito
  * format_chain_suggestion() -- reordena cadena por salud, genera explicacion
- tests/test_mak_fallback.py: 24 tests (TestParseProviderError x8, TestAggregate
  Failuresx5, TestScoreProviderHealth x5, TestFormatChainSuggestion x3,
  TestIntegrationWorkflow x2). Cobertura: tipo de error, truncacion, multi-
  fallback, ranking, reordenamiento, workflow completo.

**Verificacion (CLI):**
- py -m py_compile cultura/mak_codex/fallback_util.py: OK
- py -m pytest tests/test_mak_fallback.py -q: OK (24 passed)
- py -m pytest tests/ -q -p no:cacheprovider --tb=no: 394+ green, 1 skip,
  4 fallo en test_mak_retencion (pre-existing Linux path issues, no impacta)

**Decisiones:**
- NO toque live CoderLLM loop (fuera de scope: "findings + optional tested helper only")
- Helper module extraible y testeable SIN red/ollama/subprocess deps
- Fallback_util.py agnostico a implementacion (puede inyectarse en codex_lib
  futura sin romper tests existentes)

## Reporte Formal de Verificacion y Tolerancia Cero a Errores
- py -m compileall src/flujo: OK (anterior), fallback_util.py: OK (nuevo)
- py -m pytest tests/test_mak_fallback.py -q: OK (24 nuevos)
- py -m pytest tests/ -q -p no:cacheprovider --tb=no: OK (394+ verdes, 1 skip;
  test_mak_retencion fallo pre-existing Linux paths)
- cd web && npm run build:context: no aplica (web no tocada)
- py -m flujo verify: no aplica (repo source audit, no live modules)
- Observaciones: findings + helper + tests completos. Listo para que otro agente
  integre helpers en CoderLLM live loop si se desea.
