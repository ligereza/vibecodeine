# PLAN SEMANAL OPUS -- 2026-07-20 al 2026-07-26 (cumplir a pie de la letra)

Escrito por Fable al cierre de 2026-07-18. Operador previsto: OPUS como director,
mismo sistema (godspeed: director orquesta, haikus/sonnets ejecutan). Este plan
es un CONTRATO: cada dia tiene objetivo, comandos exactos, gate de verificacion
y salida-si-bloqueado. No improvisar el orden; si un dia se cae, su bloque pasa
al backlog del domingo, no se mezcla con el dia siguiente.

## Doctrina de operacion para Opus (leer antes del lunes)

1. Entrada obligatoria: CLAUDE.md -> context/LAST_HANDOFF.md (CIERRE DEL DIA)
   -> skill .claude/skills/godspeed/SKILL.md (checklist completo) -> este plan.
2. Mismo sistema, mano mas conservadora: Opus NO relaja ningun gate. Ante
   ambiguedad real (2+ opciones defendibles con costo alto) pregunta al usuario;
   nunca adivina esquemas externos (.noisette = fixture o nada).
3. Todo trabajo mecanico a subagentes (haiku lecturas, sonnet edits); Opus
   gasta su cupo SOLO en spec, contradicciones y accept/reject.
4. Verificacion es del director, nunca del builder: suite completa + CI matrix
   por PR; en el box, curl/PID/metadata reales, jamas el "OK" del operador.
5. Reglas duras vigentes: kill por PID (nunca pkill -f via ssh); secretos =
   NUNCA tocar ni buscar; rama head se borra SOLO con state==MERGED; una linea
   de handoff por sesion; ASCII en context/.
6. Anti-bloqueo: warn-first antes de zona sensible (memoria antiblock-warn-first);
   comando denegado 1 vez = partirlo en simples; 2 veces = lane del usuario,
   emitir el comando pasteable y seguir con otra cosa.

## LUNES 20 -- salud del organismo + refresh automatico

- 06:00 UTC corre el workflow semanal de portfolio-auto. Verificar despues:
  `curl -s https://ligereza.github.io/portfolio-auto/flujo-works.json | py -c "import json,sys;print(len(json.load(sys.stdin)))"`
  (esperado: >=8). Si fallo: `gh run list -R ligereza/portfolio-auto` y reparar.
- Auditoria semanal repo: `py -m pytest tests/ -q` (esperado exit 0, ~950 tests),
  `py -m flujo verify`, `py tools/contexto_repo.py`, peso repo (`git count-objects -vH`).
- Box: pedir al usuario UN reboot del MAK (o hacerlo via ssh si lo autoriza) y
  verificar la tesis de la semana pasada: los 3 units (mak-codex/hub/xio)
  levantan SOLOS. Gate: `systemctl --user is-active mak-codex mak-hub mak-xio`
  = active x3 y :8890/:8891/:8900 en 200 SIN intervencion manual.
- Verificar salud_proveedores en accion: `ssh mak@192.168.50.2 "cat ~/research/salud_proveedores.json"`
  tras un dia de jobs; si groq sigue 429, confirmar que quedo demotado.
- BLOQUEADO (sin reboot autorizado): dejar el gate documentado y seguir.

## MARTES 21 -- MAK produce de verdad (volumen)

- Objetivo ambicioso: 10 jobs research REALES del backlog generativo
  (`~/plataforma/backlog.jsonl`) + 4 tareas codex, todos via hub :8900, cero
  fallos terminales (pausa-en-error puede saltar, no reventar).
- Verificar el ciclo completo de una pausa real: forzar `--providers noexiste`
  en 1 job -> PAUSADO -> saltar -> informe. Gate: eventos human_gate + node_end
  en eventos.jsonl con el MISMO job_id.
- Verificar que el backlog CRECE (cosecha de LAGUNAS): `wc -l ~/plataforma/backlog.jsonl`
  antes/despues. Si no crece, es bug de trabajo.py: spec + fix + PR.
- Panel: confirmar 0 eventos sin_job nuevos (integridad); si aparecen, hay un
  escritor fantasma -> investigar ANTES de seguir.

