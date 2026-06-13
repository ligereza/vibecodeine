#!/usr/bin/env bash
set -e

NAME="$1"
if [ -z "$NAME" ]; then
  echo "Uso: bash scripts/new_checkpoint.sh \"nombre del checkpoint\""
  exit 1
fi

SAFE_NAME=$(echo "$NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-//' | sed 's/-$//')
DATE=$(date +%Y-%m-%d_%H-%M)
FILE="checkpoints/${DATE}_${SAFE_NAME}.md"

mkdir -p checkpoints

cat > "$FILE" <<EOC
# Checkpoint — $NAME

Fecha: $DATE

## Resumen corto

[Escribe aquí el resumen del avance]

## Objetivo del checkpoint

[Qué estabas intentando lograr]

## Estado actual

- [ ] Pendiente describir estado.

## Qué funcionó

- 

## Qué quedó a medias

- 

## Caminos probados

### Camino 1

- Resultado:
- Problema:
- Próximo paso:

## Archivos importantes

- 

## Decisiones tomadas

- 

## Próximo paso recomendado para una IA

1. 
2. 
3. 

## Prompt para continuar desde aquí

\`\`\`md
Continúa desde este checkpoint. Primero resume el estado actual, luego identifica bloqueos y propón el siguiente paso concreto. No empieces desde cero.
\`\`\`
EOC

echo "Creado: $FILE"
