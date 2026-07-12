# PLAN DETALLADO -- siguiente agente (desde Cauce, 2026-07-12)

Estado del repo: v0.51.0, suite verde, `flujo verify` OK. Este es el "proximo
paso" ejecutable. Orden = prioridad. Cada item dice si necesita Claude
(arquitectura/criterio) o lo puede hacer un agente gratis/Sonnet (mecanico),
segun la mision: dejar el repo operable SIN PC y SIN Claude.

## Reglas que NO se negocian (leer antes de tocar nada)
- NO activar Claude via API en GitHub Actions (decision del usuario, 2026-07-12).
- `puente/` es TEORICO (ver `puente/README.md`). No se ejecuta, no se limpia, no
  se reinterpreta lo fechado.
- `README.md` del repo es obra terminada del artista: no se le agrega nada.
- Limites cultura: descriptivo si; nada generativo de sintesis; psicosis no
  perfila personas reales; precursor solo cultura/ley/estetica.
- `.noisette`: NUNCA re-adivinar el schema (fallo 4 veces). Pedir archivo real.
- Nunca commitear secretos (`.env`, `config.json`, `*.key`, credenciales).
- `CLAUDE.md` y `context/LAST_HANDOFF.md`: ASCII-only.

## Hecho esta sesion (para no rehacerlo)
- Fold telar -> loom: sistema de motivos-plugin, 20 motivos de alfombra
  (`projects/tapiz/vibecode/loom.py` + `motifs/`). PRs #39, #40 merged. `telar.py`
  eliminado (era duplicado).
- Pieza Tilde honesta desde semilla (+)3 via motor-omega:
  `projects/cultura/tilde_residuo.py` + `TILDE_RESIDUO.md` + tests. Residuo nuevo
  (+)5 registrado en `puente/SEMILLAS.md`. PR #41 (pendiente de merge por usuario).
- Confirmado: portfolio auto LIVE (https://ligereza.github.io/portfolio-auto/),
  sin Claude API, `PORTFOLIO_TOKEN` seteado, ultima corrida OK. No requiere trabajo.
- Limpieza general del repo (handoffs viejos/confusos, junk, drift de docs).
- `puente/` marcado como teorico (`puente/README.md` nuevo).

## Prioridad 1 -- cerrar lo abierto (mecanico; agente gratis/Sonnet)
1. Mergear PR #41 (Tilde) cuando el usuario apruebe. CI verde requerido.
2. Limpieza git que quedo para el hilo principal (destructivo NO se delega):
   - worktrees leftover: `worktree-portfolio-admin`, `worktree-tapiz-ecosystem`,
     `worktree-agent-*`. Remover con `git worktree remove` si no tienen cambios.
   - ramas stale ya mergeadas: `claude/portfolio-admin`,
     `claude/director-arte-handoff`, `feat/sala3d-v2`, `feat/tapiz-*`,
     `chore/gemini-parked`. Verificar con `git branch --merged main` antes de borrar.

## Prioridad 2 -- deuda tecnica concreta (Claude, o Sonnet con plan + revisor)
3. `server.py` `/download`: si hay un endpoint sin implementar, completarlo o
   quitarlo. No dejar stub que miente.
4. `flujo brand analyze`: el help del CLI describe algo que no hace; alinear help
   con el comportamiento real o implementar la funcion.
5. Branch protection en `main` (publico): configurar desde la web de GitHub
   (require CI verde). No necesita Claude ni API.

## Prioridad 3 -- piezas nuevas del MANIFIESTO (motor-omega OBLIGATORIO)
Cada pieza arranca SOLO desde semilla viva (`puente/SEMILLAS.md`) con Omega11
declarada ANTES de producir. Estado de las 11 del `puente/MANIFIESTO.md`:
- HECHAS: #1 (git -> Resolume: `tools/vj_set/git_performance.py`), #10 (paleta
  reactivos: `projects/cultura/paleta_reactivos.py`).
