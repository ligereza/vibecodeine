"""flujo.index - indexador del arbol de material ($FLUJO_RD_ROOT) para agentes/IA (solo lectura)."""
from .indexer import (  # noqa: F401
    load_index, find, versions, dupes, cleanup, stats,
    build_from_inventory, build_from_walk, save_index,
)
