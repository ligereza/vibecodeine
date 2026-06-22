# 🤖 Contexto para IA (Handover Document)

**Estado del Proyecto:** flujo v0.34.10
**Fecha de última actualización:** 2026-06-22

## 👉 Empieza por aquí

Lee en este orden, sin saltarte pasos:

1. `README.md`
2. `PARA_IA_CONTEXT.md`
3. `docs/AGENT_GUIDE.md`
4. `docs/CLI.md`
5. `docs/REPO_MAP.md`
6. `docs/SCRIPTS_INVENTORY.md`

Después clona el repo actual desde GitHub en una carpeta limpia y verifica el
estado real con:

```bash
py -m pip install -e ".[dev]"
py -m compileall -q src scripts tests
py -m pytest tests/ -q --tb=short
py -m flujo health
py -m flujo version
```

En Linux/macOS puedes usar `python3` o `python` en vez de `py`.

## 🛠️ Cambios recientes

- **v0.34.10:** hotfix del runner de airdrops: evita que `scripts/flujo.py` sombree al paquete `src/flujo` cuando se ejecuta `py scripts/run_airdrop_checks.py`.
- **v0.34.9:** sincronización de documentación para agentes: este contexto,
  `docs/AGENT_GUIDE.md`, `docs/CLI.md`, README y changelog quedan alineados con
  el estado actual.
- **v0.34.8:** confiabilidad de airdrop y base universal: rollback con manifest
  (`REPLACE` se restaura, `NEW` se elimina), `flujo airdrop apply` valida antes
  de aplicar, alias real `flujo app`, base universal con `json.dumps`, setup más
  portable y parser YAML fallback con listas escalares.
- **v0.34.7:** runner de airdrop compatible con Windows/Git Bash, sin invocar
  bash internamente para apply/checkpoint.
- **v0.34.6:** mapa del repo e higiene estructural.
- **v0.34.5:** guardrails de airdrop, validador y logs de error.

## 🔑 Cómo entregas tu trabajo

NO tienes push. Entregas un **ZIP** con carpeta `_airdrop/` que replica la
estructura final del repo, sin subcarpetas de versión. Incluye siempre:

- `HANDOFF_<fecha>.md` o `HOTFIX_<fecha>.md`
- cambios en sus rutas reales dentro de `_airdrop/`
- tests para la lógica nueva
- versión bumpeada en `src/flujo/version.py` y `pyproject.toml`
- changelog en `src/flujo/version.py`
- documentación relevante actualizada

Validación recomendada antes de aplicar:

```bash
py scripts/validate_airdrop.py
py scripts/run_airdrop_checks.py "vX.Y.Z - descripcion"
```

Si el airdrop toca `src/flujo/airdrop.py`, requiere revisión explícita:

```bash
py scripts/validate_airdrop.py --allow-airdrop-engine
py scripts/run_airdrop_checks.py "vX.Y.Z - descripcion" --allow-airdrop-engine
```

## ⚠️ Reglas innegociables

1. **Instagram:** solo `instaloader`. Prohibido `yt-dlp`.
2. **Entorno:** sin venvs pesados; usar `py` / `python3`.
3. **Privacidad:** `flujo privacy` antes de mandar datos a IAs externas.
4. **Checkpoints:** cada avance commiteado y pusheado, sin mensajes vacíos.
5. **Borrado:** no destructivo; usar scripts de limpieza seguros o documentar
   claramente el movimiento a `_archive/`.
6. **Lógica nueva:** en `src/flujo/`, con tests.

## 🗺️ Pipeline actual

Pedido (correo / JSON) → Privacy Scan → Brief → Job → Proyecto (`config.json` +
plantilla de formato) → Render → Export ZIP.

## 🚧 Próximos pasos

1. Implementar `flujo intake json <archivo>` que consuma `schemas/intake.schema.json`.
2. Decidir canal de recepción automática: poller IMAP, formulario web/API o
   webhook de mensajería.
3. Mantener sincronizada la documentación operativa después de cada airdrop.
