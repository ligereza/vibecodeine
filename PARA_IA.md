# PARA IA

Este repo se llama **flujo** — arte y automatización. v0.34.7.

Lee primero: `docs/AGENT_GUIDE.md` y `docs/CLI.md`.

Resumen rápido:

```bash
flujo version
flujo health
flujo flyer-import inbox/correo.txt
flujo analyze
flujo job new "pedido" --email inbox/correo.txt
flujo job prepare jobs/<job>
flujo job activate jobs/<job>
flujo render run projects/piezas_vectoriales/<proyecto>/config.json
flujo daily

# Planos de stands (proyecto satélite plano)
flujo plano projects/plano/ejemplos/evento_ejemplo.json
flujo plano projects/plano/ejemplos/evento_ejemplo.json --rider
flujo plano projects/plano/ejemplos/evento_ejemplo.json --costs
```

Herramienta activa: `flyer_eventos` — descarga Instagram con **instaloader únicamente**.
Análisis automático: colores dominantes + OCR → `analysis/`
Privacidad: `flujo privacy` antes de enviar texto a IAs externas.

Documentación completa en `docs/AGENT_GUIDE.md`, `docs/CLI.md`, `docs/JOB_PIPELINE.md`,
`README.md`, `context/ESTADO.md`, `docs/RELEASE_v016.md`.

**No uses yt-dlp. No crees venvs pesados. Usa `py`.**

## Airdrops: validación obligatoria

Antes de aplicar cualquier entrega externa:

```bash
py scripts/validate_airdrop.py
py scripts/run_airdrop_checks.py "vX.Y.Z - descripcion"
```

Los errores quedan en `_logs/airdrop_error_*.txt` para compartirlos sin deformación de la web.

## Mapa antes de tocar

Antes de modificar archivos, lee `docs/REPO_MAP.md` y `docs/SCRIPTS_INVENTORY.md`. No uses `_archive/`, `reference_old/` ni checkpoints como fuente primaria salvo que el dueño lo pida explícitamente.
