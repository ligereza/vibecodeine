# Guía rápida Git Bash — Checkpoints a GitHub

## 0. Opción más fácil: script automático

Después de descargar y extraer el workspace, abre Git Bash dentro de `ai-workflow-checkpoints` y ejecuta:

```bash
bash START_HERE_GITBASH.sh
```

El script te pedirá la URL del repo de GitHub y hará:

- `git init` si hace falta
- configurar rama `main`
- conectar `origin`
- crear checkpoint automático
- hacer commit
- hacer push a GitHub


## 1. Clonar o crear repo local

Si ya tienes repo en GitHub:

```bash
git clone https://github.com/TU_USUARIO/TU_REPO.git
cd TU_REPO
```

Si empiezas desde esta carpeta:

```bash
cd /c/Users/TU_USUARIO/Documents/ai-workflow-checkpoints
bash scripts/setup_repo.sh
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git branch -M main
git push -u origin main
```

## 2. Crear un checkpoint nuevo

```bash
bash scripts/new_checkpoint.sh "avance automatizaciones arena github"
```

Edita el archivo creado dentro de `/checkpoints`.

## 3. Guardar y subir cambios

```bash
bash scripts/git_checkpoint.sh "checkpoint: avance automatizaciones arena github"
```

## 4. Importar ZIP descargado de Arena

Copia el zip a una ruta fácil, por ejemplo Descargas. Luego:

```bash
bash scripts/import_arena_workspace.sh /c/Users/TU_USUARIO/Downloads/workspace.zip
```

Después:

```bash
bash scripts/git_checkpoint.sh "import workspace arena"
```

## 5. Ver link para compartir

Después de hacer push, abre tu repo en GitHub. Puedes compartir:

- Link del repo completo.
- Link del archivo `context/MASTER_CONTEXT.md`.
- Link del checkpoint más reciente en `/checkpoints`.

## 6. Comando típico diario

```bash
cd /c/Users/TU_USUARIO/Documents/ai-workflow-checkpoints
bash scripts/new_checkpoint.sh "trabajo del dia"
bash scripts/git_checkpoint.sh "checkpoint diario"
```
