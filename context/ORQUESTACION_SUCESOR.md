# ORQUESTACION SUCESOR -- mision, triage y fases

Fecha: 2026-07-25. Autor: director Fable. Causa: agentes gastan sesiones
arreglando herramientas muertas y dejando frentes a medias; el usuario pidio
plan de orquestacion con veredicto rescatar/matar. Retiro de este doc: cuando
F0-F5 esten mergeadas y el registro VIVO/MUERTO exista en CAPACIDADES.md ->
archivar a _archive/.

Entrada obligatoria del proximo agente director, junto a CLAUDE.md y
context/LAST_HANDOFF.md. NO re-explorar el repo entero.

## 0. Rol y regulacion de gasto

- El rol ya esta codificado: skill `godspeed` + context/DIRECTOR_CONTRACT.md
  I1-I10 (se inyectan solos). NO crear otra skill de rol: seria duplicado.
- Gasto: el director (Opus/Fable) DECIDE, ESPECIFICA y VERIFICA. Sonnet edita
  con spec cerrada. Haiku lee volumen. Regla dura: TODO reporte de modelo
  barato es un claim, no un hecho -- spot-checkear con grep/git los que cargan
  peso. Caso medido 2026-07-25: de 3 claims de un inventario Haiku, 2 refutadas
  ("_archive vivo con 45 refs" eran menciones en docs, 0 imports; "SSE
  referenciado en UI" era falso, 0 refs en web/src).
- Prohibiciones vigentes (palabra del usuario, context/failed-handoff.md):
  1. Estructura, no tareas: se construye la maquina, el usuario la dispara.
  2. Nada a medias: no se abre un frente sin cerrar el anterior.
  3. Suciedad bajo la alfombra: se anota, no se limpia sobre la marcha.
  4. Cero efectos secundarios: ninguna prueba modifica datos del usuario.
  5. Medir antes de afirmar (I1).
  6. Subagentes construyen SOLO con spec cerrada; nunca "construi esta
     feature" fire-and-forget (ya fallo 2 veces).
  7. Nada de Instagram con identidad/sesion del usuario (I10).

## 1. Fases en orden (una fase = un PR con CI verde antes de la siguiente)

Nota (2026-07-25): F1 y F5 ya ejecutadas por el director; quedan F0
(contadores), F2 (manual), F3/F4 (decision usuario).

### F0 -- Cerrar el rescate (rama show/dref-preshow-20260724, PR contra rd)
Estado: el rescate del working tree YA se commiteo y pusheo (commit 69118fb:
src/flujo/rd/eventos.py + tests/test_rd_eventos.py + hub.py + failed-handoff.md,
18 tests verdes). FALTA:
- 4 contadores en web/src/components/RdDbPanel.tsx: grid de stats en lineas
  ~147-159 (array literal de 4 tarjetas, agregar 4 mas: Eventos, Triangulables,
  Sin lineup, Sin fecha ISO); extender el tipo `resumen` en linea ~44 con
  eventos, eventos_triangulables, eventos_sin_lineup, eventos_sin_fecha_iso.
  El backend YA los emite (hub.py _get_rd_db, resumen).
- Verificar: cd web && npm run typecheck && npm run build:context.
- Abrir PR de show/dref-preshow-20260724 contra rd. CI = veredicto.

### F1 -- Poda con certificado de defuncion (PRs chicos contra mejoras)
Ejecutar el triage de la seccion 2. Cada item archivado lleva certificado:
fecha, causa MEDIDA (grep/git log adjunto), condicion de resurreccion.
Archivar = git mv a _archive/legacy_YYYYMMDD_HHMM/ (preserva historial).
Nunca borrar a ciegas; nunca "arreglar" un item de la lista MATAR.

### F2 -- Manual de independencia: docs/OPERACION_APP.md
Como correr la app (py -m flujo app; fallback context/flujo_hub.html), como
agregar un panel/endpoint/icono (iconos: src/flujo/plano/iconos.py, un
_glyph_<nombre> + registro de colores/labels). Perfiles YA documentados en
docs/HUB_PERFILES.md: referenciar, no duplicar. Trampas pagadas que van si o
si: rider sin contactos (decision de la jefa de eventos RD); el hub NO procesa
jobs al arrancar (opt-in --procesar-pendientes); la IP del venue cambia por
DHCP; el server del telefono no arranca solo tras reboot; los logos no se
recortan de flyers.

### F3 -- Division RD/ISKVW sobre perfiles
web/src/data/profiles.ts: existen rd/studio/cultura/rd-plano; NO existe iskvw.
DECISION ABIERTA del usuario (seccion 3) antes de construir.

### F4 -- Suplementos en la app
Hoy solo CLI (flujo suplementos list/contraportada/validate) + modulo
src/flujo/comercial/suplementos_config.py. Forma pendiente del usuario
(seccion 3). Es RD vivo: prioridad sobre F3 si el usuario no responde.

### F5 -- Mecanismo anti-reincidencia (la fase que evita repetir todo esto)
HECHO 2026-07-25: tests/test_higiene_repo.py (tope handoff + registro
tools) + seccion 5 de CAPACIDADES.md; al sucesor solo le queda respetar
el ratchet.

## 2. Triage (veredicto del director, evidencia medida 2026-07-25)

### MATAR / ARCHIVAR
- desktop/ (app Tkinter Gemini->Claude): 8 archivos, 0 imports externos,
  Gemini PARKED 2026-07-10. EXCEPCION: desktop/tilde_meter.py es standalone
  vivo (area Cultura de CLAUDE.md) -> mover a tools/ ANTES de archivar el
  resto. Resurreccion: Gemini vuelve con API util.
  [EJECUTADO 2026-07-25 en PRs de esta sesion]
- Skills .claude/skills/relevo-web/ y orquestacion-gemini-claude/: dependen de
  Gemini parked; CLAUDE.md ya las marca sin uso. Misma condicion.
  [EJECUTADO 2026-07-25 en PRs de esta sesion]
- Fallback imginn en src/flujo/ig/download.py (_mirror_image_urls): 403
  Cloudflare permanente desde 2026-07-22. Podar; queda parth-dl + error claro.
  De paso arreglar tests/test_ig_cffi_fallback.py (fragil: forzar ImportError
  con sys.modules["curl_cffi"] = None; hoy falla en cualquier maquina con
  curl_cffi instalado). [EJECUTADO 2026-07-25 en PRs de esta sesion]
- Endpoint /api/delegate en hub.py: 0 refs en web/src, el CLI ya lo cubre.
  cotizacion/render + SSE: 0 refs en frontend -> podar o declararlos API-only
  en F2 (decidir en el PR, con el manual delante).
  [EJECUTADO 2026-07-25 en PRs de esta sesion]
- capataz.py en el cron de MAK: superseded por agente_real.py (LAST_HANDOFF lo
  declara "el reemplazo"; conviven desde 07-20). Retirar del cron, archivar el
  espejo en el repo.
- datadrops/: codigo cableado (cli.py, hub.py) pero ultimo drop real
  2026-07-03 y medido abandonado desde 2026-06-22. BAJA prioridad: archivar
  comando + modulo cuando se toque esa zona; no gastar sesion dedicada.

### REVISAR ANTES DE TOCAR (I3: changelog + git log primero; un Haiku los
marco "sueltos" pero pueden ser recien nacidos sin consumidor AUN)
- tools/token_budget.py, tools/verify_all.py, tools/context_pack.py: huelen a
  AI Op Layer v1 del 2026-07-25 (misma madrugada). Recien creados != muertos.
