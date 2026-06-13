#!/usr/bin/env bash
set -e

OUT="_ai_share_pack"
DATE=$(date +%Y-%m-%d_%H-%M)

rm -rf "$OUT"
mkdir -p "$OUT/checkpoints" "$OUT/prompts" "$OUT/docs" "$OUT/context"

copy_if_exists() {
  SRC="$1"
  DEST="$2"
  if [ -f "$SRC" ]; then
    cp "$SRC" "$DEST"
  fi
}

copy_if_exists "context/MASTER_CONTEXT.md" "$OUT/context/MASTER_CONTEXT.md"
copy_if_exists "context/TOOLS_INVENTORY.md" "$OUT/context/TOOLS_INVENTORY.md"
copy_if_exists "docs/PRODUCCION_TECNICA.md" "$OUT/docs/PRODUCCION_TECNICA.md"
copy_if_exists "docs/FLUJOS_ASISTENTES_AGENTES.md" "$OUT/docs/FLUJOS_ASISTENTES_AGENTES.md"
copy_if_exists "docs/FLUJO_IA_AVANZADA_OPTIMIZACION.md" "$OUT/docs/FLUJO_IA_AVANZADA_OPTIMIZACION.md"
copy_if_exists "docs/COMPARTIR_REPO_CON_IA.md" "$OUT/docs/COMPARTIR_REPO_CON_IA.md"
copy_if_exists "prompts/continuar_desde_checkpoint.md" "$OUT/prompts/continuar_desde_checkpoint.md"
copy_if_exists "prompts/asistente_pedido_jefe.md" "$OUT/prompts/asistente_pedido_jefe.md"
copy_if_exists "prompts/ia_avanzada_optimizacion_composicion.md" "$OUT/prompts/ia_avanzada_optimizacion_composicion.md"

# Copiar últimos 5 checkpoints por nombre/fecha
if [ -d checkpoints ]; then
  ls -1 checkpoints/*.md 2>/dev/null | sort | tail -n 5 | while read -r f; do
    cp "$f" "$OUT/checkpoints/"
  done
fi

cat > "$OUT/README_PARA_IA.md" <<EOC
# README para IA — Paquete de contexto

Fecha de generación: $DATE

Este paquete contiene una versión reducida del sistema de checkpoints para diseño gráfico + automatización + múltiples IAs.

## Instrucciones para la IA

1. Lee primero \\`context/MASTER_CONTEXT.md\\`.
2. Luego lee \\`context/TOOLS_INVENTORY.md\\`.
3. Revisa los documentos en \\`docs/\\`.
4. Revisa el checkpoint más reciente en \\`checkpoints/\\`.
5. No empieces desde cero.
6. Resume el estado actual.
7. Identifica lo que quedó a medias.
8. Propón el siguiente paso concreto.

## Pregunta base

Continúa este proyecto como productor técnico. Necesito avanzar de forma ordenada, separando asistentes, agentes, automatizaciones y checkpoints.
EOC

cat > "$OUT/PROMPT_COPIAR_PEGAR.md" <<'EOC'
# Prompt para copiar y pegar en un chat IA

Te comparto un paquete de contexto de mi sistema de trabajo como diseñador gráfico/motion con automatizaciones e IA.

Necesito que actúes como productor técnico del proyecto.

Instrucciones:

1. Lee los archivos adjuntos o el contenido que te pegue.
2. No empieces desde cero.
3. Resume el estado actual en máximo 10 bullets.
4. Identifica lo que quedó a medias.
5. Separa asistentes de agentes.
6. Propón el siguiente paso mínimo y accionable.
7. Si propones scripts, deben tener modo dry-run antes de tocar archivos reales.
8. Si falta información crítica, pregunta antes de avanzar.

Prioridad de lectura:

1. MASTER_CONTEXT.md
2. TOOLS_INVENTORY.md
3. PRODUCCION_TECNICA.md
4. FLUJOS_ASISTENTES_AGENTES.md
5. FLUJO_IA_AVANZADA_OPTIMIZACION.md
6. checkpoint más reciente
EOC

echo "Paquete para IA creado en: $OUT"

# Crear zip si existe zip instalado
if command -v zip >/dev/null 2>&1; then
  ZIP_NAME="ai_share_pack_${DATE}.zip"
  rm -f "$ZIP_NAME"
  zip -qr "$ZIP_NAME" "$OUT"
  echo "ZIP creado: $ZIP_NAME"
else
  echo "No se encontró comando zip. Puedes comprimir manualmente la carpeta $OUT."
fi

echo "Revisa el paquete antes de subirlo a cualquier IA."
