# MASTER PLAN v2 -- pauta de alta ambicion + auto-recarga (Cauce, 2026-07-17)

Este documento es DOCTRINA + BACKLOG AMBICIOSO por frentes. No reemplaza a
`context/PLAN_SIGUIENTE_AGENTE.md` (pendientes cortos de la proxima sesion);
lo alimenta. Jerarquia de fuentes: instruccion directa del usuario > CLAUDE.md
> este MASTER_PLAN > PLAN_SIGUIENTE_AGENTE > docs especificos.

v2 (2026-07-17): el usuario corrigio una lectura mia de la regla de freno.
La regla es correcta PARA PIEZAS CULTURALES, pero yo la extendi a todo el repo
y me choque contra la muralla "aqui te lo dejo en tus manos, no puedo seguir".
Esa muralla es un error, no disciplina. Ver seccion 0b (anti-muralla).

## 0. Doctrina (por que existe este plan)

- Metrica de exito INVERTIDA: el repo vale por cuan poco necesita a Claude.
  Cada tarea de este plan debe dejar un artefacto operable por agentes
  debiles/gratis o por el usuario sin PC. Control sin PC (airdrop-gate, T-F4):
  disparo AUTOMATIZADO desde XIO/Xiaomi (Termux + gh) o MANUAL desde el iPhone
  con la app de GitHub (crear release + revisar/mergear el PR). Las dos rutas
  no necesitan PC.
- Ningun agente entrega a medias: TODO/stub/pass silencioso = entrega invalida.
- Toda pieza cultural nace de semilla viva (`puente/SEMILLAS.md`) con Omega11
  (condicion de fracaso evaluable por otro) declarada ANTES de producir.
- Gate obligatorio: CI verde + revisor barato; el director (Claude caro) entra
  solo si el gate escala arquitectura/seguridad.
- WIP LIMIT: maximo 1 pieza cultural abierta por linea (tapiz/tilde/psicosis/
  precursor) y 1 tarea grande por frente a la vez. Terminar > empezar.

## 0b. Anti-muralla y auto-recarga (v2, la correccion del usuario)

La regla de freno del motor-omega es SOLO para el track cultural: forzar una ⊕
que no existe produce obra huerfana, y ahi parar es correcto. Pero el resto del
repo (tecnico, infra, calidad, tooling, docs, decisiones) casi nunca esta sin
trabajo legitimo. Confundir "no hay semilla cultural" con "no queda nada que
hacer" es la muralla que hay que evitar.

Regla anti-muralla: NO cerrar un turno con "te lo dejo en tus manos" mientras
exista trabajo autonomo verificable. Antes de declararte sin trabajo, corre una
PASADA DE DESCUBRIMIENTO (el mismo barrido sonnet del checkpoint) y elegí el
proximo item. Solo se para de verdad cuando: (a) el track cultural no tiene ⊕ y
(b) la pasada de descubrimiento no encontro NINGUN trabajo tecnico/infra sin
depender de una llave del usuario o de zona ajena (MAK). Eso es raro; cuando
pase, se dice explicito QUE se busco y por que no habia, no un "no puedo seguir"
seco.

Backlog SIEMPRE-DISPONIBLE (fuente de la proxima ola cuando el resto bloquea,
ninguno necesita llaves del usuario ni toca MAK):
- Cobertura de tests: buscar rutas criticas sin test y cubrirlas.
- Codigo muerto / drift de docs: cazar y limpiar (encargado de limpieza).
- Operabilidad sin-Claude: cablear lo que quedo suelto (ej. wire de la RD DB a
  cotizaciones/hub para que no sea otro zombi), tooling para agentes gratis.
- Hardening: seguir el patron de auditoria (silent-fails, injection, races).
- usar-o-archivar (T-F3): decidir los stubs vivos; archivar el muerto.
- Regenerables: catalogos/proyecciones que deban refrescarse desde su fuente.

Cierre de ola SIN muralla: al terminar, o hay proxima ola autonoma (se arranca)
o se documenta la pasada de descubrimiento y las llaves reales que faltan.

## 1. Horizontes

- H1 (esta semana): consolidar -- PRs abiertos mergeados, docs veraces,
  primeras 2 piezas MANIFIESTO en codigo real con tests.
- H2 (este mes): el show -- cadena xio -> showcontrol -> Resolume operable
  desde el telefono en un evento real; MAK produciendo dossiers solo.
- H3 (trimestre, PLAN_ANUAL): obra publica -- portfolio vivo que se
  auto-actualiza, pieza wifi-galeria cuando haya evento, repo 100% operable
  sin cuenta Claude.

