"""The explicit-folder adapter feeding the IRIS portfolio inbox."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


pytestmark = pytest.mark.mak
ROOT = Path(__file__).resolve().parents[1]


def _load_hub():
    name = "hub_portfolio_folder_import_test"
    spec = importlib.util.spec_from_file_location(
        name, ROOT / "cultura" / "mak_plataforma" / "hub.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _folder(tmp_path):
    root = tmp_path / "artista" / "archivo"
    (root / "serie-a" / "bocetos").mkdir(parents=True)
    (root / "serie-a" / "obra-01.jpg").write_bytes(b"jpg")
    (root / "serie-a" / "bocetos" / "obra-01.mp4").write_bytes(b"video")
    (root / "serie-a" / "bocetos" / "notes.txt").write_text("context", encoding="utf-8")
    return root


def test_observer_adapter_preserves_files_and_folder_provenance(tmp_path):
    hub = _load_hub()
    root = _folder(tmp_path)
    sys.path.insert(0, str(ROOT / "cultura" / "mak_plataforma"))
    import portfolio_corpus  # noqa: E402

    batch, inbox = portfolio_corpus.observe_portfolio_folder(
        root, corpus_id="artist-corpus", artist_id="artist-supplied")

    assert batch["schema"] == "mak-archive-observation-batch-v1"
    assert inbox["schema"] == "faro-portfolio-inbox-v1"
    assert inbox["total"] == 3
    assert inbox["available_assets"] == 2
    assert [item["relative_path"] for item in inbox["items"]] == [
        "serie-a/bocetos/notes.txt",
        "serie-a/bocetos/obra-01.mp4",
        "serie-a/obra-01.jpg",
    ]
    assert inbox["context"]["artist_id"] == "artist-supplied"
    assert inbox["context"]["membership"]["authorship_claim"] is False
    assert inbox["items"][1]["source"]["sha256"]


def test_folder_route_previews_then_requires_explicit_activation(tmp_path, monkeypatch):
    hub = _load_hub()
    root = _folder(tmp_path)
    inbox_path = tmp_path / "active" / "PORTFOLIO_INBOX.json"
    inbox_path.parent.mkdir()
    inbox_path.write_text(json.dumps({"schema": "old", "items": []}), encoding="utf-8")
    monkeypatch.setattr(hub, "HOME", str(tmp_path))
    monkeypatch.setattr(hub, "PORTFOLIO_INBOX", str(inbox_path))
    hub._PORTFOLIO_INBOX_CACHE.clear()

    preview = hub._portfolio_observe_folder({
        "source_root": str(root), "artist_id": "artist-supplied",
    })
    assert preview["ok"] is True
    assert preview["status"] == "preview"
    assert preview["activation"] is False
    assert json.loads(inbox_path.read_text(encoding="utf-8"))["schema"] == "old"

    activated = hub._portfolio_observe_folder({
        "source_root": str(root), "artist_id": "artist-supplied",
        "corpus_id": "artist-corpus", "activate": True,
    })
    current = json.loads(inbox_path.read_text(encoding="utf-8"))
    assert activated["status"] == "activated"
    assert activated["previous_inbox_backup"]
    assert current["context"]["corpus_id"] == "artist-corpus"
    assert len(current["items"]) == 3
