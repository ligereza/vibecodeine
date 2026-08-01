# Handoffs

Este directorio centraliza la historia operacional del repo.

- La fuente de verdad activa es [context/LAST_HANDOFF.md](../../context/LAST_HANDOFF.md).
- Los handoffs historicos se guardan en [docs/handoffs/archive](archive).
- Usa este indice como punto de entrada si necesitas revisar cambios anteriores.

## Contenido vigente

- [context/LAST_HANDOFF.md](../../context/LAST_HANDOFF.md): estado diario y proximo paso operativo (unica fuente que un agente deberia leer para continuidad).
- Nivel raiz de esta carpeta: **solo** los `HANDOFF_*.md`/`HOTFIX_*.md` de la sesion o semana en curso (referencia puntual, no indice). Al 2026-07-12 no hay ninguno vigente: los de la semana anterior se archivaron en `archive/handoffs/`. El estado corto vive en `context/LAST_HANDOFF.md`.
- [docs/handoffs/archive](archive): memoria comprimida CON consumidor -- ocho notas
  de decisiones (julio 2026) citadas por nombre desde `context/LAST_HANDOFF.md`
  o `CLAUDE.md`. Los ~93 checkpoints de version que vivian aqui (`HANDOFF_v0.4x.md`,
  `HOTFIX_*.md`, snapshots 2026-06-16 a 2026-06-30 en las subcarpetas `root/` y
  `handoffs/`) se retiraron el 2026-07-30: cero citas reales, git ya guarda esa
  historia completa (`git log`, `git show`).

## Regla

No dejes nuevos `HANDOFF_*.md` o `HOTFIX_*.md` historicos en la raiz del repo salvo que sean parte temporal de un airdrop por aplicar. Despues de integrarlos, archivarlos aqui y actualizar `context/LAST_HANDOFF.md`.

Cuando un handoff de nivel raiz de esta carpeta deje de ser "de la semana en curso" (referencia puntual reciente), muevelo a `archive/handoffs/`. No lo dejes acumularse suelto: la raiz de `docs/handoffs/` debe tener siempre pocos archivos (idealmente <5), no un indice historico completo.
