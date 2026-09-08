"""
Tests de la pieza MANIFIESTO #8 (cartografia de filtros).

La Omega11 (ver projects/cultura/cartografia_filtros/DOSSIER.md): la pieza
pierde si (a) registra/reconstruye el contenido detras de un bloqueo, o (b) el
mapa es indistinguible de un log plano. Estos tests fijan ambas condiciones mas
la mecanica.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PIEZA = Path(__file__).resolve().parents[1] / "projects" / "cultura" / "cartografia_filtros"
sys.path.insert(0, str(_PIEZA))

import cartografia_filtros as cf  # noqa: E402


def _bloqueo(**kw):
    base = dict(
        fecha="2026-07-16",
        capa="auto-mode-classifier",
        categoria="git-destructivo",
        silueta="quitar worktree + borrar rama en un comando",
        disposicion="reescrito",
    )
    base.update(kw)
    return cf.Bloqueo(**base)


def test_registro_sembrado_carga_y_es_borde_no_payload():
    reg = _PIEZA / "registro_bloqueos.jsonl"
    carto = cf.cargar_registro(reg)
    assert len(carto.bloqueos) == 6
    # Omega11(a): ninguna silueta del registro real es payload ejecutable.
    for b in carto.bloqueos:
        assert len(b.silueta) <= cf._MAX_SILUETA
        assert "\n" not in b.silueta
        assert "rm -rf" not in b.silueta.lower()


def test_omega11_a_rechaza_payload_largo():
    """Una silueta que dejo de ser silueta (arrastro contenido) no entra."""
    with pytest.raises(ValueError, match="payload"):
        _bloqueo(silueta="x" * (cf._MAX_SILUETA + 1))


def test_omega11_a_rechaza_marcador_de_payload():
    """Un comando crudo (marcador rm -rf, o multilinea) se rechaza al registrar."""
    with pytest.raises(ValueError):
        _bloqueo(silueta="rm -rf algo")
    with pytest.raises(ValueError):
        _bloqueo(silueta="linea1\nlinea2")
    with pytest.raises(ValueError):
        _bloqueo(silueta="ver https://ejemplo")


def test_capa_desconocida_se_rechaza():
    with pytest.raises(ValueError, match="capa desconocida"):
        _bloqueo(capa="inventada")


def test_omega11_b_no_es_log_plano():
    """El render agrupa por coordenada y distingue poroso/duro -- no es un cat."""
    carto = cf.cartografia_de([
        _bloqueo(categoria="fs-adyacente-a-credenciales", disposicion="manual-humano"),
        _bloqueo(categoria="fs-adyacente-a-credenciales", disposicion="manual-humano"),
        _bloqueo(categoria="git-destructivo", disposicion="reescrito"),
    ])
    salida = carto.render()
    # agrupacion por coordenada (celdas), no lista plana
    assert "[auto-mode-classifier] fs-adyacente-a-credenciales" in salida
    assert "[auto-mode-classifier] git-destructivo" in salida
    # distincion poroso/duro presente
    assert "borde duro (#): 2" in salida
    assert "borde poroso (~): 1" in salida
    assert "densidad por capa" in salida


def test_duros_vs_porosos():
    carto = cf.cartografia_de([
        _bloqueo(disposicion="manual-humano"),
        _bloqueo(disposicion="reescrito"),
        _bloqueo(disposicion="failsafe"),
    ])
    assert len(carto.duros) == 1
    assert len(carto.porosos) == 1
    assert carto.densidad() == {"auto-mode-classifier": 3}


def test_render_vacio_no_revienta():
    assert "vacia" in cf.Cartografia().render()


def test_por_coordenada_agrupa():
    carto = cf.cartografia_de([
        _bloqueo(categoria="a"),
        _bloqueo(categoria="a"),
        _bloqueo(categoria="b"),
    ])
    celdas = carto.por_coordenada()
    assert len(celdas[("auto-mode-classifier", "a")]) == 2
    assert len(celdas[("auto-mode-classifier", "b")]) == 1
