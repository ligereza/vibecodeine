#!/usr/bin/env python3
"""Contracts for `tools/gen_propuesta_directiva.py`, 427 lines untested.

The tool renders the formal proposal the Reduciendo Daño board reads. Its
docstring makes three promises, and a board document is exactly the place where
an unchecked promise costs something:

* every figure is read from `data/rd.db` at generation time -- "No hay números
  escritos a mano: si un dato no está en la base, acá aparece como sin dato en
  vez de inventarse";
* the page is self-contained -- "no CDN, no external JS";
* `productora_eventos` (real events) is never conflated with `eventos` (the
  quoting templates), because "conflating them would make the board read demo
  rows as real work".

The third is the sharpest: `data/rd.db` carries both tables, so the mistake is
one wrong table name away and nothing would look broken.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sqlite3

import pytest

from tools.gen_propuesta_directiva import PAGE, inline_logo, leer_db

REPO = Path(__file__).resolve().parents[1]
REAL_DB = REPO / "data" / "rd.db"
LOGO = REPO / "assets" / "logo" / "RD_logo_vector_blanco.svg"

# A resource the page *loads*. A URL sitting in the data -- a promoter's event
# link, an SVG namespace -- is content, not a dependency.
EXTERNAL_RESOURCE = re.compile(
    r"""<script[^>]+src=["']https?://|"""
    r"""<link[^>]+href=["']https?://|"""
    r"""<img[^>]+src=["']https?://|"""
    r"""@import\s+["']?https?://|"""
    r"""url\(\s*["']?https?://""",
    re.IGNORECASE,
)


def _make_db(path: Path, *, tables: dict[str, list[dict]]) -> Path:
    con = sqlite3.connect(path)
    for name, rows in tables.items():
        if not rows:
            continue
        columns = list(rows[0])
        con.execute(
            f"CREATE TABLE {name} ({', '.join(f'{c} TEXT' for c in columns)})"
        )
        con.executemany(
            f"INSERT INTO {name} VALUES ({', '.join('?' * len(columns))})",
            [tuple(row[c] for c in columns) for row in rows],
        )
    con.commit()
    con.close()
    return path


class TestTheQuotingTemplatesNeverReachTheBoard:
    """`eventos` is demo data. `productora_eventos` is real work."""

    def test_the_real_database_carries_both_tables(self) -> None:
        # If it did not, the tests below would pass while checking nothing.
        if not REAL_DB.is_file():
            pytest.skip("data/rd.db is not present in this checkout")
        con = sqlite3.connect(REAL_DB)
        try:
            names = {
                row[0] for row in
                con.execute("SELECT name FROM sqlite_master WHERE type='table'")
            }
        finally:
            con.close()
        assert {"eventos", "productora_eventos"} <= names

    def test_the_reader_returns_the_real_events_only(self) -> None:
        if not REAL_DB.is_file():
            pytest.skip("data/rd.db is not present in this checkout")
        payload = leer_db(REAL_DB)
        assert "productora_eventos" in payload
        assert "eventos" not in payload, (
            "the quoting templates reached the board payload"
        )

    def test_a_template_row_does_not_leak_into_the_payload(
        self, tmp_path: Path
    ) -> None:
        db = _make_db(tmp_path / "rd.db", tables={
            "eventos": [{"id": "1", "nombre": "PLANTILLA_DEMO_NO_MOSTRAR"}],
            "productora_eventos": [
                {"productora_slug": "una", "nombre": "Evento real"}
            ],
        })
        payload = json.dumps(leer_db(db), ensure_ascii=False)
        assert "PLANTILLA_DEMO_NO_MOSTRAR" not in payload
        assert "Evento real" in payload