## 2. Frentes y tareas ambiciosas

### F-A NUCLEO VJ / ESCENA (Resolume, timecode, noisette, showcontrol)
Estado: showcontrol (OSC/Art-Net/sACN) vivo en el telefono; vj_set
git_performance.py convierte git log en cue sheets; automator .noisette
EXPERIMENTAL bloqueado por fixture real (4 intentos fallidos adivinando).
- T-A1 [HECHA 2026-07-16, delegada por el usuario al director]: no hizo
  falta exportar nada -- los .noisette reales YA EXISTIAN en C:/IA
  (prueba.noisette + prueba(2).noisette, guardados por el Chataigne 1.10.3
  del usuario el 2026-06-30, sesion OSC->127.0.0.1:7000 + LTC + 2 Actions).
  Copiados como fixtures a tests/fixtures/chataigne_1103_real*.noisette
  (escaneados: sin credenciales, solo localhost).
- T-A2 [HECHA 2026-07-16]: NO hubo que reescribir -- la validacion contra la
  fixture real (9 tests, tests/test_noisette_real_fixture.py) probo que la
  v0.48.5 del builder ya era estructuralmente IDENTICA al archivo real
  (claves, metaData, modulo OSC, Actions, naming action/action1, condicion
  LTC). Leccion dura: 4 reescrituras adivinando y la ultima era correcta;
  lo que falto siempre fue el fixture, no mas codigo. Queda 1 paso de
  confianza total [USUARIO, 1 minuto]: abrir un .experimental.noisette
  generado en la GUI de Chataigne y confirmar que carga sin warnings.
- T-A3 [HECHA 2026-07-16, ola 2]: 26 tests nuevos para git_performance.py
  (repos git desechables en tmp_path, nunca la historia viva). El sonnet
  encontro 2 bugs reales (repo vacio reventaba con RuntimeError; --limit 0
  ignorado por truthiness); el director los arreglo y los tests ahora fijan
  el comportamiento correcto.
- T-A4 [director+usuario, H2]: ensayo end-to-end en evento: telefono manda
  OSC a Resolume real via showcontrol; runbook en xio/ (patron
  HOTSPOT_SHOW_RUNBOOK).

### F-B XIO (telefono = cerebro de escena y router del equipo)
Estado: server on-device vivo (23+ plugins), charge-control no-root,
self-heal hotspot, MAK aislado 403. Gap honesto: reboot mata el server
(AccessibilityService sin instalar).
- T-B1 [USUARIO]: build/install/grant de xio/hotspot_boot_service en el
  telefono. Cierra el unico gap de autonomia.
- T-B2 [HECHA 2026-07-16, ola 3]: gate opcional XIO_SHOWCONTROL_TOKEN sobre
  las ~25 rutas del plugin (override de register_route, hmac.compare_digest,
  env por-request; sin token = comportamiento identico). 6 tests + 62
  preexistentes verdes. PENDIENTE OPERATIVO: el telefono corre la copia
  desplegada -- redeploy del plugin (RUNBOOK seccion 7) para que aplique.
- T-B3 [HECHA 2026-07-16, ola 2]: xio/RUNBOOK.md nuevo (8 secciones, cada
  comando verificado contra los scripts reales) + puntero en los 10 .md
  originales. Contradicciones flageadas sin resolver en silencio:
  plugin_guardian duplicado byte-identico (new-plugins/ vs seguridad/),
  xio/new/plugins/ stale vs new-plugins/ real, y el subnet ".69" del
  historial de hotspot no aparece documentado en ninguna fuente.

### F-C MAK (organismo research en la caja Linux)
Estado: research 7 modos + codex + plataforma vivos en MAK; PR #48 MERGEADO
2026-07-17 (commit 6a2b147), codigo en main. PR #49 abierto (DRAFT). Aislado del xio (403).
- T-C1 [USUARIO]: mergear PR #49 (CI verde ya).
- T-C2 [director, tras merge]: revisar el gap de seguridad del puente
  xio_puente GET-only (que MAK jamas pueda escribir al xio) con test.
- T-C3 [sonnet, H2]: pipeline dossier: MAK research -> markdown con fuentes
  -> projects/cultura/dossiers/ via airdrop (sin Claude en el loop).
  Aceptacion: 1 dossier real generado por MAK y validado por el gate.

### F-D RD COMERCIAL (entregables que pagan el show)
Estado: pipeline contraportadas/flyers/cotizaciones validado end-to-end;
plantilla real de produccion vive en Desktop/ai_illustrator (fuera del repo).
- T-D1 [sonnet]: smoke real de productoras.py con fixture de flyer en
  tests/fixtures/ (USUARIO aporta el .jpg). Sin Gemini: solo la parte PIL.
