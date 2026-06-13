#!/usr/bin/env bash
set -e

echo "============================================================"
echo " AI Workflow Checkpoints — inicio rápido Git Bash"
echo "============================================================"
echo ""
echo "Este script inicializa el repo, crea un commit y lo sube a GitHub."
echo "No guarda contraseñas ni tokens. Git/GitHub te pedirá login si hace falta."
echo ""

# Ir a la carpeta donde está este script, aunque se ejecute desde otro lugar
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Carpeta actual: $SCRIPT_DIR"
echo ""

if ! command -v git >/dev/null 2>&1; then
  echo "ERROR: git no está instalado o Git Bash no lo encuentra."
  echo "Instala Git for Windows: https://git-scm.com/download/win"
  exit 1
fi

# Inicializar git si falta
if [ ! -d .git ]; then
  echo "Inicializando repositorio Git..."
  git init
else
  echo "Repositorio Git ya inicializado."
fi

# Config de Windows/Git Bash razonable
git config core.autocrlf true

# Rama main
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
if [ "$CURRENT_BRANCH" != "main" ]; then
  echo "Configurando rama main..."
  git branch -M main 2>/dev/null || true
fi

# Pedir URL del repo si no existe origin
if git remote get-url origin >/dev/null 2>&1; then
  ORIGIN_URL=$(git remote get-url origin)
  echo "Remoto origin existente: $ORIGIN_URL"
else
  echo ""
  echo "Pega la URL de tu repo GitHub vacío o existente."
  echo "Ejemplo HTTPS: https://github.com/TU_USUARIO/ai-workflow-checkpoints.git"
  echo "Ejemplo SSH:   git@github.com:TU_USUARIO/ai-workflow-checkpoints.git"
  echo ""
  read -r -p "URL del repo GitHub: " REPO_URL
  if [ -z "$REPO_URL" ]; then
    echo "No ingresaste URL. Se hará commit local, pero no push."
  else
    git remote add origin "$REPO_URL"
    echo "Remoto origin agregado: $REPO_URL"
  fi
fi

# Actualizar fecha del master context si existe
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
else:
    lines.insert(0, 'Última actualización: $DATE')
p.write_text('\n'.join(lines) + '\n', encoding='utf-8')
PY
fi

# Crear checkpoint automático si no hay checkpoint final de descarga
mkdir -p checkpoints
AUTO_CP="checkpoints/$(date +%Y-%m-%d_%H-%M)_checkpoint-subida-github.md"
cat > "$AUTO_CP" <<EOC
# Checkpoint — Subida inicial/actualización GitHub

Fecha: $(date +%Y-%m-%d_%H-%M)

## Acción

Se ejecutó `START_HERE_GITBASH.sh` para inicializar o actualizar el repo local y subirlo a GitHub.

## Estado

- Repo preparado para checkpoints de IA + diseño.
- Scripts incluidos.
- Documentación incluida.
- Flujo IA avanzada incluido.

## Próximo paso

Compartir el link de GitHub con una IA y pedirle que lea:

1. `context/MASTER_CONTEXT.md`
2. `context/TOOLS_INVENTORY.md`
3. El checkpoint más reciente en `/checkpoints`
4. `docs/PRODUCCION_TECNICA.md`
EOC

# Commit
echo ""
echo "Agregando archivos..."
git add -A

if git diff --cached --quiet; then
  echo "No hay cambios nuevos para commitear."
else
  COMMIT_MSG="checkpoint: subida inicial workflow IA diseño $(date +%Y-%m-%d_%H-%M)"
  echo "Creando commit: $COMMIT_MSG"
  git commit -m "$COMMIT_MSG"
fi

# Push si hay origin
if git remote get-url origin >/dev/null 2>&1; then
  echo ""
  echo "Subiendo a GitHub..."
  git push -u origin main
  echo ""
  echo "LISTO. Repo subido/actualizado en:"
  git remote get-url origin
else
  echo ""
  echo "Commit local listo, pero no hay remoto origin configurado."
  echo "Agrega remoto luego con:"
  echo "git remote add origin https://github.com/TU_USUARIO/ai-workflow-checkpoints.git"
  echo "git push -u origin main"
fi

echo ""
echo "============================================================"
echo " Finalizado"
echo "============================================================"
