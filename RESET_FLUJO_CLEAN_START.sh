#!/usr/bin/env bash
set -e

cat <<'MSG'
============================================================
 RESET LIMPIO PARA REPO flujo
============================================================
Este script debe ejecutarse dentro del repo clonado `flujo`.

Hace:
1. Crea rama backup con el estado actual.
2. Borra archivos/carpetas conocidos del sistema viejo/portfolio.
3. Crea estructura mínima limpia.
4. Hace commit.
5. Opcionalmente hace push.

NO ejecutes si tienes cambios sin guardar que no quieras respaldar.
MSG

read -r -p "¿Continuar? escribe SI: " OK
if [ "$OK" != "SI" ]; then
  echo "Cancelado."
  exit 0
fi

if [ ! -d .git ]; then
  echo "ERROR: ejecuta esto dentro del repo clonado de Git."
  exit 1
fi

DATE=$(date +%Y-%m-%d_%H-%M)
BACKUP="backup/antes-clean-start-$DATE"

git add -A
if ! git diff --cached --quiet; then
  git commit -m "backup: antes de clean start $DATE"
fi

git branch "$BACKUP" || true
echo "Backup creado: $BACKUP"

# Borrar contenido viejo conocido, manteniendo .git
rm -rf assets css data docs js logs projects prompts scripts checkpoints context inbox reference_files _relay_sessions _ai_share_pack
rm -f 2d.html 3d-immersion.html 404.html CURATOR.html README-AGENTS.txt README.md START_HERE_GITBASH.sh START_SIMPLE.md _headers _routes.json about.html index.html manifest.json obra.html package.json robots.txt sitemap.xml wrangler.jsonc

mkdir -p context checkpoints tools/flyer_eventos tools/slowmo_blender_ae tools/asistente_pedido tools/canva_data scripts

cat > README.md <<'EOC'
# flujo — sistema limpio de automatización diseño/motion + IA

Repositorio mínimo para construir herramientas desde cero, sin arrastrar archivos viejos.

## Herramientas objetivo

1. `flyer_eventos`: asset/foto → Photoshop → Blender → export para jefe.
2. `slowmo_blender_ae`: Blender → rangos slowmo → After Effects → consolidación segura.
3. `asistente_pedido`: pedido del jefe → plan de producción.
4. `canva_data`: CSV/JSON para Canva/Illustrator.

## Uso

```bash
bash scripts/checkpoint.sh "mensaje"
```
EOC

cat > context/ESTADO.md <<'EOC'
# Estado del proyecto

Última actualización: 2026-06-12

## Objetivo actual

Empezar desde cero un repo limpio para construir herramientas de automatización de diseño/motion + IA.

## Herramientas a construir

1. Flyer eventos.
2. Slowmo Blender/After Effects.
3. Asistente pedido del jefe.
4. Canva/JSON.

## Regla

No importar scripts viejos todavía. Solo usarlos como referencia manual si hace falta.

## Próximo paso

Elegir primera herramienta mínima: `flyer_eventos` o `slowmo_blender_ae`.
EOC

cat > tools/flyer_eventos/SPEC.md <<'EOC'
# Herramienta — flyer_eventos

Estado: diseño desde cero

## Objetivo

asset/foto de evento > preparación > Photoshop > JPG > Blender > composición 3D > export para jefe.

## Primera versión mínima

Crear estructura de carpetas + manifest por flyer. No automatizar Photoshop/Blender todavía.
EOC

cat > tools/slowmo_blender_ae/SPEC.md <<'EOC'
# Herramienta — slowmo_blender_ae

Estado: diseño desde cero

## Objetivo

Hacer seguro el flujo slowmo Blender > After Effects.

## Primera versión mínima

Validador dry-run. No borrar frames. Nunca eliminar sin confirmación.
EOC

cat > tools/asistente_pedido/SPEC.md <<'EOC'
# Herramienta — asistente_pedido

Estado: diseño desde cero

## Objetivo

Pedido del jefe > plan de producción claro.
EOC

cat > tools/canva_data/SPEC.md <<'EOC'
# Herramienta — canva_data

Estado: diseño desde cero

## Objetivo

Generar CSV/JSON limpio para Canva o Illustrator.
EOC

cat > scripts/checkpoint.sh <<'EOC'
#!/usr/bin/env bash
set -e
MSG="$1"
if [ -z "$MSG" ]; then MSG="avance $(date +%Y-%m-%d_%H-%M)"; fi
mkdir -p checkpoints
DATE=$(date +%Y-%m-%d_%H-%M)
SAFE=$(echo "$MSG" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-//' | sed 's/-$//')
CP="checkpoints/${DATE}_${SAFE}.md"
cat > "$CP" <<EOF2
# Checkpoint — $MSG

Fecha: $DATE

## Estado

$(cat context/ESTADO.md 2>/dev/null || echo "Sin context/ESTADO.md")

## Cambios realizados

- 

## Próximo paso

- 
EOF2
git add -A
if git diff --cached --quiet; then echo "No hay cambios"; else git commit -m "checkpoint: $MSG"; fi
if git remote get-url origin >/dev/null 2>&1; then git push -u origin main; fi
EOC
chmod +x scripts/checkpoint.sh

cat > .gitignore <<'EOC'
.DS_Store
Thumbs.db
.env
*.key
*.pem
credentials.json
token.json
*.psd
*.psb
*.ai
*.indd
*.aep
*.blend
*.exr
*.tif
*.tiff
*.mp4
*.mov
*.avi
*.mkv
*.zip
*.rar
*.7z
_local/
_originales/
_exports_pesados/
_quarantine_frames/
EOC

bash scripts/checkpoint.sh "clean start"

echo ""
echo "Listo. Backup: $BACKUP"
echo "Si quieres subir backup también: git push origin $BACKUP"
echo "Main limpio subido si origin existe."
