"""flujo.index - indexador real de C:\\rd para agentes/IA (solo lectura)."""
from .indexer import (  # noqa: F401
    load_index, find, versions, dupes, cleanup, stats,
    build_from_inventory, build_from_walk, save_index,
)
