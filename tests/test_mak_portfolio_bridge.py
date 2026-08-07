from pathlib import Path

from cultura.mak_plataforma import hub


def test_portfolio_file_stays_inside_iskvw_root(tmp_path, monkeypatch):
    root = tmp_path / "iskvw"
    root.mkdir()
    (root / "editor.html").write_text("<html>", encoding="utf-8")
    (root / "datos").mkdir()
    (root / "datos" / "campo.json").write_text("{}", encoding="utf-8")
    outside = tmp_path / "secret.txt"
    outside.write_text("secret", encoding="utf-8")
    monkeypatch.setattr(hub, "PORTFOLIO_ROOT", str(root))

    assert Path(hub._portfolio_file("editor.html")).name == "editor.html"
    assert Path(hub._portfolio_file("datos/campo.json")).name == "campo.json"
    assert hub._portfolio_file("../secret.txt") is None
    assert hub._portfolio_file("missing.json") is None
