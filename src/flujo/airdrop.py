"""Motor de actualizaciones (airdrop) — sin carpeta de versión.

Soltar los archivos a aplicar dentro de `_airdrop/` respetando la estructura
del repo (ej. `_airdrop/src/flujo/cli.py`). Luego `flujo airdrop apply` los
copia a su destino, crea backup, y dispara checkpoint + push automáticamente.
"""

import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .paths import repo_root


def get_airdrop_dir() -> Path:
    return repo_root() / "_airdrop"


def get_backup_base_dir() -> Path:
    return repo_root() / "_airdrop_backups"


_MANIFEST_NAME = "_airdrop_manifest.json"
_PROTECTED_TOP_LEVEL_DIRS = {
    "src", "scripts", "tests", "docs", "projects", "jobs", "tools",
    "schemas", "context", ".github",
}


def _write_manifest(backup_dir: Path, changes: List[Dict]) -> None:
    """Guarda lo aplicado para que rollback también revierta archivos NEW."""
    manifest = [
        {"rel": c["rel"], "status": c["status"]}
        for c in changes
    ]
    (backup_dir / _MANIFEST_NAME).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _load_manifest(backup_dir: Path) -> List[Dict]:
    manifest_path = backup_dir / _MANIFEST_NAME
    if not manifest_path.exists():
        return []
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict) and item.get("rel")]


def _cleanup_empty_parents(path: Path, repo: Path) -> None:
    """Elimina carpetas vacías creadas por archivos NEW, sin borrar raíces del repo."""
    current = path
    while current != repo and repo in current.parents:
        if current.parent == repo and current.name in _PROTECTED_TOP_LEVEL_DIRS:
            break
        try:
            current.rmdir()
        except OSError:
            break
        current = current.parent


# archivos que se ignoran al escanear _airdrop/
# .gitignore se permite explícitamente porque es un archivo legítimo de actualización
_IGNORE = {".gitkeep", ".DS_Store"}


def _is_ignored(src: Path) -> bool:
    """Decide si un archivo de _airdrop/ debe ignorarse."""
    if src.name in _IGNORE:
        return True
    # Permitir .gitignore (archivo de configuración real del repo)
    if src.name == ".gitignore":
        return False
    if src.name.startswith("."):
        return True
    return False


def scan_airdrop() -> List[Dict]:
    """Escanea `_airdrop/` y devuelve la lista de cambios a aplicar.

    Cada cambio mapea un archivo de `_airdrop/` a su destino en la raíz del repo
    según su ruta relativa.
    """
    base = get_airdrop_dir()
    if not base.exists():
        return []
    changes: List[Dict] = []
    for src in sorted(base.rglob("*")):
        if src.is_dir():
            continue
        if _is_ignored(src):
            continue
        rel = src.relative_to(base)
        dest = repo_root() / rel
        status = "REPLACE" if dest.exists() else "NEW"
        # rel.as_posix() => siempre con "/" (consistente en Windows y Linux/macOS)
        changes.append({"src": src, "dest": dest, "rel": rel.as_posix(), "status": status})
    return changes


def list_airdrop_files() -> List[str]:
    """Lista las rutas relativas pendientes de aplicar en `_airdrop/`."""
    return [c["rel"] for c in scan_airdrop()]


def apply_airdrop(dry_run: bool = False) -> List[Dict]:
    """Aplica todos los archivos de `_airdrop/` al repo.

    1. Crea backup de los archivos existentes (REPLACE) en `_airdrop_backups/`.
    2. Copia cada archivo a su destino (creando carpetas si hace falta).
    3. Da permiso de ejecución a los `.sh`.
    """
    changes = scan_airdrop()
    if not changes or dry_run:
        return changes

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_dir = get_backup_base_dir() / timestamp
    backup_dir.mkdir(parents=True, exist_ok=True)
    _write_manifest(backup_dir, changes)

    for c in changes:
        src, dest, rel = c["src"], c["dest"], c["rel"]
        if c["status"] == "REPLACE":
            bpath = backup_dir / rel
            bpath.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dest, bpath)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        if dest.suffix == ".sh":
            dest.chmod(dest.stat().st_mode | 0o111)
    return changes


def _git(args: List[str], cwd: Path) -> "subprocess.CompletedProcess":
    """Ejecuta git directamente (sin shell). Funciona en Windows/Linux/macOS."""
    return subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True
    )


