#!/usr/bin/env bash
set -e

NAME="$1"

if [ -z "$NAME" ]; then
  echo "Uso: bash scripts/new_flyer_evento.sh \"nombre del evento\""
  exit 1
fi

SAFE_NAME=$(echo "$NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-//' | sed 's/-$//')
DATE=$(date +%Y-%m-%d)

DIR="projects/flyer_eventos/${DATE}_${SAFE_NAME}"

mkdir -p \
  "$DIR/input" \
  "$DIR/working" \
  "$DIR/exports" \
  "$DIR/refs" \
  "$DIR/analysis" \
  "$DIR/ai"

touch "$DIR/input/.gitkeep"
touch "$DIR/working/.gitkeep"
touch "$DIR/exports/.gitkeep"
touch "$DIR/refs/.gitkeep"
touch "$DIR/analysis/.gitkeep"
touch "$DIR/ai/.gitkeep"

cat > "$DIR/manifest.json" <<EOC
{
  "tool": "flyer_eventos",
  "name": "$NAME",
  "date": "$DATE",
  "status": "created",
  "input": {
    "main_image": "",
    "event_name": "$NAME",
    "event_date": "",
    "format": "",
    "notes": ""
  },
  "steps": {
    "photoshop": "pending",
    "blender": "pending",
    "export": "pending"
  },
  "outputs": []
}
EOC

cat > "$DIR/README.md" <<EOC
# Flyer evento — $NAME

Fecha: $DATE

## Objetivo

Crear flyer para evento.

## Inputs

- Imagen principal:
- Fecha evento:
- Formato:
- Notas:

## Carpetas

- \`input/\`: imagen/video base.
- \`working/\`: archivos intermedios.
- \`exports/\`: salidas finales o previews.
- \`refs/\`: referencias.
- \`analysis/\`: OCR, colores, metadata, reportes.
- \`ai/\`: contexto y prompts para IA.

## Flujo

1. Poner imagen base en \`input/\`.
2. Analizar o completar datos si hace falta.
3. Procesar en Photoshop.
4. Exportar JPG a \`working/\`.
5. Usar en Blender.
6. Export final en \`exports/\`.

## Estado

- [ ] Input listo
- [ ] Análisis
- [ ] Photoshop
- [ ] Blender
- [ ] Export final
EOC

echo "Proyecto creado en: $DIR"
