"""Tests de la categoria dossier del knowledge store.

Cubre: ingesta de los 4 dossiers curados (tapiz, tilde, psicosis, precursor),
idempotencia, indice sin copia de contenido (solo metadata + ruta), y que la
CLI `flujo knowledge list dossiers` los muestre.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from flujo.knowledge import store

DOSSIER_IDS = {"tapiz", "tilde", "psicosis", "precursor"}

runner = CliRunner()


@pytest.fixture
def tmp_store(tmp_path: Path, monkeypatch) -> Path:
    """Redirige el knowledge root a un dir temporal; la fuente .md queda real."""
    root = tmp_path / "knowledge"
    monkeypatch.setattr(store, "knowledge_root", lambda: root)
    return root


def test_source_dossiers_exist():
    src = store.dossier_source_dir()
    assert src.is_dir()
    stems = {p.stem for p in src.glob("*.md")}
    assert DOSSIER_IDS <= stems


def test_entity_dirs_learned_dossier_category():
    assert store.ENTITY_DIRS["dossier"] == "dossiers"
    assert store.ENTITY_DIRS["dossiers"] == "dossiers"


def test_ingest_creates_four_indexes(tmp_store: Path):
    paths = store.ingest_dossiers()
    assert {p.stem for p in paths} >= DOSSIER_IDS
    assert set(store.list_entities("dossiers")) >= DOSSIER_IDS
    for pid in DOSSIER_IDS:
        data = store.load_entity("dossiers", pid)
        assert data["id"] == pid
        assert data["kind"] == "dossier"
        assert data["project"] == pid
        assert data["title"]
        assert data["subject"]
        assert data["status"] != "unknown"
        assert data["sections"]
        assert len(data["content_sha256"]) == 64
        assert data["ingested_at"]
        # La referencia apunta al .md real dentro del repo
        src = store.repo_root() / data["source_path"]
        assert src.is_file()
        assert data["source_path"].startswith("projects/cultura/dossiers/")


def test_index_is_metadata_only_no_content_copy(tmp_store: Path):
    """El store guarda mapa, no territorio: el cuerpo del .md no se copia."""
    store.ingest_dossiers()
    yaml_text = (tmp_store / "dossiers" / "tilde.yaml").read_text(encoding="utf-8")
    body = (store.dossier_source_dir() / "tilde.md").read_text(encoding="utf-8")
    # Frase del cuerpo del dossier (findings) que NO debe estar en el indice
    marker = "abreviatura utilizada por los copistas"
    assert marker in body
    assert marker not in yaml_text
    assert len(yaml_text) < len(body) / 3


def test_hard_limit_flag(tmp_store: Path):
    """psicosis y precursor declaran HARD LIMIT en el .md; el indice lo refleja."""
    store.ingest_dossiers()
    assert store.load_entity("dossiers", "psicosis")["hard_limit"] is True
    assert store.load_entity("dossiers", "precursor")["hard_limit"] is True
    assert store.load_entity("dossiers", "tilde")["hard_limit"] is False


def test_ingest_is_idempotent(tmp_store: Path):
    first = store.ingest_dossiers()
    snapshot = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in first}
    second = store.ingest_dossiers()
    assert [p.name for p in first] == [p.name for p in second]
    for p in second:
        content, mtime = snapshot[p]
        assert p.read_bytes() == content
        assert p.stat().st_mtime_ns == mtime  # ni siquiera se reescribio


def test_reingest_after_source_change(tmp_store: Path, tmp_path: Path):
    """Si el .md fuente cambia, el indice se actualiza con hash nuevo."""
    src_dir = tmp_path / "dossiers_src"
    src_dir.mkdir()
    md = src_dir / "demo.md"
    md.write_text(
        "# Dossier: demo — prueba\n\nStatus: BORRADOR\n\n## Seccion unica\n\ntexto\n",
        encoding="utf-8",
    )
    store.ingest_dossiers(src_dir)
    before = store.load_entity("dossiers", "demo")
    md.write_text(
        "# Dossier: demo — prueba\n\nStatus: INVESTIGADO\n\n## Seccion unica\n\ntexto nuevo\n",
        encoding="utf-8",
    )
    store.ingest_dossiers(src_dir)
    after = store.load_entity("dossiers", "demo")
    assert after["content_sha256"] != before["content_sha256"]
    assert after["status"] == "INVESTIGADO"


def test_missing_source_dir_raises(tmp_store: Path, tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        store.ingest_dossiers(tmp_path / "no_existe")


def test_committed_index_in_sync_with_sources():
    """El indice versionado en knowledge/dossiers/ refleja los .md actuales."""
    for pid in DOSSIER_IDS:
        data = store.load_entity("dossiers", pid)
        fresh = store.build_dossier_index(store.repo_root() / data["source_path"])
        assert data["content_sha256"] == fresh["content_sha256"], (
            f"knowledge/dossiers/{pid}.yaml desactualizado: "
            "correr py -m flujo.knowledge ingest-dossiers"
        )


def test_cli_knowledge_list_shows_dossiers():
    from flujo.cli import app

    result = runner.invoke(app, ["knowledge", "list", "dossiers"])
    assert result.exit_code == 0
    for pid in DOSSIER_IDS:
        assert pid in result.output