def _write_checkpoint_file(repo: Path, msg: str) -> Path:
    """Crea checkpoints/<fecha>_<slug>.md (equivalente a checkpoint.sh, en Python)."""
    import re

    checkpoints = repo / "checkpoints"
    checkpoints.mkdir(parents=True, exist_ok=True)
    date = datetime.now().strftime("%Y-%m-%d_%H-%M")
    slug = re.sub(r"[^a-z0-9]+", "-", msg.lower()).strip("-") or "avance"
    cp = checkpoints / f"{date}_{slug}.md"
    # Prefer LAST_HANDOFF for modern low-token AI continuation (ESTADO is legacy)
    lh_path = repo / "context" / "LAST_HANDOFF.md"
    estado_path = repo / "context" / "ESTADO.md"
    if lh_path.exists():
        estado = lh_path.read_text(encoding="utf-8")[:2000] + "\n... (truncado para checkpoint)"
    elif estado_path.exists():
        estado = estado_path.read_text(encoding="utf-8")
    else:
        estado = "Sin LAST_HANDOFF.md ni ESTADO.md"
    cp.write_text(
        f"# Checkpoint — {msg}\n\nFecha: {date}\n\n## Estado\n\n{estado}\n\n"
        f"## Cambios realizados\n\n-\n\n## Próximo paso\n\n-\n",
        encoding="utf-8",
    )
    return cp


def run_auto_checkpoint(message: Optional[str] = None) -> bool:
    """Crea checkpoint + commit + push usando git directamente (Python puro).

    No depende de `bash` ni de `scripts/checkpoint.sh`, por lo que funciona en
    Windows (Git Bash) sin chocar con el bash de WSL. Reintenta el commit si un
    pre-commit hook modifica archivos y aborta el primer intento.
    """
    repo = repo_root()
    if not (repo / ".git").exists():
        print("No es un repo git (.git no existe).")
        return False

    msg = message or f"airdrop aplicado {datetime.now().strftime('%Y-%m-%d_%H-%M')}"

    try:
        _write_checkpoint_file(repo, msg)

        # commit robusto frente a pre-commit hooks (hasta 3 intentos)
        committed = False
        for _ in range(3):
            _git(["add", "-A"], repo)
            staged = _git(["diff", "--cached", "--quiet"], repo)
            if staged.returncode == 0:
                print("No hay cambios para commitear.")
                committed = True
                break
            res = _git(["commit", "-m", f"checkpoint: {msg}"], repo)
            if res.returncode == 0:
                committed = True
                break
            # un hook pudo modificar archivos: re-agregar y reintentar
        if not committed:
            print("No se pudo commitear tras 3 intentos (revisar hooks / git status).")
            return False

        # push a la rama actual
        if _git(["remote", "get-url", "origin"], repo).returncode == 0:
            branch = _git(["rev-parse", "--abbrev-ref", "HEAD"], repo).stdout.strip() or "main"
            push = _git(["push", "-u", "origin", branch], repo)
            if push.returncode != 0:
                print(push.stderr or push.stdout)
                return False
        return True
    except Exception as e:  # noqa: BLE001
        print(f"Error en auto-checkpoint: {e}")
        return False


def rollback_last() -> Optional[Path]:
    """Restaura el último backup desde `_airdrop_backups/`.

    Desde v0.34.8 usa un manifest por backup: los archivos `REPLACE` se
    restauran y los archivos `NEW` se eliminan. Si el backup es legacy (sin
    manifest), mantiene el comportamiento anterior: solo restaura reemplazos.
    """
    repo = repo_root()
    base = get_backup_base_dir()
    if not base.exists():
        return None
    backups = sorted([d for d in base.iterdir() if d.is_dir()], reverse=True)
    if not backups:
        return None
    last = backups[0]

    manifest = _load_manifest(last)
    if manifest:
        # Primero restaurar reemplazos desde backup.
        for item in manifest:
            if item.get("status") != "REPLACE":
                continue
            rel = Path(str(item["rel"]))
            src = last / rel
            if not src.exists():
                continue
            dest = repo / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            if dest.suffix == ".sh":
                dest.chmod(dest.stat().st_mode | 0o111)

        # Luego remover archivos que fueron NEW.
        for item in manifest:
            if item.get("status") != "NEW":
                continue
            rel = Path(str(item["rel"]))
            dest = repo / rel
            if dest.exists() and dest.is_file():
                dest.unlink()
                _cleanup_empty_parents(dest.parent, repo)
        return last

    # Backups antiguos sin manifest: comportamiento legacy.
    for src in last.rglob("*"):
        if src.is_dir() or src.name == _MANIFEST_NAME:
            continue
        rel = src.relative_to(last)
        dest = repo / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        if dest.suffix == ".sh":
            dest.chmod(dest.stat().st_mode | 0o111)
    return last
