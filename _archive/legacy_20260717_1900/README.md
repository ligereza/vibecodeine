# Archivo legacy 2026-07-17 19:00 (cierre de sesion MAK, limpieza de handoffs viejos)

Movido aqui via git mv (historial completo en git log --follow). Motivo por item:

- `ACTIVE_PLAN_demo-jefe-20260629.md` (era context/ACTIVE_PLAN.md): plan de una
  demo para jefatura del 2026-06-29, hace mas de 2 semanas. La demo ya paso;
  el archivo quedo suelto en context/ sin marca de cierre, desorientando a
  cualquier agente que lo leyera pensando que era trabajo activo.
- `checkpoints_2026-07-03/` (eran 3 archivos en checkpoints/): salidas viejas
  de `crear_checkpoint()` (src/flujo/airdrop.py), un mecanismo de solo
  escritura -- no lee ni depende de archivos previos, asi que archivar estos
  3 no rompe nada. checkpoints/.gitkeep queda en su lugar para que el
  mecanismo siga funcionando.

Tambien eliminado (no archivado, `git rm` directo): `context/PLAN_OPUS_SALA3D.md`
-- el propio archivo instruia "Borrar este archivo al cerrar (su contenido
pasa al handoff normal)"; el trabajo que describia (PR #30, sala 3D v2) ya
esta mergeado y documentado en SESSION_STATE.json desde 2026-07-11. Se honro
la instruccion del autor original en vez de archivarlo.

NO se tocaron `.archive/`, `_archive/` (las demas carpetas legacy) ni
`docs/handoffs/archive/` -- son las ubicaciones de archivo oficiales segun
CLAUDE.md, no material suelto.