- tools/render_video_rd.py: pipeline 4 ejes semana 07-21, probablemente vivo.
- tools/enviar_a_mak.py + instalador: SendTo WIN->MAK probado e2e 07-23.
- tools/tapiz_live_loop.py, tapiz_telemetry.py, crtdots.py: cultura. Preguntar
  al usuario, no matar de oficio.

### PESO MUERTO EN GIT (decision del usuario, no urgente)
- svg/suplementos_rd/09_contraportadas_dark/: 39MB de cache reproducible
  (generador vivo: gen_contraportadas.py). Sacar del tree si el usuario da OK.
- jobs/2026-07-05_contraportadas: 262MB en disco -- VERIFICAR si esta trackeado
  antes de opinar sobre purga.

### NO TOCAR
- Skills caveman* (7): uso activo del usuario.
- _archive/: 0 imports vivos, correcto como esta.
- cultura/mak_plataforma/: espejo de produccion de MAK (se gobierna por PR).
- README.md raiz: obra terminada del artista.
- Suite noisette (tests/test_noisette_real_fixture.py): fixture = fuente de
  verdad, jamas especular schema.

## 3. Decisiones abiertas del usuario (marcar, no resolver solas)

1. projects/piezas_vectoriales/cotizacion-general-de-servicios-...: untracked,
   generado por una prueba de agente sin pedirlo. Borrar / conservar /
   commitear.
2. F3: forma de la division ISKVW (perfil nuevo agrupando studio+cultura, o
   renombrar studio, u otra).
3. F4: forma de suplementos en la app (panel lectura+validate, o tarjeta
   minima).
4. Purga de los MB gordos (39MB contraportadas dark; 262MB jobs si trackeado):
   solo del tree, o tambien del historial.
