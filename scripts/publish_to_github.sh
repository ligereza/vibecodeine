#!/usr/bin/env bash
set -e

REPO_URL="$1"
MESSAGE="$2"

if [ -z "$MESSAGE" ]; then
  MESSAGE="checkpoint: actualización workflow IA diseño $(date +%Y-%m-%d_%H-%M)"
fi

if [ ! -d .git ]; then
  git init
  git branch -M main 2>/dev/null || true
fi

git config core.autocrlf true

if [ -n "$REPO_URL" ]; then
  if git remote get-url origin >/dev/null 2>&1; then
    git remote set-url origin "$REPO_URL"
  else
    git remote add origin "$REPO_URL"
  fi
fi

if [ -f context/MASTER_CONTEXT.md ]; then
  DATE=$(date +%Y-%m-%d_%H-%M)
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

git add -A
if git diff --cached --quiet; then
  echo "No hay cambios para commitear."
else
  git commit -m "$MESSAGE"
fi

if git remote get-url origin >/dev/null 2>&1; then
  git push -u origin main
else
  echo "Falta origin. Uso: bash scripts/publish_to_github.sh https://github.com/USUARIO/REPO.git \"mensaje\""
fi
