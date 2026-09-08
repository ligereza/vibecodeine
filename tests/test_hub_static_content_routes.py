#!/usr/bin/env python3
"""tests/test_hub_static_content_routes.py -- the plain-content GET routes of
cultura/mak_plataforma/hub.py that carried zero tests: /favicon.ico, an
unknown /api/* path, the root fallback page, /pieza, /cuotas, /doctrina,
/reflexiones, /relevo and /genesis.

None of these appear in tests/test_hub_*.py or tests/test_mak_hub_*.py, and a
grep across the whole suite for their literal paths found no hit either --
these routes had exactly zero witnesses before this file. All of them are
markdown-to-html renderers or plain page servers, so hub.py is safe to import
here (the server only starts under `if __name__ == "__main__"`).
"""
import io
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "cultura", "mak_plataforma"))

import hub  # noqa: E402


class FakeHandler:
    def __init__(self, path, headers=None):
        self.path = path
        self.rfile = io.BytesIO(b"")
        self.headers = headers or {}
        self.command = "GET"
        self.calls = []
        self.redirect = None

    def _json(self, obj, code=200):
        self.calls.append(("json", obj, code))

    def _send(self, body_text, ctype="text/html; charset=utf-8", code=200):
        self.calls.append(("send", body_text, code))

    def _send_bytes(self, data, ctype="application/octet-stream", code=200):
        self.calls.append(("bytes", data, code))

    def send_response(self, code):
        self.redirect = {"code": code}

    def send_header(self, key, value):
        self.redirect.setdefault("headers", {})[key] = value

    def end_headers(self):
        pass

    @property
    def last(self):
        return self.calls[-1]


def _get(path):
    handler = FakeHandler(path)
    hub.H.do_GET(handler)
    return handler


class TestFaviconAndUnknownRoutes:
    def test_favicon_returns_no_content_without_a_body(self):
        handler = _get("/favicon.ico")

        assert handler.calls == []
        assert handler.redirect == {"code": 204}

    def test_unknown_api_path_is_a_named_404_not_a_page(self):
        handler = _get("/api/does-not-exist")

        kind, payload, code = handler.last
        assert kind == "json"
        assert code == 404
        assert payload == {"ok": False, "error": "ruta_api_no_encontrada",
                           "path": "/api/does-not-exist"}

    def test_unmatched_non_api_path_falls_back_to_the_face_page(self):
        handler = _get("/some/path/nobody/registered")

        kind, body, code = handler.last
        assert (kind, code) == ("send", 200)
        assert body is hub.PAGINA


class TestPieceEndpoint:
    def test_missing_id_is_rejected_before_touching_disk(self):
        handler = _get("/pieza?dir=informes")

        kind, body, code = handler.last
        assert code == 404
        assert body == "(no se pudo abrir)"

    def test_path_traversal_in_id_is_rejected(self):
        for bad_id in ("../etc/passwd", "sub/dir", "sub\\dir"):
            handler = _get("/pieza?id=" + bad_id)
            kind, body, code = handler.last
            assert code == 404, bad_id

    def test_valid_dir_and_id_reads_the_real_file_content(self, tmp_path, monkeypatch):
        monkeypatch.setattr(hub, "HOME", str(tmp_path))
        pieces_dir = tmp_path / "research" / "informes"
        pieces_dir.mkdir(parents=True)
        (pieces_dir / "reporte.md").write_text("contenido de prueba", encoding="utf-8")

        handler = _get("/pieza?dir=informes&id=reporte.md")

        kind, body, code = handler.last
        assert code == 200
        assert body == "contenido de prueba"

    def test_unknown_id_across_known_dirs_is_a_404(self, tmp_path, monkeypatch):
        monkeypatch.setattr(hub, "HOME", str(tmp_path))

        handler = _get("/pieza?id=missing.md")

        kind, body, code = handler.last
        assert code == 404
        assert body == "(no se pudo abrir)"


class TestCuotasPage:
    def test_cuotas_route_serves_the_cuotas_page_verbatim(self):
        handler = _get("/cuotas")

        kind, body, code = handler.last
        assert (kind, code) == ("send", 200)
        assert body is hub.CUOTAS_PAGE