## MIERCOLES 22 -- RD / dinero (con o sin llaves del usuario)

- Si el usuario dio data de las 13 productoras: cargarla (`py -m flujo rd-db build`),
  regenerar catalogo (`docs/CATALOGO_RD.md`), 1 cotizacion real de prueba
  (`py -m flujo brief paquete-cotizacion jobs/<job>`). Gate: suite + validate SVGs.
- Si NO: preparar el terreno igual -- 13 stubs de perfil con campos vacios
  marcados PENDIENTE-USUARIO (no inventar datos; valores de dinero = trigger
  de escalada, no delegar a haiku).
- Reactivo_matcher: 5 lookups reales contra reactivos.json y documentar 1 caso
  de uso en docs (delta-E presuntivo, disclaimer intacto).

## JUEVES 23 -- MANIFIESTO (empujar de 6/11 hacia 8/11)

- Releer MASTER_PLAN.md recuento. Piezas candidatas SIN llave: revisar si #2
  (segundo modelo util: WIN deepseek ya opera -- puede cerrar la pieza?) y #3
  admiten cierre con lo que ya existe. Regla de freno motor-omega: git log
  ANTES de construir (pieza "libre" puede estar hecha -- paso con #10).
- Ratchet de piezas hechas: cada pieza cerrada gana 1 test o 1 registro Omega11
  que no tenia. #7 NO TOCAR (orden expresa). #11 sigue con llave (infra).
- Gate: recuento actualizado en MASTER_PLAN.md + SEMILLAS.md fechado, PR verde.

## VIERNES 24 -- xio (lo que el hardware permita)

- Si AccessibilityService ya esta activo (preguntar al usuario): cerrar el loop
  de reboot autonomo del telefono y probarlo EN VIVO (pc_reboot_watch.sh).
- Con o sin eso: wifi_intelligence en uso real -- 1 scan via /scan del server
  on-device (ventana USB si hay), fixture nueva si aparece formato no cubierto.
- Trampas conocidas: MSYS_NO_PATHCONV=1 para adb; run_server.sh redeploya TODO;
  adb solo en el checkout principal. Dejar el telefono como estaba.
- BLOQUEADO (sin telefono): tests offline de plugins sin cobertura, mismo
  patron PluginContext-stub de test_showcontrol_token.py.

## SABADO 25 -- pieza #1 en vivo (Resolume) o su ensayo

- Si el usuario da ventana con Resolume abierto: RUNBOOK de tools/vj_set --
  osc_sender contra Resolume real, pieza #1 performada (git -> OSC -> visual).
  Gate: el usuario CONFIRMA que vio el efecto (verificacion visual = humana,
  leccion xdotool).
- Si no hay ventana: ensayo en seco contra un listener UDP propio (ya testeado)
  + dejar el comando exacto listo en una linea para cuando haya ventana.

## DOMINGO 26 -- cierre semanal (obligatorio, no negociable)

- Merge de todo lo verde; 0 PRs abiertos; 0 ramas extra (regla state==MERGED).
- Limpieza: __pycache__/.pytest_cache/_logs local; `git fetch --prune`.
- Metricas de la semana en el handoff: PRs mergeados, tests totales, piezas
  MANIFIESTO, dias del box sin intervencion, jobs MAK completados.
- LAST_HANDOFF.md: nuevo CIERRE DE SEMANA arriba (compacto, ASCII) +
  SESSION_STATE.json + PLAN_SIGUIENTE_AGENTE.md; escribir el plan de la
  semana siguiente CON ESTE MISMO FORMATO (el plan es un artefacto semanal).

## Metricas de exito de la semana (ambicioso pero medible)

- 5+ PRs mergeados con CI matrix verde. Suite >= 950 tests, 0 rojos.
- MANIFIESTO: 6/11 -> 8/11 (o justificacion escrita de por que no).
- Box MAK: 7 dias sin intervencion manual (reboot-proof probado el lunes).
- 10+ jobs research + 4 codex reales completados; backlog neto creciente.
- 0 eventos sin_job nuevos; salud_proveedores con datos reales de la semana.
- Pendientes-usuario: lista igual o mas corta que el domingo anterior.
