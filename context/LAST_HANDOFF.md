# LAST HANDOFF -- estado para el proximo agente

Version: 0.51.0 | Fecha: 2026-07-15 | Identidad: Cauce | Suite completa: VERDE
2026-07-13 (392 passed, 1 skipped). Sesion 2026-07-15: checkpoint SIN re-correr la
suite (pedido del usuario); verificado lo tocado (compileall server.py OK + en vivo
en el telefono 200/403).

El plan largo vive en context/PLAN_SIGUIENTE_AGENTE.md. Este es el estado corto.
Historico viejo en git y docs/handoffs/archive/.

## SESION 2026-07-15 (tarde) -- n8n MAK con APIs gratis

- APIs del usuario probadas con llamadas reales (keys en cultura/.dev,
  gitignored): Tavily OK; Groq OK (llama-3.3-70b-versatile, qwen3-32b,
  gpt-oss-120b); Cerebras OK (gpt-oss-120b, zai-glm-4.7 -- catalogo free
  ROTA, llama3.1-8b ya no existe); Azure Foundry OK con deployment
  gpt-5-mini en https://ligereza.services.ai.azure.com (el "chatgpt mini";
  razonador: sin temperature, max_completion_tokens); Azure classic
  risearch.openai.azure.com auth OK pero 0 deployments = inutilizable.
- Workflow n8n NUEVO cultura/research_agent_free_apis.json (+ doc .md):
  reemplaza research_agent_mistral_nemo.json v1, que NO era importable
  (nodo n8n-nodes-base.llm inexistente + this.helpers dentro de function
  declarations = crash + nodo Prep huerfano). v2: 4 nodos (Webhook,
  Set, Code loop+informe, Respond), cadena LLM fallback
  groq->cerebras->azure->ollama(MAK), dedupe de URLs entre iteraciones,
  meta con llmCalls/errors/fuentes. Keys por $env o body, NUNCA en el JSON.
- VERIFICADO: json.tool OK, node --check OK, harness que simula el sandbox
  n8n corrio el code real: 1 iter, 4 findings, informe coherente, 17s;
  fallback probado rompiendo Groq (4x401 -> Cerebras absorbio todo).
- MAK: ssh mak@192.168.50.2 (key ~/.ssh/flujo_ollama) OK; n8n vivo :5678;
  ollama :11434 solo local (bien). PENDIENTE: setear env vars del
  contenedor n8n (ver doc) + importar el workflow + curl de prueba.

## SESION 2026-07-15 (autonoma) -- xio showcontrol + aislar MAK del xio

- showcontrol (commit 8719929): plugin xio OSC + Art-Net + sACN, SEND-only, pure
  stdlib (socket+struct, sin pip, sin shell -> cero inyeccion). Rutas POST /osc
  /artnet /sacn + GET /status, todo validado (IPv4, puerto, rangos DMX/universo);
  9/9 tests de bytes off-device. DESPLEGADO EN VIVO (input-dance): 26 plugins,
  /status 200, host malo 403, OSC real /composition/tempo [120.0] -> 28 bytes. Uso
  en xio/new-plugins/showcontrol/. SEGURIDAD: el server bindea 0.0.0.0, asi que
  estos endpoints (como todo plugin) los alcanza cualquier cliente del hotspot; ok
  en LAN de crew, si hay publico en el hotspot agregar token antes de confiar.
- AISLAR MAK (caja Linux del LLM local, dell-11m 192.168.198.85) DEL xio: MAK esta
  en el hotspot directo, con el Xiaomi (192.168.198.7) de gateway + DNS; confirmado
  que alcanzaba el xio (HTTP 200). Riesgo real: un modelo/script infectado en MAK
  pegandole a endpoints peligrosos (charge/hotspot/red = el unico internet). FIX
  enforzado EN EL TELEFONO (no en MAK, para que malware-root en MAK no lo levante):
  server.py before_request _deny_blocked_sources -> 403 a los IP de XIO_DENY_IPS
  (env en run_server.sh = 192.168.198.85). DNS/internet de MAK intactos (dnsmasq/
  rmnet son servicios aparte, no el Flask). VERIFICADO: MAK->xio 403 x4; localhost
  ->xio 200; MAK internet 200 + DNS OK. CAVEAT: es por IP; si el subnet del hotspot
  cambia (reboot: 127->69->198) el IP de MAK cambia y la regla queda vieja -> re-
  setear XIO_DENY_IPS. Capas extra opcionales pendientes: regla nft EN MAK (necesita
  el sudo del usuario, no guardado) y/o mover MAK detras del PC Windows por ethernet
  (ICS) para sacarlo del LAN del hotspot (lo mas robusto, mas invasivo).
- README.md: texto (bloque comentado, oculto en la vista de GitHub) actualizado --
  identidad Cauce + area xio (controller on-device + showcontrol) + area Cultura. El
  SVG animado arte-ascii-readme.svg (el vaso) NO se toca; el texto del README si es
  editable (aclaracion del usuario).

## HARDENING POR AUDITORIA (2026-07-13, sesion autonoma) -- commit 4835491

Auditoria ultracode (26 agentes, 6 zonas) -> 19 hallazgos verificados; aplicados
en workflow paralelo (8 unidades de archivos disjuntos) + verificacion central
VERDE. Todo pusheado a claude/vola-cultura-portfolio-20260712.

