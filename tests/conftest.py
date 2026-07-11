"""Make the suite test THIS checkout's src/flujo, not an editable install.

From a git worktree, `import flujo` would otherwise resolve to the main
checkout's installed package and the suite would silently test stale code.
Prepending this repo's src/ pins every test to the code next to it.
"""
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
