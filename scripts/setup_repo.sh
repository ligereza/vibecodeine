#!/usr/bin/env bash
set -e

if [ ! -d .git ]; then
  git init
fi

git config core.autocrlf true

touch logs/CHANGELOG.md

git add .
git commit -m "chore: inicializar sistema de checkpoints" || echo "Nada nuevo para commitear."

echo "Repo inicializado. Ahora agrega remoto si falta:"
echo "git remote add origin https://github.com/TU_USUARIO/TU_REPO.git"
echo "git branch -M main"
echo "git push -u origin main"
