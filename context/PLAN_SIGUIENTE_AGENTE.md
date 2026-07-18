# PENDIENTES + FUERTE/DEBIL -- checkpoint cierre (Cauce, 2026-07-18)

Estado del repo: v0.55.0, suite VERDE 2026-07-18 (899+ tests, compileall OK,
flujo verify OK). main con PRs #72-#87 mergeados (MAK fases 1-3, portfolio vivo,
repair systemd). MANIFIESTO 6/11 PIEZAS CERRADAS.

## Reglas no negociables
- NO activar Claude via API en GitHub Actions.
- `puente/` = TEORICO (no se ejecuta).
- `README.md` = obra terminada (sin cambios).
- `.noisette`: fixture real tests/test_noisette_real_fixture.py es la fuente de verdad.
- Nunca commitear secretos (.env, *.key, cultura/.dev*).
- `CLAUDE.md` y `context/*.md`: ASCII-only.

## FUERTE (verificado 2026-07-18)
- Suite VERDE 899 tests, compileall OK, CI matrix ubuntu+windows strict.
- xio on-device: server Termux+Shizuku VIVO, 23+ plugins, showcontrol desplegado.
- MAK dual-dept operativo: research+codex stack compartido, WIN fallback, pausa-en-error,
  systemd mak-codex reparado (enabled+EnvironmentFile opcional+WorkingDirectory fijo).
- Portfolio publico LIVE (ligereza.github.io/portfolio-auto, 8 obras, 0 Claude API).
- RD pipeline validado: contraportadas/flyers/cotizaciones end-to-end + audits aplicados.
- Higiene: 0 cache, branch protection ACTIVA, worktrees vivos = god-salud-integridad.

## PENDIENTES USUARIO (bloqueadores ajenos, prioridad alta)
1. PAT Termux (~/.airdrop_token) para redeploy por USB sin sesion interactiva.
2. AccessibilityService en Ajustes Xiaomi (reboot auto-recovery de xio server).
3. Data 13 productoras + specs venues OpenKlub/Paralelo89 para gota_rd backend.
4. Pieza MANIFIESTO #1 en vivo con Resolume: tools/vj_set/RUNBOOK.md (demo).

## PENDIENTES SIN GATE (backlog tecnico, puedo iniciar pero no termino solo)
- units mak-hub y mak-xio del box estan disabled (misma fragilidad reboot que
  tenia mak-codex, ya reparada+enabled) -- revisar/habilitar cuando sea seguro.
- divergencia grafo.py (fallback al RESTO de llm.order) vs cadena.py (solo
  posteriores) -- posible unificacion documentada en PR #85 notas, backlog.
- piezas MANIFIESTO #2/#3/#11 con llave bloqueada (usuario), #7 NUNCA tocar
  (orden expresa), #8 cartografia filtros (SOLO descriptor).

## VERIFICACION (siempre antes de cerrar)
```
py -m compileall src/flujo
py -m pytest tests/ -q
py -m flujo verify
cd web && npm run typecheck && npm run build:context && cd ..
```

## ENTRADA RAPIDA
1. context/LAST_HANDOFF.md (estado del dia).
2. Este plan (pendientes + fuerte/debil).
3. py tools/contexto_repo.py task "<keywords>" para ruta de tarea.
4. puente/README.md para aclarar que puente = TEORICO.
