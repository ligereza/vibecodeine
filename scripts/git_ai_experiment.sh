#!/usr/bin/env bash
set -e

NAME="$1"
if [ -z "$NAME" ]; then
  echo "Uso: bash scripts/git_ai_experiment.sh \"nombre-proyecto-o-experimento\""
  exit 1
fi

SAFE_NAME=$(echo "$NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-//' | sed 's/-$//')
DATE=$(date +%Y-%m-%d_%H-%M)
BRANCH="ai-optimizacion/${SAFE_NAME}-${DATE}"
CHECKPOINT="checkpoints/${DATE}_antes-ia-avanzada-${SAFE_NAME}.md"

if [ ! -d .git ]; then
  echo "No existe .git. Ejecuta primero: bash scripts/setup_repo.sh"
  exit 1
fi

mkdir -p checkpoints

cat > "$CHECKPOINT" <<EOC
# Checkpoint — Antes de IA avanzada: $NAME

Fecha: $DATE

## Objetivo del experimento

Usar una IA más poderosa/moderna para analizar contexto, composición o flujo y proponer optimizaciones sin perder la versión actual.

## Estado antes del cambio

[Describir versión actual]

## Archivos/previews enviados a IA

- 

## Qué NO debe cambiar

- 

## Qué se busca mejorar

- 

## Link o nombre del chat usado

- 

## Resultado esperado

- Diagnóstico
- Cambios conservadores
- Cambios ambiciosos
- Checklist antes/después

## Decisión final

- [ ] Pendiente
- [ ] Se aplicó
- [ ] Se descartó
- [ ] Quedó a medias
EOC

# Guardar estado actual antes de rama
git add -A
if git diff --cached --quiet; then
  echo "No hay cambios pendientes antes de crear branch."
else
  git commit -m "checkpoint: antes de IA avanzada $NAME"
fi

git checkout -b "$BRANCH"

echo "Creado checkpoint: $CHECKPOINT"
echo "Creada y activada rama experimental: $BRANCH"
echo "Ahora prepara el paquete para IA avanzada y trabaja aquí."
echo "Para volver a main: git checkout main"
