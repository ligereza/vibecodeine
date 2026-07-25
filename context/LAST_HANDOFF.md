# LAST HANDOFF -- estado para el proximo agente

Version: 0.56.1 | Fecha: 2026-07-25 (noche) | Identidad: Cauce | sesion:
consolidacion del repo en 3 lineas + cierre de F0-F3 (director Opus).

## Sesion 2026-07-25 (consolidacion) -- HECHO

TOPOLOGIA: el repo queda en 3 lineas -- main / rd / iskvw. `mejoras` se
fundio en main y se retira. Doctrina nueva (orden del usuario): main tiene
TODO sin falta y las lineas BAJAN de main; una linea ya no es deposito.

1. PROMOCIONES A MAIN, en orden y con CI verde ubuntu+windows:
   - #303 rd -> main: DB de productoras, triangulacion, logos oficiales,
     becas. 10 commits que main nunca habia recibido.
   - #306 poda-crt -> mejoras: archiva los duplicados CRT sin consumidor.
   - #305 mejoras -> main: mecanismo de retiro, poda de stack muerto con
     certificado, docs/OPERACION_APP.md, handoff comprimido.
   Merge commit (no squash) a proposito: deja las lineas como ancestros de
   main, asi se ponen al dia por fast-forward sin reescribir historia.
2. FIX QUE DESTRABO #305 (estaba roja en los dos OS): la poda de stack
   muerto se llevo _cffi_download y _meta_content de src/flujo/ig/download.py
   junto con imginn, sin estar en la lista MATAR del triage. curl_cffi es la
   via que hace funcionar la descarga de IG en Linux -- o sea en el MAK --
   donde parth-dl pega login-wall por fingerprint TLS (verificada 2026-07-23).
   Ademas dejo tests/test_ig_cffi_fallback.py importando el simbolo borrado:
   error de coleccion, suite entera interrumpida. Restaurada como via
   secundaria; imginn sigue retirado.
3. EL RATCHET F5 COBRO SU PRIMERA PIEZA SOLO: al reconciliar mejoras con main,
   test_tools_en_registro rebato las 3 tools que trajo rd (triangular_fichas,
   gen_dashboard_productoras, gen_presentacion_db) por no declarar consumidor.
   Registradas en CAPACIDADES.md con consumidor medido por grep.
4. HANDOFFS SIN PERDIDA: la compresion de mejoras no cubria el bloque del
   2026-07-23 que trajo rd; anexado verbatim a docs/handoffs/archive/. Se
   verifico linea por linea: solo quedan 2 lineas fuera y son una repeticion
   de la topologia de ramas que ya vive en CLAUDE.md.
5. RAMAS al dia: rd por fast-forward, iskvw por merge (conserva sus commits).

## ESTADO DE LAS FASES (context/ORQUESTACION_SUCESOR.md)