- RD-SVG (bug real, silent-failure): contraportada_svg.py tenia strings de
  busqueda con tildes/enies/vinetas que NO matcheaban la plantilla ASCII
  01_contraportada_base_10x14cm.svg -> descripcion/beneficios/nutrition salian con
  placeholder CRUDO y el CLI reportaba exito igual. Corregidos los 7 strings +
  guard _replace_required (ValueError si un campo OBLIGATORIO da 0 reemplazos) +
  register_namespace (quita prefijos ns0:) + variantes ASCII en svg_validator.
  PROBADO end-to-end (pieza real: 0 placeholders, ns0 ausente, validator ok).
  IMPORTANTE: la plantilla REAL de produccion NO es la del repo -- es
  Escritorio/ai_illustrator (modelo ops.json/state.json sobre .ai, sitio
  REDUCIENDODANO.CL). El QR es ESTATICO ahi (no cambia por pieza) -> quitada la
  linea muerta que intentaba inyectarlo. Si se quiere sincronizar el generador del
  repo con produccion: leer ai_illustrator, exigir fixture, NO adivinar layout.
- xio (5 fixes de seguridad/robustez; REDEPLOY HECHO Y VERIFICADO 2026-07-13: push
  de los 5 archivos a /sdcard/xio_termux/{new,new-plugins} + run_server.sh via
  input-dance; server reinicio pid 12713->3309, las 5 firmas de fix confirmadas en
  el codigo corriendo, el log muestra joins reales de equipos al hotspot con 200 -no
  mas 500-. adb del PC en xio/actual/platform-tools/adb.exe; el telefono esta por
  USB serial 8299e66f -- wifi-adb 5555 estaba caido, NO el link):
  connectivity_supervisor threading.Lock (arregla race 'dict changed size' ->
  HTTP 500 cuando un equipo entra al hotspot mid-show); server.py
  _request_confirmed allow-list estricta ({confirm:false} ya no pasa la guardia de
  acciones peligrosas); hyperos_unlocker int-coerce + rango 0..6 (arregla injection
  cpu/gpu); network_controller resuelve UID real (block-wifi/data ya no da falso
  ok:true); xiaomi_controller shlex.quote (delete/mkdir/rename/list ya no borran
  el archivo equivocado con espacios).
- cultura: tilde_paridad _es_filoso ahora exige flecha '->' MAS glosa entre
  parentesis (la dieresis, perdida fonetica sin inversion de sentido, ya no cuenta
  como filosa). core: cli.py comando logo-lab duplicado borrado + handoff create
  translitera a ASCII lo que appendea a este archivo.