- T-D2 [HECHA 2026-07-16, ola 3]: scripts/generar_catalogo_rd.py genera
  docs/CATALOGO_RD.md deterministico desde packs.py/costs.py/engine.py (cero
  precios hardcodeados, 10 tests). HALLAZGO CRITICO del sonnet: `flujo
  cotizaciones` estaba ROTO (flujo.brand vaciado en una migracion dejo
  ImportError en engine.py; piezas.py lo tragaba con try/except pass).
  Director restauro brand.py como loader real de projects/flujo/flujo.json
  y arreglo el import de piezas.py; verificado en vivo ambas audiencias.
- T-D3 [H2]: 1 entrega comercial completa corrida SOLO por agentes gratis
  siguiendo skills entregas-rd/taller-svg-rd (Claude solo audita el resultado).

### F-E CULTURA / OBRA (motor-omega)
Estado: tapiz/loom maduro (20 motivos); tilde SPEC sin render; MANIFIESTO
2/11 hechas; MAPA_GENERATIVO (PR #49) cura 19 ideas a medias.
- T-E1 [sonnet] pieza MANIFIESTO #4 -- ESTEGANOGRAFIA: modulo
  tools/svg/steg_changelog.py que embebe version+hash del changelog en canal
  ilegible de los SVG entregados (metadata/atributos no-render) + extractor +
  tests roundtrip. Semilla: (+)3 (canal ilegible = residuo). Omega11
  DECLARADA: la pieza PIERDE si (a) el roundtrip embed->extract falla tras
  pasar el SVG por svg_lint, o (b) el SVG renderiza distinto (diff visual) con
  el payload dentro.
- T-E2 [sonnet] TILDE RENDER: implementar el render de projects/tilde/SPEC.md
  (sobrevivencia-01) consumiendo el formato de desktop/tilde_meter.py; fixture
  sintetica si no hay corpus real aun. Omega11 DECLARADA: pierde si el render
  necesita datos inventados (no medidos) para verse "bien".
- T-E3 [sonnet] pieza MANIFIESTO #6 -- CRON NOCTURNO CON BORRADO: script
  self-contained (tools/cron_nocturno/) que genera una variante de loom por
  noche y una vez por semana borra una SIN MIRAR (regla de freno del motor);
  sin Claude API; doc de instalacion (Task Scheduler Windows + cron Termux).
  Omega11 DECLARADA: pierde si el borrado es reversible o si requiere
  decision humana.
- T-E4 [HECHA 2026-07-16, director] pieza MANIFIESTO #8 CARTOGRAFIA DE
  FILTROS: projects/cultura/cartografia_filtros/ mapea el borde donde un
  agente con full-auth igual choca el clasificador; sembrada con 6 bloqueos
  reales y fechados de ESTA sesion (siluetas neutras, sin payload; guarda en
  codigo + grep). Ω11 no se cumplio. 8 tests. MANIFIESTO 5/11.
- BLOQUEADAS (no tocar): #2 (falta 2do modelo), #5 (hardware), #7 (orden del
  usuario), #11 (infra), (+)2 OBRA_02 (espera lector humano).

### F-F INFRA AGENTES (que el repo se opere solo)
Estado: CI real; airdrop protocol maduro; branch protection AUSENTE;
sellos de docs viejos; 5 SPEC-stubs sin decidir.
- T-F1 [USUARIO]: branch protection en main (require CI). El gate entero
  descansa en esto.
- T-F2 [sonnet]: re-verificacion REAL de docs/CLI.md, docs/SCRIPTS_INVENTORY
  .md, docs/AGENT_AIRDROP_PROTOCOL.md comando por comando contra v0.52.0;
  corregir texto y sello SOLO con evidencia (regla: jamas subir numero a mano).
- T-F3 [director]: politica "usar o archivar": los 5 SPEC-stubs de tools/
  (asistente_pedido, canva_data, privacidad_datos, resolume_chataigne_automator
  doc-stub, slowmo_blender_ae) reciben fecha limite 2026-08-01; sin alcance
  del usuario para esa fecha -> _archive.
- T-F4 [HECHA 2026-07-16 en codigo; ESTRENO pendiente]: disparador sin-PC
  via XIO (correccion del usuario: el Xiaomi con Termux es mejor gatillo que
  el iPhone, que queda de fallback web). Motor: .github/workflows/
  airdrop_gate.yml (release airdrop-* + ZIP -> guardas -> run_airdrop_checks
  --skip-push -> PR airdrop/<tag>). Gatillo: xio/new/airdrop_push.sh
  (Termux + gh, token fine-grained en $HOME, nunca /sdcard). Docs en
  AGENT_AIRDROP_PROTOCOL.md y RUNBOOK 7b. Estreno = primer release real
  (requiere el token en el telefono, setup del usuario).