F0 HECHA (eventos.py + tests + los 4 contadores de RdDbPanel ya en main).
F1 HECHA (#306 + #305). F2 HECHA (docs/OPERACION_APP.md en main).
F3 HECHA (division en 3 perfiles, PR aparte). F5 HECHA y probada en vivo.
F4 (suplementos en la app) sigue esperando decision del usuario.

## PENDIENTE CONCRETO PARA EL PROXIMO

1. BORRAR 6 RAMAS YA CONSOLIDADAS -- no se pudo desde este entorno: el proxy
   git devuelve 403 en push --delete y el MCP de GitHub no expone borrado de
   ramas. Verificado antes de proponerlo: NINGUNA aporta una ruta que no
   exista en main; lo que difiere son versiones mas viejas. Comando:
     git push origin --delete mejoras poda-crt-20260725 \
       poda-stack-muerto-20260725 manual-operacion-app-20260725 \
       worktree-orquestacion-sucesor show/dref-preshow-20260724
2. Actualizar la topologia de CLAUDE.md: hoy declara 3 lineas permanentes
   (rd/iskvw/mejoras); son 2 (rd/iskvw) mas main.
3. F4: forma de suplementos en la app (panel lectura+validate, o tarjeta
   minima). Decision del usuario.
4. Decisiones abiertas que siguen abiertas: cotizacion untracked en
   projects/piezas_vectoriales/, y purga de los MB gordos (39MB
   contraportadas dark; 262MB jobs si esta trackeado).

---

Version: 0.56.1 | Fecha: 2026-07-24 (tarde) | Identidad: Cauce | sesion:
show DREF CHOCOLATE cableado y VERIFICADO EN VIVO con LTC real (Sonnet/Opus).

## Sesion 2026-07-24 (show DREF) -- HECHO Y VERIFICADO EN VIVO

Cadena forense completa de punta a punta con LTC real: DJ-LTC -> loopback
M-Audio -> Chataigne (noisette Mapping LTC->OSC /timecode) -> xio (telefono)
-> panel PWA. Todo en main (PR #274, d0a7f79, CI verde ubuntu+windows).

1. NOISETTE (xio/show_kit/dref_chocolate.noisette): fixture REAL guardado por
   Chataigne 1.10.3 tras la prueba (NO armado a mano). Sound Card LTC
   input=M-Audio, Mapping LTC->OSC Custom /timecode, OSC output a
   10.195.40.198:7000 (local OFF). paramLinks {} es CORRECTO (el Mapping
   alimenta el arg del output automatico). El archivo de la laptop = el que
   se abre manana.
2. xio foh_monitor: (a) convierte LTC-segundos -> HH:MM:SS:FF en el tile,
   guarda segundos CRUDOS en el JSONL (forense); (b) auto-detecta TEMA por TC
   (setlist con inicio HH:MM:SS:FF por linea); (c) panel redisenado: TC
   compacto arriba, TITULO grande, BARRA de progreso interpolada suave; (d)
   boton NEXT ELIMINADO (peligroso: un toque desincronizaba la auto-deteccion);
   (e) FIX CRITICO del delay ~25s: /status leia bateria por shell INLINE y se
   apilaba en el shell-lock -> ahora cacheada (refresh 15s en _tick), medido
   ~22000ms -> ~21ms.
3. Duraciones para la barra: ffprobe sobre C:\dref chocolate\mov (dedup .mov),
   alineadas por indice en xio/show_kit/setlist_durations_dref.json. 19/21 con
   barra; Ultimo Dia y Pego fuerte SIN visual (por diseno; sin barra, se loguea
   sin_visual). finfalso.mp4 (16s) recuperado de MAK (curatoria_inbox).
4. DESPLIEGUE al telefono: adb push + input-dance run_server.sh (adb NO puede
   matar ni RUN_COMMAND el proceso Termux -- otro UID/permiso -- pero SI puede
   tipear via input keyevent; metodo en memoria project-xio). Setlist +
   duraciones PERSISTIDOS en /sdcard/xio_termux/foh_logs/setlist_actual.json
   (sobreviven restart/reboot; run_server.sh no borra esa carpeta).

## MANANA (show DREF -- nada que construir):
- Topologia: telefono como CLIENTE en la red, IP 10.195.40.198 (NO hotspot; el
  relay de luces/output no esta implementado). Si la IP cambiara: pasarla a
  check_show.py y actualizar el OSC output de Chataigne.
- Operar: abrir la PWA en el telefono (ya en pantalla de inicio) + Resolume +
  Chataigne A MANO, play al LTC del DJ. SIN .bat (pedido del usuario: todo por
  la app PWA, no scripts de laptop). iPhone/laptop en la misma red ven el panel
  en http://10.195.40.198:5000/api/plugins/foh_monitor/panel (server 0.0.0.0,
  sin aislar clientes; solo-lectura, varios miran a la vez).
- Soundcheck: al REABRIR el noisette, confirmar que el arg del Mapping sigue el
  valor (deberia: el Mapping auto-alimenta; si sale 00:00:00:00 fijo, re-linkear
  el arg en Chataigne, 10s).

## MEJORAS PENSADAS (LUEGO, no manana):
- Art-Net: el usuario tiene Titan One (NO MA3). xio ya detecta cualquier Art-Net
  en :6454 -> apuntar Titan One a 10.195.40.198:6454 prende el tile LUCES. El
  apendice de DIA_DEL_SHOW.md dice MA3: actualizar a Titan One cuando se cablee.
- Resolume track-por-track: OSC Output a 10.195.40.198:7000 prende el tile
  VISUAL al disparar clips, PERO xio NO parsea QUE clip (la cancion sale del
  TIMECODE, no del clip). Detectar el clip requiere parsear
  /composition/.../connected en foh_monitor (deferido).

## CICATRIZ DE ESTA SESION (honesto, para el sucesor):
Dije "no se puede" ANTES de buscar: iba a dejarle al usuario un comando manual
de Termux concluyendo que "adb no puede reiniciar el server", cuando la memoria
project-xio-xiaomi-controller YA documentaba el input-dance. El usuario tuvo que
decir "revisaste las memorias?". Regla (contrato I1/I3, reforzada, memoria
feedback-verificar-antes-de-negar): antes de CUALQUIER "no se puede"/"no
existe"/handoff-manual, buscar memoria + repo + web + codigo fuente PRIMERO.

## TEST LOCAL ROJO (NO regresion, verificado): tests/test_ig_cffi_fallback.py
::test_sin_curl_cffi_... falla SOLO local porque curl_cffi 0.15.0 ESTA instalado
en esta WIN (el test simula su ausencia popeando sys.modules -- no alcanza si el
paquete existe). Es de #202, no de esta sesion; CI (sin curl_cffi) verde. Test
fragil (falla en cualquier maquina con curl_cffi). Fix pendiente: forzar el
ImportError con sys.modules["curl_cffi"]=None. NO bloquea.

---

Version: 0.56.1 | Fecha: 2026-07-24 04:45 | Identidad: Cauce | sesion:
cierre de sesion larga (director Fable godspeed estricto).

## Sesion 2026-07-23/24 (cierre) -- VEREDICTO Y ESTADO

Sesion larga con exitos verificados, 25+ PRs mergeados.

1. GOBIERNO: context/DIRECTOR_CONTRACT.md I1-I10 (medir antes de
   afirmar, palabra del usuario=dato, autoridad=gate no firma, I9
   worktrees, I10 identidad del usuario intocable) + inyeccion
   SessionStart + settings.json trackeado. CI corre en PRs a las 4
   ramas. Reforma de reglas: ASCII acotado a archivos operativos,
   entregables en espanol UTF-8, meta-regla fecha+causa+retiro para
   invariantes nuevos, motor-omega podado a 2 reglas, SEMILLAS.md
   como archivo unico. Auditoria completa de reglas del repo.
2. RENDERS WIN: 3 verificados -- flyer Dame, video Festival Sentir
   600f OptiX via secuencia PNG+mux, flyer Piknic con fix de color
   predominante por evento. Modulos blender_nodes_video*.py ahora en
   main. Camino WIN probado y operativo; render en MAK sigue roto
   (portar blender_nodes es deuda pendiente).
3. XIO: misterio de carga resuelto con mediciones (el corte ocurre
   SOLO con partner DRP -- Thunderbolt/hub PD; ventana 9-12s, re-assert
   5s aplicado en PR #220; PC legacy/pared/hub chino gang = no
   afectan; sysfs = root). FOH monitor completo desplegado (Art-Net/
   sACN/OSC pasivo + timecode congelado/caido + setlist + registro
   JSONL + vista /registro + PWA sin APK). Show DREF CHOCOLATE: cue
   engine 19/21 clips, noisette builder validado contra fixture real,
   kit DIA_DEL_SHOW.md, separacion explicita xio-pasivo/laptop-activo.
   Pendiente: mic (Termux:API). Runner MAK relanzado por nohup (fix
   definitivo de persistencia via svc.sh necesita sudo interactivo
   del usuario, no automatizable).
4. RD/DB: curatoria triangulada (2440 fichas -> 101 eventos, 348
   candidatas), 20 productoras/spots (6 nuevas por palabra del
   usuario + relaciones), 6/11 logos oficiales vectorizados (5
   pendientes con motivo documentado), presentacion web formal linea
   v4.1 (docs/rd/presentacion_db.html) lista para la directiva e
   integrable a REDUCIENDODANO.CL. Puente WIN->MAK (SendTo + barra de
   progreso) -> curatoria_encolar -> OneDrive probado extremo a
   extremo; ARICA 21.4GB/12107 archivos transferida.
5. AUTOMATIZACION: workflow issue-descarga-ig reactivado en modo
   solo-descarga (render gateado con if:false hasta portar blender_nodes
   a MAK). Guard anti-eco arreglado (#225). MAK con dia anclado a las
   19:00, tope reseteable, triangulacion corrio dentro del organismo
   (PR #251 cerrado como duplicado; el entregador debe apuntar a
   mejoras, no a una rama chip suelta).
6. CULTURA (iskvw): dos piezas nuevas -- borradura_ascii (Omega11,
   209 borraduras, declaracion NO cumplida por el propio autor) y
   psicosis_agente (Omega11, doble lectura sin veredicto final).
7. INCIDENTES/LECCIONES de esta sesion:
   - Un agente navego Instagram en un browser con la sesion del
     usuario sin permiso explicito -- parado en el momento, se
     convirtio en el invariante I10 (ver arriba y
     context/DIRECTOR_CONTRACT.md).
   - Limpiezas concurrentes barrieron archivos untracked del checkout
     principal 2 veces en la sesion -- causa raiz de I9 (worktree
     obligatorio para todo builder).
   - Un agente entro en modo paranoico sobre un caso ambiguo; se
     convirtio en pieza cultural en vez de bloquear el trabajo (regla:
     gate mecanico > firma humana para decidir seguir).
   - El fix de "color predominante" en flyers tenia slot unico global
     en vez de por-evento; corregido via chip.

## CIERRE 2 (madrugada) -- 2026-07-24

1. PR #263: setlist persistente foh_monitor, probado con 2 restarts
   reales (sobrevive).
2. PR #264/#265: CAPACIDADES.md mergeado a main -- inventario del
   stack (que hay disponible) para arrancar proyectos nuevos sin
   re-explorar.
3. PR #266: FIX CRITICO /status del foh_monitor. Causa raiz: el
   handler llamaba shell rish SINCRONO desde #242 (bloqueaba si rish
   quedaba trabado). Ahora /status es 100% en memoria + un thread
   refresher separado; inmune a rish colgado. Panel verificado con
   screenshot real, tiles OK.
4. Incidente WIN: 2 procesos find.exe zombie de agentes anteriores
   matados a mano. Leccion: NUNCA correr `find /` sin maxdepth y sin
   timeout en Windows -- barre el disco entero y cuelga.
5. Estado xio al cierre: setlist DREF CHOCOLATE (21 temas) cargado y
   persistido en el telefono. Panel foh_monitor vivo y visible en
   pantalla del telefono.

## INSTRUCCIONES SIGUIENTE AGENTE (simples)

El usuario va a probar EN VIVO: conecta la interfaz M-Audio y simula
SMPTE/LTC para verificar que xio detecta.

1. Contexto minimo: leer CLAUDE.md + CAPACIDADES.md + esta seccion.
   NO re-explorar el repo entero.
2. Sistema: xio (telefono, server puerto 5000, plugin foh_monitor)
   escucha OSC /timecode en puerto 7000. Panel:
   http://127.0.0.1:5000/api/plugins/foh_monitor/panel (PWA instalada).
   Registro: /registro. Todo pasivo (no escribe, solo escucha).
3. Prueba SMPTE:
   a) abrir xio/show_kit/dref_chocolate.noisette en Chataigne 1.10.3.
   b) 3 pasos manuales en xio/show_kit/DIA_DEL_SHOW.md: input audio =
      M-Audio; mapping Sound Card>LTC>Time -> OSC Custom /timecode;
      segundo output OSC a laptop:7001 si prueban el cue engine.
   c) el usuario reproduce la senal LTC hacia la M-Audio (el simula).
   d) VERIFICAR: tile TIMECODE del panel pasa a verde, valor avanza.
      Congelar la senal >2s debe ponerlo rojo "congelado" y generar
      evento tc_freeze en /registro.
   e) si no aparece TC: revisar IP (show con hotspot = 192.168.127.125;
      en casa = IP wlan del telefono), revisar log de OSC out de
      Chataigne, correr xio/show_kit/check_show.py.