- ESTADO reconciliado: SESSION_STATE.json estaba desincronizado vs realidad/git
  (fecha, xio UNTRACKED, VOLA sin commitear, PR#41 abierto, repo privado) -- todo
  corregido contra ground-truth de git/gh (xio 142 files tracked, VOLA en 44a728d,
  PR#41 MERGED, repo PUBLIC).
- PORTFOLIO REAL: VERIFICADO ya hecho -- works.json de portfolio-auto tiene 8
  obras curadas reales, 0 placeholders Unsplash, 0 assets faltantes. Clon del repo
  real en C:\IA\portfolio-auto-real. Resto: pulido cosmetico menor (interactivos
  en grilla 2d), bajo valor.
- BLOQUEADO por factores externos (no por falta de trabajo): redeploy xio (telefono
  no alcanzable desde el PC, sin adb en red); cultura nueva (las 4 piezas esperan
  regularizador HUMANO, no mas codigo).

## EN CURSO (2026-07-13, xio auto-heal Shizuku) -- checkpoint

Control: SOLO wifi-adb `adb connect 192.168.127.125:5555` (sin USB). Server
on-device vivo (26 plugins, :5000). Watchdog de Shizuku HECHO Y PROBADO.

1. WATCHDOG Shizuku -- HECHO (2026-07-13). Automatiza la caida que pediste.
   Shizuku era SPOF: al morir, rish falla y el server queda ciego en silencio.
   Solucion sin PC/root: Termux corre su propio adb (`pkg android-tools`), conecta
   por LOOPBACK `adb connect 127.0.0.1:5555` (adb-key autorizada una vez por el
   usuario), y `shizuku_watchdog.sh` (setsid, loop 20s) re-arma shizuku_server con
   `setsid <lib>` cuando cae. Endurecido vs doze: `dumpsys deviceidle whitelist
   +com.termux +moe.shizuku.privileged.api` + `termux-wake-lock`. run_server.sh
   ahora levanta el watchdog + wakelock solo. Scripts en xio/new/:
   shizuku_watchdog.sh, wd_start.sh, setup_watchdog.sh, run_server.sh.
   VALIDADO: kill shizuku_server -> GONE 16s -> revivido en t+20s (log RE-ARMED x2).
   Tip aprendido: comandos a Termux por wifi-adb necesitan `MSYS_NO_PATHCONV=1` +
   wake (kv 224) + `am start` Termux + `input text`/`input keyevent 62` (space).
   El tap de autorizacion adb tambien es scriptable via input tap (esta vez lo
   autorizo el usuario a mano).
   LIMITE: tras REBOOT adbd vuelve a USB (pierde tcpip 5555) -> loopback muere;
   el usuario no reinicia. Cubrir reboot = Termux:Boot + re-enable wireless adb.
2. RECUPERACION MANUAL (si el watchdog no estuviera): `adb connect
   192.168.127.125:5555`; `lib=dirname(pm path moe.shizuku.privileged.api)+
   /lib/arm64/libshizuku.so`; `adb -s ... shell "setsid $lib </dev/null
   >/dev/null 2>&1 &"`.
3. FLUJO ON-DEVICE (fase D) -- HECHO PARCIAL Y VALIDADO (2026-07-13). El CLI core
   corre EN el telefono (Termux/py3.14): `flujo --help` y `flujo version` ejecutan
   completos (banner v0.51.0 + changelog). Script reproducible: xio/new/flujo_ondevice.sh
   (instala deps puras typer/rich/requests/pyyaml, copia flujo_src -> $HOME/flujo,
   corre `PYTHONPATH=$HOME python -m flujo <cmd>`). LIMITE: comandos que tocan
   models.py (pydantic) o intake/json_parser.py (jsonschema) NO andan -- pydantic-core
   y rpds-py necesitan Rust/maturin, sin wheel para Termux/bionic; habilitar =
   `pkg install rust` + build (pesado, no hecho). Desktop (resolume/blender/instaloader)
   N/A en Android. cli.py NO importa models/intake al top, por eso --help/version andan.
4. PERF thermal_monitor -- HECHO (2026-07-13, commit 7e29da9). El poll hacia ~179
   rish calls seriadas (ls + 2 cats x 89 zonas) = ~11s; ahora 1 `for` batch on-device
   devuelve path|type|temp+throttle de todas -> poll 2 calls, /temperatures ~3s warm.
   Verificado on-device (87 zonas, battery 35C). Baja contencion del _shell_lock.
   Patron reusable para otros plugins que hacen cats por-item (ej battery_care).
5. SERVER SUPERVISOR -- HECHO (2026-07-13, commit d234525). Segunda capa de auto-heal
   junto al shizuku_watchdog: si server.py muere nada lo revivia. server_supervisor.sh
   (Termux, setsid, loop 30s) health-check a /api/plugins con el python de Termux; tras
   3 fallos seguidos (~90s, anti-flap) relanza run_server.sh. sup_start.sh idempotente;
   run_server.sh lo arranca junto al watchdog. VALIDADO: pkill server.py -> FAIL 1/3..3/3
   -> relaunch -> http:200; watchdog+supervisor idempotentes (sin duplicar).
   AHORA el on-device se auto-recupera de: Shizuku muerto Y server muerto, sin PC.
   Mismo limite reboot (adbd->USB) para el watchdog. Los keepalive corren bajo uid
   u0_a313 (ps de adb-shell uid2000 NO los ve; confirmar por sus .log o pgrep en Termux).
6. FIX SISTEMICO rish `| cat` -- HECHO (2026-07-13, commit 862f202). El file-redirect
   de _rish rompia TODO comando cmd-based (pm/appops/cmd/wm) con Binder "Failed
   transaction 2147483646" (pasan fd de stdout por Binder; escribir a archivo regular
   falla). Rompia ~10 plugins on-device en silencio. Fix: `(cmd) 2>/dev/null | cat >
   out` (comando -> pipe, cat -> archivo). Sin regresiones (thermal/connectivity/
   screenshot binario OK). Efecto: privacy_auditor/audit paso de roto a 36 apps reales
   (commit c507e9f: + batch appops N->1 + match case-insensitive). Batcheados
   ademas: debloat/scan (139386d, timeout->8.7s), miui_tweaker settings+ads+telemetry
   (8650389), performance_tweaker/status (979b630, timeout->6.4s). Patron: N _shell
   en loop -> 1 shell call que echo "clave|$(cmd)" por item y parsea.
7. AUDIT DE SALUD (2026-07-13) -- 52 endpoints de LECTURA seguros probados on-device:
   42 OK con datos, 7 EMPTY legitimos (history/alerts/logs sin data aun), 0 BINDER
   ERRORS (el |cat destrabo todo: miui/privacy/debloat/usb/wifi/network/hyperos andan).
   3 "ERR/SLOW": 2 falsos positivos (debloat/status pide ?package=; hyperos/device-level
   es POST) + performance_tweaker/status (era N x, ya batcheado). content_explorer NO
   se probo (lee SMS/contactos). Script del audit: probe por whitelist de sufijos
   seguros, clasifica OK/EMPTY/BINDER/SLOW. NO probar endpoints de accion en vivo.
   VERIFICACION DE EMPTY (2026-07-13): 6 de 7 son legitimos (listas in-memory que
   arrancan vacias: exclusions/history/alerts/stats-daily/query-log/guardian-alerts).
   El 7mo, network_controller/uids, era BUG silencioso: `dumpsys package` + regex que
   exigia Package[..] y uid= en la MISMA linea (dumpsys los separa) -> {}. Arreglado
   (commit bab7ddd) con `pm list packages -U` (1 linea `package:x uid:N`) -> 393 pkgs.
8. CHARGE CONTROL sin root -- HECHO Y PROBADO (2026-07-13, commit a26ad79). EL
   DESCUBRIMIENTO GRANDE: `dumpsys usb set-port-roles port0 <sink|source>
   <device|host>` controla el FLUJO REAL de energia como shell-uid via rish, SIN
   root. `sink device`=carga; `source host`=OTG, no carga. Corrige la memoria vieja
   ("charge-cap imposible sin root" -- esa solo probo `dumpsys battery set`, que era
   cosmetico). Plugin nuevo charge_control (25 plugins ahora): cap 80 + floor 77
   (histeresis), hard_floor 20 (NUNCA morir: fuerza carga e ignora todo por debajo),
   charge on/off, powerbank (OTG source), dock (sink+host para hub PD). Seguridad 2
   capas: guard del server (423 sin confirm, endpoints charge/powerbank/dock) +
   rechazo en plugin si nivel<=hard_floor; limiter default OFF. PROBADO end-to-end a
   traves del server: OFF-> dfp/source charging false; ON-> ufp/sink charging true
   (ventana ~10s, telefono quedo cargando 61%). Meta-leccion (ver
   xio/PLAN_SERVICIOS_SIN_ROOT.md): "imposible sin root" casi siempre = ruta /sys
   cerrada por SELinux, pero la MISMA capability suele estar en un SERVICIO
   privilegiado (dumpsys/cmd/service call) alcanzable via Shizuku. Atacar por el
   servicio, no por el sysfs.
9. PERSISTENCIA TRAS REBOOT -- PARCIAL (2026-07-13). Termux:Boot INSTALADO (el base
   Termux v0.118.0 es de F-DROID -> instalar el Termux:Boot de F-Droid, versionCode
   1000; el de GitHub v0.8.1 falla INSTALL_FAILED_SHARED_USER_INCOMPATIBLE por firma
   distinta). Instalado por `adb install` (= shell uid, sin root); abierto 1 vez con
   monkey para registrar el receiver. Boot launcher en ~/.termux/boot/00-xio-boot.sh
   (ext4, exec) que llama xio/new/reboot_recover.sh (en /sdcard, iterable por push):
   trata loopback 5555 -> wireless-debug por mDNS, normaliza a tcpip 5555, re-arma
   Shizuku, corre run_server.sh. MURO NO-ROOT (probado, no adivinado): el adb de
   Termux solo alcanza adbd por TCP; al boot adbd = USB-only, no hay listener TCP
   salvo wireless-debug; `settings put global adb_wifi_enabled 1` por shell NO pega
   (readback 0, Android lo protege); tcpip no persiste; persist.adb.tcp.port bloqueado
   por SELinux. ADEMAS no hay enlace USB de DATOS al PC: Windows solo ve el telefono
   por Bluetooth (audio), el Thunderbolt es charge-only -> NO hay adb-USB de respaldo.
   CONCLUSION: la auto-recuperacion de reboot no-root NO es posible en este setup sin
   accion del usuario. El boot script auto-recupera EN CUANTO exista un transporte adb
   (usuario enciende "Depuracion inalambrica" a mano + pairing, o un cable USB de datos
   real a un PC). NO se hizo reboot de prueba: reiniciar ahora perderia el 5555 sin
   forma de restaurarlo (no hay USB de datos) -> se difiere a cuando haya red de
   respaldo. Scripts: xio/new/{reboot_recover.sh, 00-xio-boot.sh, setup_boot.sh}.
10. RECUPERACION DE REBOOT AUTONOMA -- ARMADA Y CORRIENDO (2026-07-13, commit bff8a8f).
    Correccion clave a (9): el puerto USB-A del PC SI enumera adb (serial 8299e66f); el
    Thunderbolt era charge-only para DATOS (por eso Windows solo veia Bluetooth). Con
    USB-A hay canal de recuperacion que sobrevive el reboot. Muros confirmados:
    wireless-debug exige wifi-CLIENTE (router) -> descartado por diseno (el tel ES el
    internet, sin router); RUN_COMMAND intent bloqueado (com.android.shell no puede
    recibir com.termux.permission.RUN_COMMAND); persist.adb.tcp.port SELinux. CLAVE 5G:
    el rmnet del Xiaomi es independiente del hotspot, asi el TELEFONO avisa por 5G aunque
    el hotspot este caido -- el watcher del PC corre `curl ntfy.sh` EN el telefono por
    USB. pc_reboot_watch.sh (PC git-bash, CORRIENDO ahora pid+; autostart opcional
    xio-reboot-watch.vbs que instala el usuario en shell:startup): vigila el device USB;
    en boot-fresco/server-down re-arma Shizuku + tcpip 5555 + arranca server (input-dance,
    Termux:Boot headless de respaldo) + reporta hotspot + push ntfy por 5G. allow-external
    -apps activado en Termux (setup_runcommand.sh). Topico solo en el device
    (/sdcard/xio_termux/ntfy_topic.txt), NUNCA en git; el usuario se suscribe en la app
    ntfy del iPhone. ntfy+5G+USB probados OK. Idea Claude-on-device por API: descartada
    (no rompe el muro Shizuku-al-boot y quema runway; el repo va a agentes gratis).
    REBOOT REAL PROBADO (2026-07-13): uptime reseteo 90740->14s. El server se recupero
    100% AUTONOMO -- watcher re-armo Shizuku + tcpip por USB, Termux:Boot DISPARO (el
    Autostart que activo el usuario funciono) y uso el 5555 del watcher para lanzar
    server+watchdog+supervisor; server UP en ~90s. UN fallo: el hotspot NO auto-reencendio
    (HyperOS no lo restaura al boot; ningun comando no-root reactiva el tether del usuario
    -- `cmd wifi start-softap` dice explicito que NO tethera). Y el ntfy "toca el toggle"
    NO puede llegar: el iPhone del usuario necesita el hotspot para recibirlo (circular).
    FIX (commit 93a270d): recover() reenciende el hotspot PRIMERO por PANTALLA (el tel no
    tiene PIN) -- `am start -a android.settings.TETHER_SETTINGS` + `uiautomator dump` para
    leer el checkbox "Portable hotspot" (primer android:id/checkbox) + `input tap 540 583`
    si esta en false. VALIDADO aislado (off -> auto-reencendido -> up). Tambien lockfile
    .pc_watch.pid (habia 7 watchers duplicados). AHORA el reboot recupera TODO sin tocar
    nada: Shizuku + tcpip + hotspot + server. 2DO REBOOT PROBADO OK (2026-07-13, hands-off
    total, usuario NO intervino): recovery en ~45s -- Shizuku 14:48:46, tcpip 14:48:53,
    hotspot auto-reenable (toggle false->tap->true) 14:49:04-22, server UP t=45s; el
    internet del usuario volvio SOLO. Endurecido antes del test: wake+`wm dismiss-keyguard`
    +swipe antes de cada input (post-boot hay lock de deslizar sin PIN), y monitor
    continuo del hotspot en el loop (reintenta si un reenable temprano fallo). Pulido
    (commit 7b817eb): tras el tap, espera la IP de wlan1 (~24s) antes de reintentar
    (evita re-abrir Settings 2 veces). Nota: watcher + Termux:Boot AMBOS corren
    run_server.sh -> `pkill` puede causar un DOWN transitorio de segundos al boot, pero
    el server_supervisor lo revive; verificado UP y estable (0 procs duplicados).
    Watcher corriendo (1 instancia, lockfile). Scripts: xio/new/{pc_reboot_watch.sh,
    setup_runcommand.sh, xio-reboot-watch.vbs, reboot_recover.sh}. ntfy topico solo en
    device; el ntfy solo sirve si el hotspot ya volvio -> por eso el reenable automatico
    (no la notificacion) es el fix real. Persistencia del watcher: xio-reboot-watch.vbs
    en shell:startup (lo instala el usuario; auto-mode bloquea la accion de autorun).

## SIN-WINDOWS del hotspot + runbook de show (2026-07-13, sesion autonoma)

Objetivo de esta tanda: quitar la dependencia del PC para el hotspot (Capa 1 del show)
y dejar el escenario "Xiaomi solo en escenario, usuario en el FOH" operable. Usuario dio
autonomia total y se alejo del PC; hitos avisados al iPhone por ntfy (5G del propio tel).

- Verificado por dumpsys wifi: el Xiaomi SIRVE de router al equipo entero, no solo al PC.
  MaximumSupportedClientNumber=32; SIN aislamiento de clientes en la config softap (los
  equipos se ven entre si -> malla, phone->PC directo OSC/Art-Net funciona);
  AutoShutdownEnabled=false (el hotspot NO se cae por inactividad). Falta prueba empirica
  de aislamiento (2 phones ping) que solo se hace en el venue.
- NUEVO self-heal on-device del hotspot SIN PC: xio/new/hotspot_watch.sh + hs_start.sh
  (launcher idempotente, calcado de shizuku_watchdog/wd_start). Loop 30s via loopback
  adb (uid shell); si wlan1 pierde IPv4 por 2 ciclos y Shizuku+tcpip estan vivos, corre
  el input-dance (TETHER_SETTINGS + uiautomator + input tap 540 583) para reencender.
  DOBLE compuerta de seguridad: solo entra si wlan1 sin inet Y el checkbox esta 'false'
  -> nunca apaga un hotspot sano. Guard de transporte: si no hay loopback (post-reboot)
  hace skip, no adivina "down". Cableado en run_server.sh (arranca en cada boot).
  DESPLEGADO y ACTIVO ahora: hotspot_watch pid 15585, liveness confirmada (hs_start
  re-run dice "already running"). Cubre el caso "hotspot cae con el telefono ENCENDIDO"
  sin Windows (estado que persiste durante un show si NO hay reboot).
- reboot_recover.sh ENDURECIDO: en el caso reboot-sin-host (donde abortaba en silencio)
  ahora manda ntfy ACCIONABLE al iPhone con el estado real del hotspot ("Reboot SIN host:
  ... Hotspot: DOWN. Si DOWN, toca el hotspot"). Y el ping final reporta hs_state real
  tras dar ~40s al self-heal. Helper hs_state() lee wlan1 directo (uid Termux).
- RUNBOOK del show: xio/HOTSPOT_SHOW_RUNBOOK.md -- arquitectura 3 capas, pre-show con PC,
  que se auto-cura y que no, energia como defensa primaria contra el reboot, y el unico
  hueco con sus 2 caminos.
- HUECO HONESTO (parte del usuario): reboot fisico SIN host no se auto-cura no-root; el
  hotspot necesita un AccessibilityService on-device (unico mecanismo que sobrevive reboot,
  arranca solo, toca pantalla, sin Shizuku). NO pude compilarlo autonomo: este PC no tiene
  toolchain Android (sin Java/SDK) -- limite de capacidad, no etico. Y NO bajo un MacroDroid
  PRO pirata (linea legal/etica). Caminos dejados en el runbook: A) macro MacroDroid FREE
  (boot -> tap toggle); B) AccessibilityService propio (buildable por dev/agente libre,
  se activa headless con `settings put secure enabled_accessibility_services` -- shell lo
  tiene, persiste reboot). Defensa primaria que vuelve el hueco irrelevante: power bank /
  fuente PD en escenario = sin reboot = sin problema.
