"""Resolve optional local runtimes without installing or executing them.

The MAK machine keeps Blender outside ``PATH`` on purpose.  Consumers must
still agree on the same executable, otherwise one audit says "missing" while
the render tools use a real binary.  This module only checks paths; it never
starts a process or changes the environment.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path


def resolve_blender(repo_root: str | Path | None = None) -> Path | None:
    """Return the first executable Blender candidate visible to this MAK.

    ``repo_root`` is used to locate the sibling ``/home/mak/blender`` install
    while keeping tests and other checkouts isolated.  The explicit env var
    remains the highest-priority override and is never printed by this helper.
    """
    candidates: list[Path] = []
    configured = os.environ.get("BLENDER_EXE", "").strip()
    if configured:
        candidates.append(Path(configured).expanduser())
    found = shutil.which("blender")
    if found:
        candidates.append(Path(found))
    if repo_root is not None:
        root = Path(repo_root).expanduser().resolve()
        home_root = root.parent if root.name == "flujo" else root
        candidates.extend((
            home_root / "blender" / "blender",
            home_root / "blender-4.5.3-viejo" / "blender",
        ))
    else:
        candidates.extend((
            Path("/home/mak/blender/blender"),
            Path("/home/mak/blender-4.5.3-viejo/blender"),
        ))
    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate)
        if key in seen:
            continue
        seen.add(key)
        try:
            if candidate.is_file() and os.access(candidate, os.X_OK):
                return candidate.resolve()
        except OSError:
            continue
    return None
