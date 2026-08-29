"""Discovery contract for the existing ISKVW/Portfolio department."""
from __future__ import annotations

from pathlib import Path

from src.flujo.departments import catalog


ROOT = Path(__file__).resolve().parents[1]


def test_archive_portfolio_view_is_discoverable_under_iskvw_portfolio():
    data = catalog(ROOT)

    assert data["schema"] == "mak-departments-v1"
    assert set(data["areas"]) == {"rd", "cultura", "iskvw"}

    links = data["areas"]["iskvw"]["tool_links"]
    archive_view = next(
        link for link in links
        if link.get("path") == "/api/portfolio/archive-view"
    )

    assert archive_view == {
        "label": "Archive portfolio view",
        "path": "/api/portfolio/archive-view",
        "mode": "read_only",
        "status": "draft",
        "publication": False,
        "authorship": False,
    }
