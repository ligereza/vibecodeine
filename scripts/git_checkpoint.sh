#!/usr/bin/env bash
set -e

MESSAGE="$1"
if [ -z "$MESSAGE" ]; then
  MESSAGE="checkpoint: actualización $(date +%Y-%m-%d_%H-%M)"
fi

# Asegurar que estamos en un repo
if [ ! -d .git ]; then
  echo "No existe .git. Ejecutando setup inicial..."
  bash scripts/setup_repo.sh
fi

# Actualizar fecha en MASTER_CONTEXT si existe
if [ -f context/MASTER_CONTEXT.md ]; then
  DATE=$(date +%Y-%m-%d_%H-%M)
  # Compatible con Git Bash/Windows sin depender de sed -i distinto
  python - <<PY
from pathlib import Path
p = Path('context/MASTER_CONTEXT.md')
s = p.read_text(encoding='utf-8')
lines = s.splitlines()
for i, line in enumerate(lines):
    if line.startswith('Última actualización:'):
        lines[i] = 'Última actualización: $DATE'
        break
p.write_text('\n'.join(lines) + '\n', encoding='utf-8')
PY
fi

# Mostrar estado
echo "Estado antes de commit:"
git status --short

# Agregar todo respetando .gitignore
git add -A

# Commit solo si hay cambios staged
if git diff --cached --quiet; then
  echo "No hay cambios para commitear."
else
  git commit -m "$MESSAGE"
fi

# Push si existe remoto origin
if git remote get-url origin >/dev/null 2>&1; then
  CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
  echo "Subiendo a origin/$CURRENT_BRANCH..."
  git push -u origin "$CURRENT_BRANCH"
else
  echo "No hay remoto origin configurado. Agrega uno con:"
  echo "git remote add origin https://github.com/TU_USUARIO/TU_REPO.git"
fi
