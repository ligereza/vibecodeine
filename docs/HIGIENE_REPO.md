# Higiene del repo

Versión: v0.51.0

## Política

El repo debe mantenerse útil para trabajo real y legible para agentes. No debe convertirse en un basurero de outputs, caches o pruebas locales.

Ejecuta `py scripts/suggest_repo_hygiene.py` (100% no destructivo) + terminal safe rm SOLO generados (pycache/.pytest_cache) para ver sugerencias actualizadas del estado actual. Siempre empieza por `flujo app` + hub + LAST_HANDOFF (reinforces resumption and speeds daily designer flow: pedido → `flujo app`/hub → real actions/visualizers → export). **Punto de entrada: `flujo app` (lanza app real + hub) → usa hub + lee context/LAST_HANDOFF.md.**

## Nunca commitear

- `_airdrop/`, `_airdrop_backups/`, `_logs/`
- `__pycache__/`, `*.pyc`
- `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`
- `*.egg-info/` nuevos
- `data/*.db`, `*.sqlite*`
- `context/DAILY.md`, `context/dashboard.html`
- `projects/**/salida_generada/`
- medios pesados descargados: `*.mp4`, `*.mov`, `*.mkv`, `*.psd`, `*.ai`, `*.zip`
- `jobs/20*` y `projects/piezas_vectoriales/20*` de pruebas/demo (jobs reales fechados no deberían commitearse; `jobs/_template/` sí se versiona)

Ejemplos intencionales que SÍ se mantienen versionados: `etiquetas_ejemplo`, `flyer_horizontal_minimo`, `plantillas_rd`, `prueba-rd-intervencion-terreno`, `rider_rd_intervencion_terreno`, `suplementos_rd`.

## Antes de checkpoint

```bash
git status --short
py -m compileall -q src scripts tests
py -m pytest tests/ -q
py -m flujo health
```

Limpieza de generados/caches (equivalente, dos formas vivas):

```bash
flujo clean --generated       # via CLI Typer
py scripts/flujo_clean_generated.py   # script directo (pycache + outputs regenerables de piezas_vectoriales)
py scripts/flujo_health.py            # chequeo directo (usado tambien por .github/workflows/render_piezas_vectoriales.yml)
bash scripts/cleanup_demo_artifacts.sh --dry-run
bash scripts/cleanup_demo_artifacts.sh --apply   # elimina jobs/projects de demo listados arriba + caches + backups airdrop
```

## Antes de aceptar un airdrop externo

```bash
py scripts/validate_airdrop.py
py scripts/run_airdrop_checks.py "mensaje"
```

Ver `docs/AGENT_AIRDROP_PROTOCOL.md` para el detalle completo (que valida, que hace el runner paso a paso, flags).

## Deuda conocida

- `projects/tapiz/vibecode.egg-info/` está trackeado históricamente.
- Historial de commits de v0.34 con tareas parciales/fallidas fue consolidado (ver CLAUDE.md, seccion "Mapa del repo"; el viejo REPO_MAP.md fue archivado).
- checkpoints/ y docs/handoffs/ se mantienen como bitácora (no agregar commits ruidosos de micro-tareas).
- Se recomienda correr git filter-repo para reducir tamaño del .git (ver docs/LIMPIEZA_HISTORIAL.md).

**Actual (2026-06):** `context/flujo_hub.html` + `svg_visualizer.html` + `plano_demo.html` + `LAST_HANDOFF.md` son la fuente de verdad diaria.

Histórico (checkpoints, _archive, reference_old) movido a `.archive/`. Mantener el root limpio. Ver `.archive/README.md` y `CLAUDE.md` (mapa del repo).
