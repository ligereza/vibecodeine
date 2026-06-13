#!/usr/bin/env bash
set -e

NAME="$1"
if [ -z "$NAME" ]; then
  echo "Uso: bash scripts/start_ai_relay.sh \"nombre del caso\""
  exit 1
fi

SAFE_NAME=$(echo "$NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-//' | sed 's/-$//')
DATE=$(date +%Y-%m-%d_%H-%M)
DIR="_relay_sessions/${DATE}_${SAFE_NAME}"
mkdir -p "$DIR"

cat > "$DIR/README.md" <<EOC
# Relay IA — $NAME

Fecha: $DATE

## Uso

1. Completa `00_SHARED_CONTEXT.md`.
2. Pega `01_CHAT_A_DIRECTOR_PROMPT.md` en Chat A.
3. Guarda la respuesta en `03_RESPONSE_CHAT_A.md`.
4. Pega `02_CHAT_B_SPECIALIST_PROMPT.md` + respuesta A en Chat B.
5. Guarda la respuesta en `04_RESPONSE_CHAT_B.md`.
6. Completa `05_SYNTHESIS.md`.
7. Haz checkpoint.

## Regla

Cada chat tiene un rol. No repetir contexto completo si no hace falta.
EOC

cat > "$DIR/00_SHARED_CONTEXT.md" <<'EOC'
# Contexto compartido

## Proyecto/caso

## Objetivo

## Estado actual

## Archivos o links relevantes

## Qué quiero mejorar

## Restricciones

## Qué NO debe cambiar

## Pregunta principal
EOC

cat > "$DIR/01_CHAT_A_DIRECTOR_PROMPT.md" <<'EOC'
# Prompt Chat A — Director técnico

Actúa como productor técnico/director de flujo para diseño gráfico, motion, automatización e IA.

Te daré un contexto compartido. Tu tarea es entender el problema y preparar un paquete para que otro chat especialista pueda trabajar sin preguntarme todo de nuevo.

## Tareas

1. Resume el estado actual.
2. Detecta qué falta o qué está ambiguo.
3. Propón plan en pasos.
4. Define qué debería revisar Chat B.
5. Genera un paquete breve para Chat B.

## Formato

### Estado actual
### Problemas o huecos
### Plan recomendado
### Tarea exacta para Chat B
### Paquete para Chat B
### Preguntas para el humano

## Contexto

[PEGAR 00_SHARED_CONTEXT.md]
EOC

cat > "$DIR/02_CHAT_B_SPECIALIST_PROMPT.md" <<'EOC'
# Prompt Chat B — Especialista

Actúa como especialista crítico. No empieces desde cero: trabaja desde el paquete preparado por Chat A.

## Tu tarea

1. Revisar el diagnóstico de Chat A.
2. Detectar errores, riesgos o mejoras.
3. Proponer cambios concretos.
4. Separar versión conservadora y versión ambiciosa.
5. Dar checklist de implementación.

## Formato

### Validación del plan de Chat A
### Riesgos no considerados
### Mejoras concretas
### Versión conservadora
### Versión ambiciosa
### Checklist
### Qué debería decidir el humano

## Contexto compartido

[PEGAR 00_SHARED_CONTEXT.md]

## Respuesta de Chat A

[PEGAR 03_RESPONSE_CHAT_A.md]
EOC

cat > "$DIR/03_RESPONSE_CHAT_A.md" <<'EOC'
# Respuesta Chat A

[Pegar aquí respuesta del Chat A]
EOC

cat > "$DIR/04_RESPONSE_CHAT_B.md" <<'EOC'
# Respuesta Chat B

[Pegar aquí respuesta del Chat B]
EOC

cat > "$DIR/05_SYNTHESIS.md" <<'EOC'
# Síntesis final

## Qué dijo Chat A

## Qué dijo Chat B

## Coincidencias

## Diferencias

## Decisión humana

## Próximo paso

## Checkpoint recomendado
EOC

echo "Sesión relay creada en: $DIR"
echo "Abre los archivos y usa los prompts en tus chats IA."

# Intentar copiar primer prompt al portapapeles en Windows Git Bash
if command -v clip.exe >/dev/null 2>&1; then
  cat "$DIR/01_CHAT_A_DIRECTOR_PROMPT.md" | clip.exe
  echo "Prompt Chat A copiado al portapapeles."
fi
