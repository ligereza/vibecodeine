# LAST HANDOFF -- estado para el proximo agente

Version: 0.51.0 | Fecha: 2026-07-13 | Identidad: Cauce | Suite: verde (cuando se
construyo; NO re-corrida al cerrar) | flujo verify: no re-corrido esta sesion

El plan largo vive en context/PLAN_SIGUIENTE_AGENTE.md. Este es el estado corto.
Historico viejo en git y docs/handoffs/archive/.

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
