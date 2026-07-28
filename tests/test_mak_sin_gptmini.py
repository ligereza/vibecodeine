"""GPT mini is reserved for the main session, not MAK automation."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _text(path):
    return (ROOT / path).read_text(encoding="utf-8")


def test_modelo_capaz_es_cerebras():
    text = _text("cultura/mak_research/research_lib.py")
    assert 'MODELO_CAPAZ = "cerebras"' in text
    assert '"razonar": "cerebras,groq,ollama"' in text
    assert '"bulk": "cerebras,groq,ollama"' in text


def test_panel_y_codex_no_rutean_a_azure():
    panel = _text("cultura/mak_research/panel.py")
    codex = _text("cultura/mak_codex/codex_lib.py")
    capataz = _text("cultura/mak_plataforma/capataz.py")
    assert '"proveedor": "azure"' not in panel
    assert 'order=["azure"' not in panel
    assert 'LLM(order="%s,groq,ollama" % MODELO_CAPAZ)' in codex
    assert 'CADENA_COMPLETA = "cerebras,groq,ollama"' in capataz


def test_gptmini_no_figura_como_recurso_activo():
    cuotas = _text("cultura/mak_plataforma/cuotas.py")
    assert "gpt-5-mini" not in cuotas