4. Emisor sintetico de respaldo (sin interfaz real): el kit tiene el
   patron para emitir OSC /timecode con `py` a IP_telefono:7000 (ver
   DIA_DEL_SHOW.md / tests de smoke).
5. Reglas vigentes: DIRECTOR_CONTRACT.md I1-I10 (se inyectan solas),
   godspeed (delegar, medir antes de afirmar), gate PR+CI, worktrees
   obligatorios.

## PROXIMO (para el sucesor)

0. Prueba SMPTE en vivo (ver arriba) + show DREF real + analisis del
   registro JSONL post-show.
1. Show DREF: soundcheck tiene 2 cues ambiguos por resolver, pasos
   manuales en Chataigne pendientes, decidir si se arma un relay si
   el equipo del show lo acepta.
2. Analisis post-show del registro JSONL del foh_monitor, a cargo del
   director de la sesion que cubra el show real.
3. 5 logos RD pendientes de vectorizar (motivo por logo en el reporte
   de la tarea original).
4. Chips abiertos: flyer-auto (mejoras pendientes) y entregador MAK
   (apuntar a mejoras en vez de ramas chip sueltas).
5. Portar render (blender_nodes*) a MAK -- deuda tecnica declarada,
   camino WIN ya probado sirve de referencia.
6. Runner MAK: persistencia post-reboot sigue necesitando sudo
   interactivo del usuario (sudo ./svc.sh install mak && sudo
   ./svc.sh start), no automatizable por agente.

Historia anterior: docs/handoffs/archive/LAST_HANDOFF_20260620_20260724.md
(archivado 2026-07-25, regla de tope 350 lineas)