class TestMarkdownFolderPages:
    def test_doctrina_lists_docs_and_renders_the_selected_one(self, tmp_path, monkeypatch):
        monkeypatch.setattr(hub, "DOCTRINA_DIR", str(tmp_path))
        (tmp_path / "doctrina_uno.md").write_text("# Uno\n\nprimer texto", encoding="utf-8")
        (tmp_path / "doctrina_dos.md").write_text("# Dos\n\nsegundo texto", encoding="utf-8")

        handler = _get("/doctrina?d=doctrina_dos.md")

        kind, body, code = handler.last
        assert (kind, code) == ("send", 200)
        assert "<h1>Dos</h1>" in body
        assert "segundo texto" in body
        assert 'href="/doctrina?d=doctrina_uno.md"' in body
        assert 'href="/">' in body

    def test_doctrina_with_no_docs_shows_empty_body(self, tmp_path, monkeypatch):
        monkeypatch.setattr(hub, "DOCTRINA_DIR", str(tmp_path))

        handler = _get("/doctrina")

        kind, body, code = handler.last
        assert code == 200
        assert "(vacío)" in body

    def test_reflexiones_uses_its_own_folder_and_prefix(self, tmp_path, monkeypatch):
        monkeypatch.setattr(hub, "REFLEXIONES_DIR", str(tmp_path))
        (tmp_path / "reflexion_a.md").write_text("# A\n\ntexto a", encoding="utf-8")

        handler = _get("/reflexiones")

        kind, body, code = handler.last
        assert code == 200
        assert "<h1>A</h1>" in body
        assert "reflexiones" in body


class TestRelevoPage:
    def test_relevo_reads_the_primary_source_when_present(self, tmp_path, monkeypatch):
        relevo_file = tmp_path / "RELEVO_MAK.md"
        relevo_file.write_text("# Estado\n\nal dia", encoding="utf-8")
        monkeypatch.setattr(hub, "RELEVO", str(relevo_file))

        handler = _get("/relevo")

        kind, body, code = handler.last
        assert code == 200
        assert "RELEVO_MAK.md" in body
        assert "<h1>Estado</h1>" in body

    def test_relevo_falls_back_to_the_historical_record_when_primary_is_missing(
            self, tmp_path, monkeypatch):
        monkeypatch.setattr(hub, "RELEVO", str(tmp_path / "does-not-exist.md"))
        monkeypatch.setattr(hub, "_REPO_ROOT", str(tmp_path))
        context_dir = tmp_path / "context"
        context_dir.mkdir()
        (context_dir / "HANDOFF_HISTORICO.md").write_text("# Fallback\n\nresumen", encoding="utf-8")

        handler = _get("/relevo")

        kind, body, code = handler.last
        assert code == 200
        assert "context/HANDOFF_HISTORICO.md" in body
        assert "<h1>Fallback</h1>" in body

    def test_relevo_without_any_source_says_so_instead_of_failing(self, tmp_path, monkeypatch):
        monkeypatch.setattr(hub, "RELEVO", str(tmp_path / "missing-a.md"))
        monkeypatch.setattr(hub, "_REPO_ROOT", str(tmp_path))

        handler = _get("/relevo")

        kind, body, code = handler.last
        assert code == 200
        assert "no se encontró un documento de continuidad operativo" in body


class TestGenesisPage:
    def test_genesis_embeds_the_historical_document_and_orientation_text(
            self, tmp_path, monkeypatch):
        genesis_file = tmp_path / "GENESIS.md"
        genesis_file.write_text("# Origen\n\nhistoria", encoding="utf-8")
        monkeypatch.setattr(hub, "GENESIS", str(genesis_file))

        handler = _get("/genesis")

        kind, body, code = handler.last
        assert code == 200
        assert "génesis / archivo histórico" in body
        assert "<h1>Origen</h1>" in body

    def test_genesis_without_the_file_says_so_instead_of_failing(self, tmp_path, monkeypatch):
        monkeypatch.setattr(hub, "GENESIS", str(tmp_path / "missing-genesis.md"))

        handler = _get("/genesis")

        kind, body, code = handler.last
        assert code == 200
        assert "(GENESIS.md no encontrado)" in body
