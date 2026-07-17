# Archivo legacy 2026-07-16 20:00 (checkpoint limpieza)

Movido aqui via git mv (historial completo en git log --follow). Motivo por item:

- `xio_advplugins/` (era xio/advplugins): los 12 plugins fueron absorbidos por
  nombre identico en xio/new-plugins/. Copia muerta desde 2026-07-12.
- `agente1_flyers_web/` (era projects/agente1_flyers_web): brief de delegacion
  ya materializado en web/src/ (workspaces RD/Studio). No se itero mas.
- `agente2_resolume_chataigne/` (era projects/agente2_resolume_chataigne): brief
  de delegacion; el trabajo real siguio en src/flujo/resolume/. Regla .noisette
  (no adivinar schema) sigue vigente en CLAUDE.md.
- `mejoras_herramientas_2026-06.md` (era proposals/): propuesta 2026-06-22 ya
  ejecutada (hub diario + tooling low-token contexto_repo.py / token_budget.py).
- `dot-claude-commands-push-all.md` (era .claude/commands/push-all.md): comando
  boilerplate externo que hacia `git add .` + push directo, contra el modelo del
  repo (PR + gate CI). Retirado del set de comandos activos.
- `dot-claude-commands-README.md` (era .claude/commands/README.md): el harness
  lo interpretaba como comando roto ("<picture>").

NO se archivaron (dependencias vivas verificadas por grep 2026-07-16):
- projects/flyer_eventos: referenciado por src/flujo (dashboard/scoring.py,
  flyer/project.py, intake/pipeline.py).
- xio/actual: xio/new/server.py y pc_reboot_watch.sh usan
  xio/actual/platform-tools/adb.exe como adb bundled.