### F-G WEB HUB
Estado: hub 3 workspaces (RD/Studio/Cultura) generado a context/*.html.
- T-G1 [qwen/sonnet, tras PR #48]: panel Cultura muestra el grafo MAK
  (canvas ya existe en el PR) sin llamadas de red nuevas.
- T-G2 [H2]: hub servible desde el telefono (xio plugin static) para operar
  el show sin PC.

## 3. Protocolo de despliegue multi-agente (obligatorio)

1. PLAN-PRIMERO: todo sonnet recibe contexto inline (rutas exactas, que NO
   tocar) y devuelve plan corto antes de editar si la tarea es >2 archivos.
2. NUNCA fire-and-forget: el director verifica output con suite + lectura
   del diff antes de commitear. Un solo commit por tarea, mensaje honesto.
3. Areas disjuntas por ola: dos agentes jamas editan el mismo archivo.
4. Verificacion por tarea: compileall + pytest + flujo verify (+ typecheck
   web si aplica). Reporte formal siempre.
5. Escalada: seguridad, credenciales, CI, airdrop.py, comportamiento publico
   del CLI -> director. Mecanico -> sonnet/qwen.
6. Cierre de ola: actualizar PLAN_SIGUIENTE_AGENTE (corto) y este plan
   (tachar/estado), LAST_HANDOFF, SESSION_STATE.

## 4. Cadencia y versionado

- Cada ola de trabajo = 1 rama + 1 PR + bump minor si cambia comportamiento.
- Checkpoint de limpieza como el de hoy: 1 vez por semana, mismo playbook
  (barrido sonnet -> decisiones director -> PR).
- Este plan se revisa al cierre de cada ola; las tareas hechas se marcan
  [HECHA fecha] en lugar de borrarse.

## 5. REFLEXION CRITICA (2026-07-16) y mejoras aplicadas en v1.1

Critica honesta del estado del repo, herramientas e ideas sin desarrollar,
tras el barrido de 5 analistas de hoy:

1. EL REPO ESCRIBE PLANES MAS RAPIDO DE LO QUE EJECUTA. DIRECTOR_PLAN quedo
   historico el mismo dia que se escribio; 5 tools/ son SPEC sin una linea de
   codigo; MANIFIESTO lleva 2/11; el PR #49 es literalmente un curador de "19
   ideas a medias". La enfermedad no es falta de ideas, es falta de
   terminacion. MEJORA APLICADA: WIP limit (seccion 0), politica usar-o-
   archivar con fecha (T-F3), y la regla de que este plan marca [HECHA] en
   vez de acumular texto nuevo.
2. EL NUCLEO DURO SIGUE SIENDO EL MAS DEBIL. La mision dice que Claude gana
   su costo en noisette/VJ/timecode, y es exactamente el frente con 4
   fracasos y 0 fixtures. La dependencia es UNA accion del usuario de 5
   minutos (exportar un .noisette). MEJORA: T-A1 marcada bloqueante numero 1
   del plan entero; nada de F-A se intenta sin ella (regla anti-reintento ya
   existia, ahora tiene tarea dueno).
3. HERRAMIENTAS ZOMBI. [PROGRESO 2026-07-17] vibo_voz ELIMINADO (las APIs de
   MAK reemplazan su routing; contexto_repo.py rescatado a tools/); gota_rd
   estaba RESUELTO hace tiempo (aviso del usuario). Quedan: desktop/ (parked
   con Gemini), compete_engine/tapiz_live_loop sin wiring declarado. Cada
   zombi cuesta contexto de agente en cada sesion. MEJORA: T-F3 les pone
   fecha; los que sobrevivan deben aparecer en un comando del CLI o en un
   skill, o se archivan.
4. SEGURIDAD REPETITIVA. Ya van 3 incidentes de keys en working tree (2.txt,
   cultura/.dev, .dev.limpio). El patron es "research deja credenciales donde
   trabaja". MEJORA: regla nueva en seccion 3: todo agente que cree un archivo
   con secretos DEBE crearlo fuera del repo o verificar el gitignore en el
   mismo paso; el checkpoint semanal incluye grep de patrones de key.
5. PESO GIT CRECIENTE. 51M de SVG regenerables trackeados + zips historicos;
   .git 36M y subiendo. No urgente, pero la tendencia es mala. MEJORA:
   checkpoint semanal vigila `git count-objects -vH`; si size-pack supera
   100M, se decide LFS o derivados-fuera-de-git ANTES de seguir.
6. EL GATE NO ESTA CERRADO. Sin branch protection, todo el discurso de "CI +
   revisor" es voluntario. Es un click del usuario. MEJORA: T-F1 al tope de
   los pendientes de usuario en todos los docs de estado.
7. LO QUE SI FUNCIONA (no tocarlo por ansiedad de mejora): xio on-device,
   pipeline RD, portfolio-auto, suite de tests, protocolo airdrop. La
   tentacion de "refactorizar lo sano" queda prohibida por esta linea.

## 6. OLA 1 (desplegada y CERRADA 2026-07-16)

- S1 = T-F2 [HECHA 2026-07-16] docs CLI/SCRIPTS_INVENTORY/AIRDROP re-verificados
  de verdad (CLI: +creative-director, +voz; INVENTORY estaba en v0.34.6 con ~20
  scripts muertos como activos y ~24 sin documentar; AIRDROP 0 errores).
- S2 = T-E1 [HECHA 2026-07-16] tools/svg/steg_changelog.py, carrier <metadata>
  no-renderizable, Omega11 (a) y (b) verificadas por test; 7 tests. Limite
  honesto: no probado contra roundtrip de Illustrator ni minifiers.
- S3 = T-E2 [HECHA 2026-07-16] hallazgo: el render YA existia (sobrevivencia.py
  cumplia el SPEC; el status del SPEC estaba stale). Se agregaron 5 tests contra
  el instrumento real y se corrigio el SPEC. Leccion: revisar status de otros
  SPEC.md antes de asignar "build" (drift plan-vs-realidad otra vez).
- S4 = T-E3 [HECHA 2026-07-16] tools/cron_nocturno/ (variante loom por noche,
  borrado ciego semanal por sha256(semana ISO), lapidas.log versionable,
  README con schtasks/cron); 13 tests.
- REVIEW ADVERSARIAL (sonnet, 2026-07-16): veredicto MERGE_WITH_FIXES.
  BLOCKER real encontrado y corregido: purge() sin guarda de semana -- un
  trigger duplicado borraba una variante extra por invocacion; fix = guarda
  de semana ISO leida de lapidas.log (el registro ya versionado) + 2 tests
  de regresion. MINOR corregido: embed() ahora barre marcadores duplicados
  (tampering) antes de insertar + 1 test. Leccion: la Omega11 "una por
  semana" era una afirmacion, no una propiedad -- el review adversarial es
  parte del gate, no adorno.
T-A1/T-B1/T-C1/T-F1 quedan en manos del usuario (son las 4 llaves que
destraban H2).

## 7. OLAS 2-3 + trabajo director (2026-07-16/17)

- OLA 2 (PR #52): T-A3 tests vj_set + 2 bugfixes; T-B3 RUNBOOK xio unico.
- OLA 3 (PR #53): T-B2 token showcontrol; T-D2 catalogo RD; fix CLI cotizaciones.
- Director: T-A1/T-A2 (PR #55) fixture .noisette real + builder validado + carga
  real en Chataigne (GUI + headless); T-F4 (PR #57) airdrop-gate sin-PC;
  T-E4 (PR #59) pieza MANIFIESTO #8 cartografia de filtros. MANIFIESTO 5/11.
- Limpieza 2026-07-17 (PR pendiente): vibo_voz ELIMINADO (APIs MAK lo
  reemplazan; contexto_repo.py rescatado a tools/); gota_rd ya estaba resuelto.

## 8. OLA 4 (auto-recargada 2026-07-17, doctrina v2 en accion)

Origen: no es semilla cultural (esas siguen bloqueadas) sino el backlog
siempre-disponible (seccion 0b). El detonante fue construir la RD DB: dejarla
suelta la volveria un zombi mas, asi que la ola la CABLEA y limpia lo que quede.
- W4-1 [director] RD DB nace CABLEADA: base de datos consultable (HECHA, este
  commit) -> siguiente, que algo real la consuma (hub o cotizaciones) para que
  no sea proyeccion huerfana.
- W4-2 [director] T-F3 usar-o-archivar: decidir compete_engine/tapiz_live_loop
  (sin wiring) y los SPEC-stubs; archivar el muerto con git mv, fecha al vivo.
- W4-3 [sonnet] pasada de descubrimiento de cobertura: rutas criticas sin test
  (empezando por lo tocado hoy) -> tests nuevos.