- BUENAS CANDIDATAS ahora (semilla clara + self-contained, sin API/hardware):
  - #4 Esteganografia: embeber el changelog en el canal ilegible de los SVG que
    se entregan. Codigo puro. Semilla (+)3 (canal ilegible = residuo). Claude o
    Sonnet+revisor.
  - #8 Cartografia de filtros: mapear QUE bloquea cada modelo como su Tilde.
    DESCRIPTIVO (registra el borde, NO cruza el bloqueo, NO extrae contenido
    vedado). Semilla (+)3. Claude (criterio de seguridad).
  - #6 Cron nocturno con borrado: genera una variante por noche; una vez por
    semana se borra una sin mirar. Self-contained (cron + regla). NO usa Claude
    API (agente gratis/local). Semilla: la regla de freno del motor.
- BLOQUEADAS / no ahora:
  - #2 duelo de modelos: Gemini PARKED -> falta un 2do modelo util. Esperar.
  - #3 cuatro estaciones (multi-agente): potente pero caro. Correr SOLO con orden
    explicita del usuario (ultracode/workflow).
  - #5 wifi-galeria: requiere hardware ESP32. Cuando haya evento.
  - #7 test de bifurcacion: el usuario pidio NO trabajar mas sobre ese registro.
  - #11 entrenar modelo con flyers: requiere infra de training. Fuera de alcance.
  - (+)2 (OBRA_02): bloqueada esperando lector humano. No generar desde ahi.

## Como arrancar una pieza puente (recordatorio motor-omega)
(a) nombrar semilla viva de SEMILLAS.md -> (b) precipitar (cruzar con material
existente) -> (c) sobre-narrar (mantener >1 lectura defendible) -> (d) escribir
Omega11 ("pierde si ___", evaluable por otro) ANTES de producir -> (e) registrar
resultado fechado en SEMILLAS.md; los fracasos no se reinterpretan.

## Verificacion (siempre, antes de cerrar)
```
py -m compileall src/flujo
py -m pytest tests/ -q
py -m flujo verify
# si tocas web:
cd web && npm run typecheck && npm run build:context && cd ..
```

## Entrada rapida para el que llega
1. `context/LAST_HANDOFF.md` (estado corto).
2. Este plan.
3. Contexto de una tarea: `py tools/vibo_voz/contexto_repo.py task "<keywords>"`.
4. `puente/README.md` aclara que puente es teorico (no confundir con codigo).

## Deuda de docs (reportada por la limpieza 2026-07-12, no urgente)
La limpieza de esta sesion resolvio lo seguro (Vibo -> Cauce, punteros muertos,
3 handoffs viejos archivados, 3 docs de entrada obsoletos convertidos en stubs a
CLAUDE.md, junk y ramas/worktrees stale). Quedo pendiente lo que necesita criterio:
- Sellos "verificado v0.48.5" en docs/CLI.md, docs/AGENT_AIRDROP_PROTOCOL.md y
  docs/SCRIPTS_INVENTORY.md: NO subir el numero a mano (seria afirmar una
  verificacion falsa, el peor patron del repo). Re-verificar de verdad contra el
  codigo actual y recien ahi actualizar el sello.
- CONTRIBUTING.md menciona `scripts/checkpoint.sh` (superseado por
  validate_airdrop.py + run_airdrop_checks.py) y no nombra CLAUDE.md. Rewrite.
- docs/DIRECTOR_PLAN.md (v0.49.0, 2026-07-10) describe a Gemini como routing
  activo; anotarlo como historico o refrescar (Gemini PARKED desde 2026-07-10).
- CLAUDE.md, subseccion "Gemini-to-Claude desktop": presenta la app como Gemini
  vivo sin el caveat de PARKED que ya esta en la tabla del equipo. Agregar una
  linea (ASCII) aclarando que hereda el limite de Gemini PARKED.
- .claude/commands/*.md quedaron staged pero son boilerplate generico externo
  (push-all.md hace `git add .` + push directo, contra el modelo del repo).
  Decidir keep / gitignore / borrar (no los commiteo en esta sesion).
- Menciones "Vibo" fuera de docs/ (tools/ADOBE_TOOLKIT.md, tools/adobe_panel/,
  proposals/*.md): actualizar a Cauce cuando se toquen esos archivos.
- Ramas locales sin mergear (chore/gemini-parked, worktree-tapiz-ecosystem) y
  ramas remotas ya mergeadas: revisar y limpiar (git, hilo principal).