- Notificacion: para que el iPhone reciba el ntfy con el hotspot caido, el iPhone necesita
  internet propio (datos celulares), no el hotspot del Xiaomi.

## ESTADO FINAL xio (2026-07-13) -- trabajo mayor COMPLETO

El controlador on-device quedo maduro y auto-sostenible sin PC:
- Self-healing 2 capas: shizuku_watchdog (revive Shizuku) + server_supervisor (revive
  Flask), ambos setsid+doze-whitelist+wakelock, arrancados por run_server.sh, probados.
- Fix sistemico rish `| cat`: destrabo TODOS los comandos cmd-based (pm/appops/settings/
  cmd/wm) que fallaban con Binder error en el backend rish.
- Hot-paths N x _shell batcheados: thermal, privacy_auditor, debloat, miui_tweaker,
  performance_tweaker (timeouts -> segundos).
- Audit de salud: 43 endpoints de lectura OK con datos, 6 EMPTY legitimos, 0 bugs.
- flujo CLI core corre on-device (--help/version); pydantic/jsonschema bloqueados (Rust).
- CHARGE CONTROL sin root (objetivo original de xio): charge-limiter 80% + charge
  on/off + powerbank + dock, via set-port-roles. Probado. Plan de "imposibles" en
  xio/PLAN_SERVICIOS_SIN_ROOT.md (atacar por servicios, no por /sys).
