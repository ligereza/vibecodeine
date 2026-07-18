# PLAN UPSCALE -- ruta 0.53.0 -> 0.55.0+ (Cauce, 2026-07-18)

Objetivo: dos bumps de milestone en la(s) proxima(s) sesion(es), dejando cada
frente VERIFICADO y operable por manos gratis. Doctrina: CLAUDE.md (director
decide/verifica, haiku/sonnet ejecutan volumen, gate CI + revisor).

## Estado de partida (verificado 2026-07-18)

- main = v0.53.0, suite verde, CI verde, branch protection activa.
- PR #71: conflictos RESUELTOS (merge ead2fa2 pusheado), CI corriendo.
  Contiene: MAK generativo (backlog lagunas, matcher RD delta-E, works.json),
  dispatcher exit-2, 21 tests serve, borrado total auth MAK (LAN privada).
- Worktrees vivos: god-haiku-fixes (PR #71) y mak-research-cultural (historico
  post #48; candidato a remover tras merge de #71 si diff vs main = 0).
- 41 tests nuevos ig/analyze ya en main (0.53.0).

## 0.54.0 -- MERGE PR #71 (gate: usuario)

1. USUARIO: review + merge PR #71 (CI ya debe estar verde; conflictos listos).
2. Agente post-merge (30 min, Haiku + director spot-check):
   - pull main, suite completa + flujo verify.
   - resolver LAST_HANDOFF/SESSION_STATE si el merge duplico secciones.
   - limpiar: worktree god-haiku-fixes + rama (ya mergeada); evaluar
     mak-research-cultural (diff vs main; si 0, remover).
   - bump 0.54.0 (version.py changelog + pyproject + state files), push.
3. Riesgo conocido: la suite del worktree corre contra el editable install de
   main; la verdad es el CI del PR, no el pytest local del worktree.

## 0.55.0 -- UN frente grande, elegir 1 de 3 (decision usuario)

### Opcion A: MAK pausa-en-error end-to-end (requiere SSH al box)
- NO re-buscar: NO existe implementacion (verificado exhaustivo 2026-07-18,
  ver LAST_HANDOFF seccion GODSPEED). Solo diseno:
  cultura/mak_plataforma/diseno/eventos_y_backlog.md + emisor vivo.
- Construir: investigar() checkpoint/reanudar, --resume en main(), worker.py
  reconocer "PAUSADO: ", /api/reanudar en interfaz.py + hub.py, botones
  reintentar/editar/saltar/abortar.
- Deploy pendiente que arrastra: retencion.py + fallback_util + codex_lib
  integrado al box (el PR #71 los deja en repo, no en el box).
- Gate RESUELTO 2026-07-18: SSH = mak@192.168.50.2 (llave id_ed25519 local ya
  autorizada, host dell-11m, verificado BatchMode). Frente DESBLOQUEADO.
  Ojo fail2ban: pocas conexiones, usar ControlMaster o comandos agrupados.

### Opcion B: pieza MANIFIESTO via motor-omega (sin dependencias externas)
- Candidatas vivas: #8 cartografia filtros (ya tiene base en
  projects/cultura/cartografia_filtros/), o la que herede una semilla de
  puente/SEMILLAS.md. Protocolo: skill motor-omega (condicion Omega11 ANTES
  de producir). Trigger de escalada: pieza cultural = Fable/Opus decide.
- Gratis-friendly: el instrumento queda operable sin Claude.

### Opcion C: works.json -> portfolio.yml (blast radius CI, decision usuario)
- generar_works.py existe + 20 tests (PR #71). Falta el paso en
  .github/workflows/portfolio-auto que lo corra y publique.
- Toca workflows CI = trigger de escalada + aprobacion explicita del usuario.
- Chico pero visible: portfolio publico deja de ser placeholder-catalogo.

## Tareas de fondo (cualquier sesion, sin gate)

- Emisor HALLAZGO faltante: correlacionar_archivos.py + memoria.py (resto ya
  cubierto por PR #71).
- Vigilar peso repo: svg/suplementos_rd ~51M regenerable, .git 36M.
- tests/test_smoke.py skip permanente (test_image.png): decidir fixture o
  borrar el test.

## Llaves del usuario (sin cambio, siguen pendientes)

noisette ojo humano en Chataigne | PAT Termux (~/.airdrop_token) |
AccessibilityService xio | data 13 productoras | specs venues OpenKlub/
Paralelo89 | SSH MAK (desbloquea Opcion A).

## Regla de ejecucion pa la proxima sesion

Arrancar: leer LAST_HANDOFF -> este plan -> confirmar CI de #71 -> 0.54.0.
Despues elegir opcion 0.55 segun que llave este disponible. Todo lo mecanico
en olas haiku/sonnet con verificacion mecanica del director (patron GODSPEED
.claude/skills/godspeed/SKILL.md tras merge #71).
