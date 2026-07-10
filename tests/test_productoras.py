"""Tests offline de productoras (sin llamadas a Gemini).

El smoke test REAL (Gemini vision contra el flyer de thegrid) se corrio
2026-07-10 y paso; aqui se fija la logica local: match exacto contra el
store, slugify, y el fallback de .env.
"""
import json

from flujo.eventos import productoras


def test_match_grid_literal(tmp_path):
    # la entrada real del store: el alias debe incluir la forma LITERAL
    # que extrae Gemini ("GRID"), no solo el nombre formal
    entry = {"name": "The Grid", "aliases": ["GRID", "thegrid.club"]}
    (tmp_path / "thegrid.json").write_text(json.dumps(entry), encoding="utf-8")
    known = productoras.load_all(tmp_path)
    assert productoras.match({"productora_name": "GRID"}, known) == "thegrid"
    assert productoras.match({"productora_name": "grid"}, known) == "thegrid"
    assert productoras.match({"productora_name": "The Grid"}, known) == "thegrid"
    # igualdad exacta: no hay substring-match (evita over-match)
    assert productoras.match({"productora_name": "GRIDX"}, known) is None
    assert productoras.match({"productora_name": None}, known) is None


def test_match_via_texto_visible(tmp_path):
    # corrida real 2026-07-10: Gemini devolvio productora_name=null pero
    # 'GRID' venia en other_text_visible -> debe matchear igual
    entry = {"name": "The Grid", "aliases": ["GRID"]}
    (tmp_path / "thegrid.json").write_text(json.dumps(entry), encoding="utf-8")
    known = productoras.load_all(tmp_path)
    ex = {"productora_name": None,
          "other_text_visible": ["FASE GENERAL 02", "GRID", "KI/KI", "DEC 5"]}
    assert productoras.match(ex, known) == "thegrid"
    # texto visible sin alias curado: sigue sin match
    assert productoras.match({"productora_name": None,
                              "other_text_visible": ["KI/KI"]}, known) is None


def test_store_real_tiene_alias_literal():
    # el json commiteado en data/productoras debe mantener el alias GRID
    from pathlib import Path
    store = Path(__file__).resolve().parents[1] / "data" / "productoras"
    entry = json.loads((store / "thegrid.json").read_text(encoding="utf-8"))
    aliases_lower = [a.lower() for a in entry["aliases"]]
    assert "grid" in aliases_lower


def test_slugify():
    assert productoras.slugify("The Grid Club") == "the_grid_club"
    assert productoras.slugify("  ") == "sin_nombre"
    assert productoras.slugify("Ke!ne$") == "ke_ne"


def test_env_fallback_parsea_sin_dotenv(tmp_path, monkeypatch):
    # _env_fallback lee KEY=valor a mano; keys con comillas y sin ellas
    monkeypatch.setattr(productoras, "_env_fallback", productoras._env_fallback)
    env = tmp_path / ".env"
    env.write_text('GEMINI_API_KEY="abc123"\nGEMINI_API_KEY_2=def456\nOTRA=x\n',
                   encoding="utf-8")

    def fake_fallback():
        valores = {}
        for linea in env.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if linea.startswith("GEMINI_API_KEY") and "=" in linea:
                nombre, valor = linea.split("=", 1)
                valores.setdefault(nombre.strip(), valor.strip().strip('"').strip("'"))
        return valores

    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY_2", raising=False)
    monkeypatch.setattr(productoras, "_env_fallback", fake_fallback)
    assert productoras._keys() == ["abc123", "def456"]


def test_identify_nunca_autocrea(tmp_path, monkeypatch):
    monkeypatch.setattr(productoras, "extract_from_flyer",
                        lambda _p: {"productora_name": "Nueva Prod"})
    res = productoras.identify(tmp_path / "x.jpg", tmp_path)
    assert res["matched"] is False
    assert res["needs_confirmation"] is True
    assert list(tmp_path.glob("*.json")) == []  # no escribio nada solo