Limite unico pendiente: REBOOT del telefono (adbd vuelve a USB, pierde tcpip 5555 ->
el loopback del watchdog muere). El usuario no reinicia; cubrirlo = Termux:Boot +
re-enable wireless adb. Todo pusheado a claude/vola-cultura-portfolio-20260712.

## Hecho (esta sesion, 2026-07-12 -- VOLA + portfolio)

PORTFOLIO-AUTO (repo aparte ligereza/portfolio-auto, LIVE, ya pusheado a su main
30be342 -- NO es el repo flujo):
- VOLA publicada: pieza nueva "lo visible y lo invisible" (vaso + vacio bajo la
  triada). Assets vola-vaso.svg + vola-void.svg en assets/works/, entrada en
  data/works.json. (VOLA lleva tilde aguda a proposito; el archivo va ASCII.)
- FIX del vaso: vola-vaso.svg estaba casi en blanco (opacidades 0.03-0.10, "umbral
  de percepcion"). Reconstruido con el campo de glifos legible de
  arte-ascii-readme.svg (original SOLO leido, no tocado) + animacion de "digestion"
  en overlay con mix-blend-mode:screen (solo aclara, no puede borrar). Legible ya,
  verificado por render headless-Edge contra doublecup.png. Commit 2b35a5b.
- 2 VISUALIZADORES INTERACTIVOS restaurados (auto-hosteados desde artifacts, ya no
  como artifact republicado -- esto CIERRA el viejo pendiente "republicar af6411d3"):
  - sala-3d.html  <- artifact af6411d3 (Three.js WebGL + CSS3D, galeria 3D real).
  - tapiz.html    <- artifact e414adac (TAPIZ system projection / psicosis-fungi).
  Tecnica: WebFetch de la URL del artifact GUARDA EL HTML CRUDO COMPLETO EN DISCO
  (header "full HTML saved to ...tool-results\\artifact-<id>-*.html"); se le quita
  el bloque <!-- frame-runtime --> ... <!-- /frame-runtime --> (wrapper iframe de
  claude.ai) con script, y queda pagina self-contained. js/app.js: el caso unico
  3d-immersion se generalizo a un mapa INTERACTIVE_PAGES (sala-3d, tapiz). Commit
  30be342. (Ver memoria reference_selfhost_artifact.md.)

FLUJO (este repo, TODO SIN COMMITEAR en main @1dd8342 -- el usuario dijo "olvida
github" para flujo; queda en disco, decidir despues si se versiona):
- Deuda tecnica P2: quitado stub mentiroso /api/materials/<id>/download en
  src/flujo/serve/server.py y linea de ayuda stale "brand analyze" en cli.py.
- projects/cultura/ 4 piezas-triada motor-omega (una por semilla viva), con .md
  (Omega11 escrita) y test cada una, suite verde al construir:
  fila_cero.py (+7 tests), tilde_paridad.py (+5), mecanismo_residuo.py (+6),
  marca_sin_precio.py (+8). Mapa: SUPER_PLAN_TRIADA.md. PENDIENTE humano: cada
  Omega11 espera su regularizador real (lector no-autor + plazo) para EXPONERSE y
  registrarse fechada; NADA entra a puente/SEMILLAS.md hasta eso (no se toco).
- projects/tapiz/ piezas VOLA: vaso_animado.svg/.py (+VASO_ANIMADO.md),
  vibecode/void_shapes.py + void modes en spaces.py/svg_export.py (aditivo, +11
  tests en test_tapiz_vibecode.py), void_animado.svg, VOLA.md (concepto),
  TILDE_DEL_HIGH.md (analisis cultural: el signo de la sustancia cruza, el estado
  "high" no; el LLM es Mary que nunca sale del cuarto). No reemplaza nada original.
- doublecup.png en la raiz: screenshot de referencia del README real (vaso legible).
  Untracked; borrable, no versionar si estorba.

## XIO -- Xiaomi controller on-device (track aparte, xio/ UNTRACKED, no commiteado)

Objetivo: correr el server Flask xio/new EN el telefono (Termux + Shizuku/rish), no
en la PC. FASE 1 y FASE 2 COMPLETAS 2026-07-12.

- FASE 1 DONE: server on-device (XIO_BACKEND=rish), 23 plugins; PC-apagada y
  pantalla-apagada NO lo matan (termux-wake-lock puesto); solo un REBOOT del telefono
  (Shizuku no-root no auto-arranca, se re-arma por USB). Flask instalado tras
  `pkg upgrade -y` (arreglo RAIZ del ssl/libexpat faltante -- py3.14 sobre base vieja).
  Alcanzable en http://192.168.127.125:5000 (hotspot wlan1; internet = rmnet datos) y
  por USB via `adb forward tcp:5055 tcp:5000`. Launcher: xio/new/run_server.sh (pkillea
  el viejo, copia fresco de /sdcard/xio_termux, relanza).
- FIX CRITICO xiaomi_controller.py `_rish`: rish TRUNCA salidas grandes (ip addr,
  dumpsys, screenshots) de forma intermitente aun en llamadas secuenciales (pipe
  app_process->Shizuku sin drenar). Ahora `_rish` redirige la salida a un archivo en
  /sdcard y lo lee del filesystem LOCAL (Termux lee /sdcard), evitando el pipe;
  serializado con lock (Flask es threaded). 6/6 consistente tras el fix. Afecta a
  TODO el backend rish, no solo un plugin.
- FASE 2 DONE: plugin xio/new-plugins/connectivity_supervisor (active-router),
  verificado en vivo con screenshots del navegador on-device. Poll read-only ~20s de
  clientes del hotspot via ip neigh SOLO (cmd wifi list-tethered-clients da
  SecurityException para uid 2000; leases dnsmasq walled -> sin hostnames non-root,
  MAC es el unico ID). Registro por MAC con eventos join/drop/rejoin persistidos.
  Inteligencia MAC: marca bit locally-administered (0x02) como "random" (privacy iOS/
  Android) vs "hardware", auto-nombra privacy-XXXX / device-XXXX. Alertas de
  infraestructura: eventos+notificacion cuando hotspot o internet cambian de estado
  (hotspot_down/up, internet_down/up; el primer poll solo fija baseline). BT
  informativo y on-demand (default bt_watch=False, desacoplado del poll para que la
  deteccion de caidas sea rapida). DASHBOARD en vivo GET /ui (consola movil
  self-contained, chips + dispositivos presentes + feed de eventos, refresh 3s):
  http://192.168.127.125:5000/api/plugins/connectivity_supervisor/ui. Rutas GET
  /ui /status /clients /watch /events /bt, POST /label /config, POST
  /reassert-hotspot (GUARDED, 423 sin confirm). No quarantined (poll read-only).
  ARQUITECTURA: /status NO toca rish (servia ip addr inline -> con el poll de 3s del
  dashboard se apilaban las llamadas en el _shell_lock, latencia 23s); ahora el poll
  cachea hotspot/internet en self._infra y /status sirve estado en memoria -> 0.01s.
  Regla: endpoint en timer sirve cache, solo el poll de fondo toca rish. Screenshots
  CONFIRMADOS reparados por el fix _rish: /api/screen devuelve PNG 1080x2400 completo.
  NUANCE iOS: la MAC random es ESTABLE por-sesion -> sirve para un show sin tocar
  ajustes Apple (solo rota en el ciclo diario/OS).
- FASE 2b (hardening, mismo dia): salud de bateria en el poll+dashboard (dumpsys
  battery -> level/temp/status, tira "Battery 98% 33C charging", alertas overheat
  >=45C y low <=20%); short-link /router -> /ui; registro PERSISTE (escribe a
  /sdcard/xio_termux/connsup, fuera del arbol que run_server.sh borra). Wireless ADB
  habilitado (adb tcpip 5555 + adb connect 192.168.127.125:5555; cable opcional).
  LECCION CRITICA: `adb tcpip` reinicia adbd y MATA el shizuku_server si se lanzo
  como `adb shell <lib>` (hijo de adbd) -> rish devuelve "Server is not running",
  server ciego. Arranca DETACHED: `adb shell "setsid <lib> </dev/null >/dev/null 2>&1 &"`
  (PPID 1, sobrevive reinicios de adbd). lib = pm path moe.shizuku.privileged.api +
  /lib/arm64/libshizuku.so. Todo el sistema de eventos (drop/join/infra) VALIDADO en
  vivo (la caida de Shizuku disparo drops reales + la recuperacion los joins e infra).
  Commit dc1f087 (base xio) + commit de bateria. xio/ ya versionado (.gitignore
  excluye platform-tools + APKs).
- FASE 2c (seguridad, mismo dia): integrado Plugin Guardian (carpeta que dejo el
  usuario en xio/seguridad/) como plugin 24 en xio/new-plugins/plugin_guardian/:
  auditoria de comandos, blocklist de comandos peligrosos, enforcement de permisos
  por plugin (manifest), review-mode, audit-log JSONL persistente. plugins/base.py
  reemplazado por version superset (PluginContext gana safe_shell()/set_security_hook
  /set_audit_logger/check_permission; aditivo, los plugins existentes usan _shell
  legacy y NO se ven afectados). Verificado on-device: 24 plugins cargan, "Security
  active", /api/plugins/plugin_guardian/status OK, sin regresiones.
- PUSHEADO a origin (rama claude/vola-cultura-portfolio-20260712): commits dc1f087,
  5b93571, daa5992. Se puede seguir desde nube/iPhone contra esa rama.
- Estado al cerrar: server on-device corriendo (24 plugins), hotspot INTACTO
  (nunca tocado), Shizuku detached vivo, wireless-adb activo. Pantalla bloqueada.
- HALLAZGO iOS: Apple usa MACs aleatorias por-red (bit locally-administered) ->
  iPhone/iPad reaparecen como unknown-XXXX al reconectar. Para tracking estable,
  desactivar "Direccion Wi-Fi privada" de ESTE hotspot en cada dispositivo Apple. No
  se puede FORZAR reconexion WiFi/BT de Apple: el supervisor DETECTA y AVISA, no
  puppetea (muro iOS).
- Verificacion: compileall xio/new + xio/new-plugins OK; endpoints probados en vivo
  sobre USB. PENDIENTE: Termux:Boot autostart (APK no instalada; Shizuku igual
  necesita re-arme manual tras reboot); label-by-hostname para sobrevivir rotacion de
  MAC; commitear xio/ requiere .gitignore para platform-tools/adb.exe (binario
  pesado). Memoria: project_xio_xiaomi_controller.md.

## Doing / Next

- RESUELTO (portfolio "no puedo abrirlos" = salia una IMAGEN donde deberia estar
  el artefacto). ERA bug de codigo, NO cache (me equivoque antes diciendo cache).
  Causa real: los works interactivos (sala-3d, tapiz) llevan cover PNG + mediaType
  image, y varias rutas de render mostraban ESA imagen en vez de abrir la pagina
  viva: openLB (lightbox del home-else y del 2d masonry) y obra.js (obra.html?id=X,
  pagina de detalle) renderizaban <img> cover. Solo buildCard del home enrutaba
  bien. Fix (commit e4e43a5, pusheado): guard en openLB (si w.template esta en
  INTERACTIVE_PAGES -> location.href a la pagina) + INTERACTIVE_PAGES + redirect en
  obra.js. Ahora TODA ruta abre sala-3d.html / tapiz.html. NO pude click-test en
  navegador real (Chrome no instala sin admin, Playwright abortado); verifique
  rutas de codigo (deterministas) + paginas 200 + render headless. Limpieza menor
  pendiente: sala-3d/tapiz tienen mediaType "image" y se cuelan en la grilla 2d
  (el click igual abre la pagina por el guard; ideal quitar mediaType o filtrarlos).
- CUP: vola-vaso.svg estaba ESTIRADO (comprimido horizontal) ademas de casi-blanco.
  Reconstruido en scratchpad/build_vola_vaso.py DESDE la geometria real de
  arte-ascii-readme.svg (bloque unico <text white-space:pre 10px/12px, .b fondo /
  .g vidrio / .l liquido; la MISMA que produce doublecup.png), size explicito
  676x904, link <a> del repo desenvuelto, "digestion" como filter:brightness (no
  mueve glifos, no puede re-distorsionar). Proporcional y legible, verificado por
  render headless-Edge claro y oscuro. Original arte-ascii-readme.svg NO tocado.
  En commit e4e43a5.
- NO click-testeado en vivo: la sala 3D interior post-ENTRAR (WebGL, headless sin
  GPU). El agente reporto canvas three.js r149 init sin errores. Si post-ENTRAR
  sale negro, debuggear ahi.
- Decidir si el trabajo flujo sin commitear (arriba) se versiona o queda local.
- Carryover previo: PR #41 (tilde_residuo.py) -- confirmar si sigue abierto y
  decidir merge. branch protection en main + secret ANTHROPIC_API_KEY siguen sin
  configurar (ver SESSION_STATE.next).

## Blockers
- (+)2 (OBRA_02) bloqueada esperando lector humano.
- Cada Omega11 de projects/cultura/ espera regularizador humano (lector no-autor +
  plazo) antes de exponerse/registrarse.
- build_chataigne_noisette_experimental: falta .noisette real (NO re-adivinar).
- #2 duelo de modelos: Gemini PARKED, falta un 2do modelo util.

## Reglas vivas (no negociar)
- NO activar Claude via API en Actions (decision usuario 2026-07-12).
- El airdrop QUEDA COMO ESTA. puente/ es teorico (puente/README.md): no ejecutar,
  no limpiar, no reinterpretar lo fechado. NO tocar puente/SEMILLAS.md.
- README.md del repo y arte-ascii-readme.svg: obra terminada, no agregar/reemplazar.
- context/AVANCES_BLOCK.txt NO es doc muerto (input de tools/tapiz_telemetry.py).
- Cultura: descriptivo, nada generativo-de-sintesis; psicosis jamas perfila
  personas reales; precursor solo cultura/ley/estetica; NADA operativo de sustancias
  (dosis/sintesis/adquisicion).
- Ordenes destructivas de git van al hilo principal, no a subagentes.
- Nunca versionar secretos (.env, config.json, *.key). CLAUDE.md y este archivo:
  ASCII-only. portfolio-auto es PROJECT subpath: rutas RELATIVAS siempre (nunca
  /assets), o dan 404.

## Verificacion (antes de cerrar, si tocas flujo Python)
- py -m compileall src/flujo
- py -m pytest tests/ -q
- py -m flujo verify
- (si tocas web) cd web && npm run typecheck && npm run build:context

## Entrada
1. Este archivo. 2. context/PLAN_SIGUIENTE_AGENTE.md. 3. CLAUDE.md.