class TestItReadsRatherThanInvents:
    def test_a_missing_table_yields_an_empty_list_not_a_crash(
        self, tmp_path: Path
    ) -> None:
        db = _make_db(tmp_path / "vacia.db", tables={
            "packs": [{"id": "1", "orden": "1", "nombre": "Pack"}],
        })
        payload = leer_db(db)
        assert payload["packs"]
        for absent in ("reactivos", "suplementos", "productoras", "venues",
                       "productora_eventos", "logos"):
            assert payload[absent] == [], f"{absent} was invented"

    def test_a_pack_without_inclusions_gets_an_empty_list(
        self, tmp_path: Path
    ) -> None:
        db = _make_db(tmp_path / "sin_inclusiones.db", tables={
            "packs": [{"id": "1", "orden": "1", "nombre": "Pack"}],
        })
        assert leer_db(db)["packs"][0]["inclusiones"] == []

    def test_inclusions_are_attached_to_their_pack(self, tmp_path: Path) -> None:
        db = _make_db(tmp_path / "con_inclusiones.db", tables={
            "packs": [{"id": "p1", "orden": "1", "nombre": "Pack"}],
            "inclusiones": [
                {"pack_id": "p1", "orden": "1", "texto": "Primera"},
                {"pack_id": "p1", "orden": "2", "texto": "Segunda"},
                {"pack_id": "otro", "orden": "1", "texto": "De otro pack"},
            ],
        })
        assert leer_db(db)["packs"][0]["inclusiones"] == ["Primera", "Segunda"]

    def test_a_missing_database_names_the_command_that_builds_it(
        self, tmp_path: Path
    ) -> None:
        # An operator who runs this without the projection needs the next
        # step, not a traceback.
        with pytest.raises(SystemExit) as caught:
            leer_db(tmp_path / "no_existe.db")
        assert "rd-db build" in str(caught.value)

    def test_the_page_falls_back_to_sin_dato_rather_than_a_number(self) -> None:
        # The payload is rendered client-side; this is where a missing datum
        # becomes visible instead of becoming a figure.
        assert 'return alt || "sin dato"' in PAGE

    def test_the_page_states_that_its_figures_come_from_the_database(self) -> None:
        assert "sin dato" in PAGE
        assert "No hay números escritos a mano" in PAGE


class TestTheDocumentIsSelfContained:
    def test_the_template_loads_no_external_resource(self) -> None:
        assert not EXTERNAL_RESOURCE.search(PAGE)

    def test_the_rendered_document_loads_no_external_resource(
        self, tmp_path: Path
    ) -> None:
        if not LOGO.is_file():
            pytest.skip("the logo asset is not present in this checkout")
        db = _make_db(tmp_path / "rd.db", tables={
            "packs": [{"id": "1", "orden": "1", "nombre": "Pack"}],
        })
        html = _render(db)
        assert not EXTERNAL_RESOURCE.search(html)

    def test_a_url_inside_the_data_is_content_not_a_dependency(
        self, tmp_path: Path
    ) -> None:
        # The real database holds a promoter's Instagram link, and the SVG
        # carries its xmlns. Both are absolute URLs and neither is fetched, so
        # the check has to be about loading, not about the string "http".
        if not LOGO.is_file():
            pytest.skip("the logo asset is not present in this checkout")
        db = _make_db(tmp_path / "rd.db", tables={
            "productora_eventos": [{
                "productora_slug": "una",
                "enlace": "https://www.instagram.com/reel/EJEMPLO/",
            }],
        })
        html = _render(db)
        assert "https://www.instagram.com/reel/EJEMPLO/" in html
        assert not EXTERNAL_RESOURCE.search(html)


class TestTheLogoIsInlined:
    def test_the_logo_is_embedded_as_markup(self) -> None:
        if not LOGO.is_file():
            pytest.skip("the logo asset is not present in this checkout")
        svg = inline_logo(LOGO)
        assert svg.lstrip().startswith("<svg")
        assert "http" not in svg.split(">", 1)[0] or "xmlns" in svg.split(">", 1)[0]

    def test_a_missing_logo_is_not_silently_dropped(self, tmp_path: Path) -> None:
        with pytest.raises((OSError, SystemExit)):
            inline_logo(tmp_path / "no_existe.svg")


def _render(db: Path) -> str:
    """Reproduce what `main` writes, without going through argparse."""
    payload = leer_db(db)
    logo = inline_logo(LOGO)
    return (
        PAGE
        .replace("__LOGO__", logo)
        .replace("__LOGO_FOOT__", logo)
        .replace("__DATA_JSON__", json.dumps(payload, ensure_ascii=False))
    )


class TestTheDocumentCarriesTheData:
    def test_every_placeholder_is_filled(self, tmp_path: Path) -> None:
        if not LOGO.is_file():
            pytest.skip("the logo asset is not present in this checkout")
        db = _make_db(tmp_path / "rd.db", tables={
            "packs": [{"id": "1", "orden": "1", "nombre": "Pack"}],
        })
        html = _render(db)
        for placeholder in ("__LOGO__", "__LOGO_FOOT__", "__DATA_JSON__"):
            assert placeholder not in html, f"{placeholder} was left unreplaced"

    def test_a_changed_row_changes_the_document(self, tmp_path: Path) -> None:
        # "If the database changes, the document changes" is the whole claim.
        if not LOGO.is_file():
            pytest.skip("the logo asset is not present in this checkout")
        first = _render(_make_db(tmp_path / "a.db", tables={
            "packs": [{"id": "1", "orden": "1", "nombre": "Pack Alfa"}],
        }))
        second = _render(_make_db(tmp_path / "b.db", tables={
            "packs": [{"id": "1", "orden": "1", "nombre": "Pack Beta"}],
        }))
        assert "Pack Alfa" in first and "Pack Alfa" not in second
        assert "Pack Beta" in second
