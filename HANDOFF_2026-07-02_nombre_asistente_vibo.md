# HANDOFF 2026-07-02 - nombre propio del asistente: Vibo

## Problema resuelto

El usuario pidio un nombre distinto de "Claude" para dirigirse al asistente.
Se creo la identidad "Vibo" (derivado de "vibecodeine") y se dejo persistida
en el repo para que sobreviva entre sesiones y aplique a cualquier agente.

## Archivos modificados

- `CLAUDE.md` (NUEVO, raiz): definicion canonica del nombre + arranque rapido.
  Claude Code carga este archivo automaticamente al iniciar cada sesion.
- `AGENTS.md`: nueva seccion "Identidad del asistente" para que agentes
  no-Claude tambien respeten el nombre.
- `context/LAST_HANDOFF.md`: actualizado a 2026-07-02 con este cambio.
- `context/SESSION_STATE.json`: fecha 2026-07-02 + entrada en done.
- `HANDOFF_2026-07-02_nombre_asistente_vibo.md` (este archivo).

## Como cambiar el nombre en el futuro

Editar la seccion "Identidad del asistente" en `CLAUDE.md` y en `AGENTS.md`
en el mismo cambio (ambos archivos deben coincidir).

## Riesgos o pendientes reales

- Ninguno funcional: cambio docs-only, no toca codigo ni build.
- El push directo desde la sesion remota fallo con 403 (acceso de solo
  lectura al repo). Por eso esta entrega va por airdrop segun protocolo.
  El commit local existe en la rama claude/custom-name-preference-543qs0
  del contenedor, pero el contenedor es efimero: aplicar este airdrop es
  la via real de entrega.

## Comandos de uso

```bash
py scripts/validate_airdrop.py
py scripts/run_airdrop_checks.py "docs: nombre propio del asistente (Vibo)"
```

## Reporte Formal de Verificacion y Tolerancia Cero a Errores

- py -m compileall src/flujo: no aplica (docs-only, cero archivos Python tocados)
- py -m pytest tests/ -q: no aplica (docs-only)
- cd web && npm run build:context: no aplica (docs-only)
- py -m flujo verify: no aplica (docs-only)
- Observaciones: context/SESSION_STATE.json validado como JSON (json.load OK);
  CLAUDE.md y context/LAST_HANDOFF.md verificados ASCII-only byte a byte;
  scripts/validate_airdrop.py ejecutado sobre _airdrop/ con resultado OK.
