# Protocolo operativo de airdrop para agentes

Este documento es la regla base para integrar trabajo de agentes sin push directo.

## Principio

Un agente no pega archivos sueltos ni instrucciones ambiguas. Un agente entrega un ZIP con `_airdrop/` en la raiz. Esa carpeta replica rutas finales del repo.

## Estructura correcta

```txt
_airdrop/HANDOFF_2026-06-30_descripcion.md
_airdrop/context/LAST_HANDOFF.md
_airdrop/src/flujo/ejemplo.py
_airdrop/tests/test_ejemplo.py
_airdrop/docs/ejemplo.md
```

## Estructura incorrecta

```txt
airdrop/
_airdrop/_airdrop/
v0.48/_airdrop/
src/flujo/ejemplo.py fuera de _airdrop
archivos como enlaces Markdown en vez de archivos reales
```

## Contenido obligatorio

Cada airdrop debe traer:

1. `HANDOFF_*.md` o `HOTFIX_*.md`.
2. `context/LAST_HANDOFF.md` actualizado en ASCII-only.
3. Archivos reales en rutas finales del repo.
4. Verificacion reportada.
5. Lista de archivos del ZIP.

## Prohibido

```txt
__pycache__/
.pytest_cache/
node_modules/
dist/
build/
_airdrop_backups/
_logs/
*.zip dentro del airdrop
*.db
credenciales
tokens
cookies
archivos pesados reales
_delete.txt
delete.txt
```

Prohibido tocar `src/flujo/airdrop.py` salvo autorizacion explicita del usuario.

## Validacion y apply

Desde raiz del repo en Windows/Git Bash:

```bash
py scripts/validate_airdrop.py
py scripts/run_airdrop_checks.py "mensaje corto"
```

Si ya aplico cambios pero fallo despues:

```bash
py scripts/run_airdrop_checks.py --resume "mensaje corto"
```

Si el usuario autorizo tocar motor de airdrop:

```bash
py scripts/validate_airdrop.py --allow-airdrop-engine
py scripts/run_airdrop_checks.py "mensaje corto" --allow-airdrop-engine
```

## Que valida `scripts/validate_airdrop.py`

- `_airdrop/` existe y contiene archivos reales, no solo carpetas vacias.
- No hay archivos de 0 bytes.
- Incluye un `HANDOFF_*.md` o `HOTFIX_*.md`.
- No incluye caches, `.egg-info`, bases de datos, medios pesados, ZIPs ni outputs generados.
- No incluye `_delete.txt`.
- No toca `src/flujo/airdrop.py` salvo autorizacion explicita con `--allow-airdrop-engine`.
- Detecta rutas deformadas por Markdown/autolink como `[archivo.py](http...)`.

## Que hace el runner (`scripts/run_airdrop_checks.py`, orden real verificado v0.52.0 (2026-07-16))

1. `validate_airdrop` (motor Python `flujo.airdrop`, no bash).
2. `airdrop dry-run` (`flujo.airdrop.scan_airdrop()`).
3. `airdrop apply` (`flujo.airdrop.apply_airdrop()`), con backup/manifest.
4. `pip install -e ".[dev]"`.
5. `compileall -q src scripts tests`.
6. `pytest tests/ -q`.
7. `flujo health`.
8. `flujo version` + chequeo `get_version() in get_changelog()`.
9. `scripts/hub_smoke.py` (salvo `--skip-hub-smoke`).
10. `flujo.airdrop.run_auto_checkpoint()`: git add -A, commit, push (salvo `--skip-checkpoint` / `--skip-push`).

Si un paso falla, se detiene y escribe un log en `_logs/airdrop_error_*.txt`; no se hace checkpoint si compileall, pytest, health, version o el chequeo de changelog fallan.

Flags utiles: `--resume` (salta validate/dry-run/apply, corre checks+checkpoint tras un apply manual previo), `--skip-hub-smoke`, `--skip-checkpoint`, `--skip-push`.

Nota Windows/Git Bash: el runner es Python puro; no invoca `bash` internamente para apply/checkpoint (a diferencia de versiones muy antiguas de este doc que mencionaban `apply_airdrop.sh`/`checkpoint.sh`).

## Regla de fallo

Si algo falla, no declarar exito. Reportar:

```txt
comando ejecutado
codigo de salida
error exacto
archivo de log si existe
```

## Limpieza despues de aplicar

```bash
rm -rf _airdrop
find . -type d -name "__pycache__" -prune -exec rm -rf {} +
rm -rf .pytest_cache
git status --short
git log --oneline -5
```

## Canal sin PC: airdrop-gate (verificado en codigo 2026-07-16, estreno pendiente)

El mismo ZIP del protocolo se puede entregar SIN PC. El gate corre entero en
GitHub Actions (.github/workflows/airdrop_gate.yml); el que entrega solo
dispara:

- Desde el Xiaomi (xio, Termux): `bash xio/new/airdrop_push.sh entrega.zip "mensaje"`
  (requiere `pkg install gh` + token fine-grained solo-este-repo en
  `$HOME/.airdrop_token`, chmod 600; NUNCA en /sdcard ni en el env del server).
- Desde el iPhone con la app de GitHub (fallback manual, sin PC): crear un
  Release con tag `airdrop-...` y adjuntar el ZIP; la misma app sirve luego
  para revisar el diff y mergear el PR que abre el gate. Cualquier navegador
  tambien vale.

El workflow: descarga el ZIP del release, aplica guardas (sin rutas absolutas
ni traversal; rechaza ZIPs que toquen `.github/` o `src/flujo/airdrop.py` --
ese cambio requiere PC y revision explicita), extrae `_airdrop/`, corre
`run_airdrop_checks.py --skip-push` (validate + apply + suite completa) y si
queda verde abre un PR `airdrop/<tag>` listo para mergear desde el telefono.
Rojo = nada se aplico a main; el log queda en el run de Actions.
