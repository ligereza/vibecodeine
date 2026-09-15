from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EDITORS = (ROOT / "iskvw" / "editor.html", ROOT / "flujo" / "iskvw" / "editor.html")
EXPECTED_FORMATS = [
    "declared-works",
    "documented-record",
    "observed-field",
    "practice-context",
]


def _format_ids(source: str) -> list[str]:
    match = re.search(r"const ARCHIVE_VIEW_FORMAT_IDS = \[([^\]]+)\];", source)
    assert match, "archive-view format contract is missing"
    return re.findall(r"'([^']+)'", match.group(1))


def test_iskvw_editors_share_archive_view_semantics_without_byte_identity() -> None:
    sources = [path.read_text(encoding="utf-8") for path in EDITORS]

    assert all(_format_ids(source) == EXPECTED_FORMATS for source in sources)
    for source in sources:
        assert "documented_record" in source
        assert "es registro de una obra, no la obra" in source
        assert "selection.documented_record_count" in source
        assert "hipótesis interna · no aprobación" in source
        assert "Contraevidencia conservada" in source
        assert "Referencias lógicas:" in source
        assert "promotion=none" in source
        assert "publication!==false" in source
        assert "shared_member_paths||[]).map(archiveViewReference)" in source
        assert "esc(item.asset_path||" not in source
