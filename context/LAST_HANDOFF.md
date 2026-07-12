# LAST HANDOFF -- estado para el proximo agente

Version: 0.51.0 | Fecha: 2026-07-12 | Identidad: Cauce | Suite: verde | flujo verify: OK

El plan detallado del proximo paso vive en context/PLAN_SIGUIENTE_AGENTE.md. Este
archivo es el estado corto; ese es el mapa de trabajo. El historico de sesiones
viejas quedo en git y en docs/handoffs/archive/ (no se pierde, no ensucia aca).

## Hecho (esta sesion, 2026-07-12)
- Fold telar -> loom: sistema de motivos-plugin, 20 motivos de alfombra
  (projects/tapiz/vibecode/loom.py + motifs/). PRs #39, #40 merged. telar.py
  duplicado eliminado.
- Pieza Tilde honesta desde semilla puente (+)3 via protocolo motor-omega:
  projects/cultura/tilde_residuo.py (+ TILDE_RESIDUO.md + tests). Residuo (+)5
  registrado en puente/SEMILLAS.md. PR #41 abierto (pendiente de merge).
- Portfolio auto verificado LIVE: https://ligereza.github.io/portfolio-auto/
  (sin Claude API; PORTFOLIO_TOKEN seteado). No requiere trabajo.
- Limpieza general: handoffs viejos/confusos archivados, junk generado, drift
  de docs. puente/ marcado como TEORICO (puente/README.md nuevo).

## Doing / Next
- Leer context/PLAN_SIGUIENTE_AGENTE.md (prioridades 1-3).
- Inmediato: merge PR #41; limpieza git de worktrees y ramas stale (hilo
  principal, no delegado a subagentes).

## Blockers
- (+)2 (OBRA_02) bloqueada esperando lector humano.
- #2 duelo de modelos: Gemini PARKED, falta un 2do modelo util.
- build_chataigne_noisette_experimental: falta .noisette real (NO re-adivinar).

## Reglas vivas (no negociar)
- NO activar Claude via API en Actions (decision usuario 2026-07-12).
- El airdrop QUEDA COMO ESTA (canal de agentes web sin acceso a GitHub). No
  borrar, no extender.
- puente/ es teorico (ver puente/README.md): no ejecutar, no limpiar, no
  reinterpretar lo fechado.
- README.md del repo: obra terminada, no agregar nada.
- context/AVANCES_BLOCK.txt NO es doc muerto: es input de tools/tapiz_telemetry.py
  (su desfase de version alimenta un asset de arte psicosis). No borrar ni
  "refrescar" sin decision explicita.
- psicosis jamas perfila personas reales; precursor solo cultura/ley/estetica.
- Ordenes destructivas de git van al hilo principal, no a subagentes.
- Nunca versionar secretos (.env, config.json, *.key). CLAUDE.md y este archivo:
  ASCII-only.

## Verificacion (antes de cerrar)
- py -m compileall src/flujo
- py -m pytest tests/ -q
- py -m flujo verify
- (si tocas web) cd web && npm run typecheck && npm run build:context

## Entrada
1. Este archivo. 2. context/PLAN_SIGUIENTE_AGENTE.md. 3. CLAUDE.md.
