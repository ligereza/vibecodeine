"""Helper para anclar rutas a la raíz del repo flujo."""
from pathlib import Path


def repo_root() -> Path:
    """Devuelve la raíz del repo asumiendo que este archivo está en scripts/."""
    return Path(__file__).resolve().parents[1]
