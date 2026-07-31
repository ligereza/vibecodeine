"""GPT mini is reserved for the main session, not MAK automation."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _text(path):
    return (ROOT / path).read_text(encoding="utf-8")


def test_modelo_capaz_es_cerebras():
    text = _text("cultura/mak_research/research_lib.py")
    assert 'MODELO_CAPAZ = "cerebras"' in text
    # 2026-07-30: watsonx encabeza `razonar` por salud medida (32/32). Lo que
    # este ratchet cuida no es el orden, es que gpt-5-mini/azure NO entre a la
    # automatizacion de MAK: eso se comprueba abajo, sobre el valor completo.
    assert '"razonar": "watsonx,cerebras,groq,ollama"' in text
    assert '"bulk": "cerebras,groq,ollama"' in text


def test_slots_no_rutean_a_azure():
    """Los slots de rol son la ruta por defecto del organismo: azure (gpt-5-mini)
    no puede aparecer en ninguno, cambie el orden que cambie."""
    text = _text("cultura/mak_research/research_lib.py")
    bloque = text.split("_SLOTS = {", 1)[1].split("}", 1)[0]
    assert "azure" not in bloque


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