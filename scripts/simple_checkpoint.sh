#!/usr/bin/env bash
set -e

MESSAGE="$1"
if [ -z "$MESSAGE" ]; then
  MESSAGE="avance simple $(date +%Y-%m-%d_%H-%M)"
fi

# Asegurar carpetas mínimas
mkdir -p inbox context checkpoints

DATE=$(date +%Y-%m-%d_%H-%M)
SAFE_MSG=$(echo "$MESSAGE" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-//' | sed 's/-$//')

# Inicializar git si hace falta
if [ ! -d .git ]; then
  git init
  git branch -M main 2>/dev/null || true
fi

git config core.autocrlf true

# Actualizar fecha en estado simple
if [ -f context/ESTADO_ACTUAL_SIMPLE.md ]; then
  python - <<PY
from pathlib import Path
p = Path('context/ESTADO_ACTUAL_SIMPLE.md')
s = p.read_text(encoding='utf-8')
lines = s.splitlines()
for i, line in enumerate(lines):
    if line.startswith('Última actualización:'):
        lines[i] = 'Última actualización: $DATE'
        break
p.write_text('\n'.join(lines) + '\n', encoding='utf-8')
PY
fi

# Crear índice simple del inbox
cat > context/INBOX_INDEX.md <<EOC
# Índice simple de inbox

Fecha: $DATE

Esta lista se genera automáticamente desde la carpeta \`inbox/\`.
Los archivos pueden estar incompletos, viejos o rotos. Sirven como evidencia para entender avances.

## Archivos encontrados

EOC

if [ -d inbox ]; then
  find inbox -maxdepth 4 -type f | sort | while read -r f; do
    size=$(wc -c < "$f" 2>/dev/null || echo "?")
    echo "- \`$f\` (${size} bytes)" >> context/INBOX_INDEX.md
  done
else
  echo "- No existe inbox/" >> context/INBOX_INDEX.md
fi

# Crear checkpoint simple
CP="checkpoints/${DATE}_simple_${SAFE_MSG}.md"
cat > "$CP" <<EOC
# Checkpoint simple — $MESSAGE

Fecha: $DATE

## Estado actual

EOC

if [ -f context/ESTADO_ACTUAL_SIMPLE.md ]; then
  cat context/ESTADO_ACTUAL_SIMPLE.md >> "$CP"
else
  echo "No existe context/ESTADO_ACTUAL_SIMPLE.md" >> "$CP"
fi

cat >> "$CP" <<EOC

---

## Índice de archivos de apoyo

EOC

cat context/INBOX_INDEX.md >> "$CP"

cat >> "$CP" <<'EOC'

---

## Prompt para continuar

```md
No empieces desde cero. Lee este checkpoint simple. Los archivos del inbox son evidencia incompleta: pueden estar rotos, viejos o básicos. Tu tarea es ayudarme a ordenar el siguiente paso mínimo, no proponer una arquitectura gigante.
```
EOC

# Git add/commit/push
git add -A
if git diff --cached --quiet; then
  echo "No hay cambios para commitear."
else
  git commit -m "checkpoint simple: $MESSAGE"
fi

if git remote get-url origin >/dev/null 2>&1; then
  git push -u origin main
else
  echo "No hay remoto origin configurado. El checkpoint quedó local."
  echo "Para conectar GitHub usa START_HERE_GITBASH.sh o git remote add origin URL."
fi

echo ""
echo "Listo. Checkpoint creado: $CP"
echo "Archivos clave para una IA:"
echo "- context/ESTADO_ACTUAL_SIMPLE.md"
echo "- context/INBOX_INDEX.md"
echo "- $CP"
