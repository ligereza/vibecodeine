from pathlib import Path


EDITOR = Path(__file__).parents[1] / "iskvw" / "editor.html"


def test_editor_surfaces_mak_contract_without_making_hub_required():
    source = EDITOR.read_text(encoding="utf-8")

    assert "id=\"inbox-contrato\"" in source
    assert "fetch('/api/portfolio/contract'" in source
    assert 'id="inbox-copiloto-externos-lista"' in source
    assert "/api/portfolio/external-candidates" in source
    assert "fetch('/api/portfolio/review-queue'" in source
    assert "fetch('/api/portfolio/triangulation'" in source
    assert "/api/portfolio/triangulation/context-link" in source
    assert "function enlazarContexto" in source
    assert "enlazar a grupo..." in source
    assert 'id="inbox-revision"' in source
    assert "function cargarRevision" in source
    assert "evidencia humana" in source
    assert "Contexto humano aceptado" in source
    assert "sin grupo de triangulacion enlazado" in source
    assert 'id="inbox-indice-lista"' in source
    assert "/api/portfolio/index" in source
    assert "Usuarios mencionados, no entidades resueltas" in source
    assert 'id="inbox-foco"' in source
    assert "Estudio de obra" in source
    assert "abrir en estudio" in source
    assert "function mostrarAccionPieza" in source
    assert "function cargarTriangulacionPieza" in source
    assert "foco-visual-field" in source
    assert "foco-orbit-item" in source
    assert "foco-dock" in source
    assert "/api/portfolio/copilot/vision" in source
    assert "visión AWS" in source
    assert "previsualizar orden" in source
    assert 'id="inbox-herramientas"' in source
    assert "no se ha movido ningun archivo" in source
    assert "function pintarFoco" in source
    assert "ID exacto para enfocar" in source
    assert "resolverCandidatoExterno" in source
    assert "no publica automaticamente" in source
    assert "consentimiento registrado antes de publicar" in source


def test_editor_keeps_search_board_filter_and_association_tray_separate():
    source = EDITOR.read_text(encoding="utf-8")

    assert 'id="inbox-buscar"' in source
    assert 'id="inbox-tablero"' in source
    assert 'id="inbox-asociacion"' in source
    assert 'id="inbox-resumen"' in source
    assert 'data-inbox-view="pendientes"' in source
    assert 'data-inbox-view="archivo"' in source
    assert 'data-inbox-view="mesa"' in source
    assert 'let INBOX_VIEW = "pendientes"' in source
    assert 'class="inbox-tools"' in source
    assert "inbox-pin-media" in source
    assert "inbox-action-primary" in source
    assert "const INBOX_SELECTED = new Set()" in source
    assert "anadirSeleccionAlTablero" in source
