#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The merge that authorises overwriting the artist's live archive.

The first version of this tool counted three outcomes per field -- improved
(old empty), inherited (new empty), lost (gone) -- and printed "campos
perdidos: 0" as the gate the operator reads before saying yes.

An adversarial pass over the real archive found that those three buckets
covered 1.879 of 17.602 decisions. The other 15.723 were fields BOTH passes
filled, where the new one won with no comparison and no line in the report:
9.348 differed and 4.595 of those got SMALLER. A 260-character description
became "Una pintura abstracta con figuras humanas y elementos naturales."

That is this repo's house defect built into the tool meant to protect against
it: hand-written buckets over a presence test that stopped covering the
majority of what the operation does, under a headline number that could only
ever read zero.

What is pinned here is the fourth bucket, the per-field attribution, and the
two things that make the write itself safe.
"""
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TOOL = RAIZ / "tools" / "consolidar_fichas.py"


def _mod():
    import importlib.util
    spec = importlib.util.spec_from_file_location("consolidar", TOOL)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _ficha(fid, vision, motor="watsonx", **extra):
    d = {"id": fid, "fuente": "ig", "vision": vision,
         "medicion": {"vision": {"estado": "medido", "motor": motor}}}
    d.update(extra)
    return d


def _escribir(ruta, fichas):
    ruta.write_text("\n".join(json.dumps(f, ensure_ascii=False)
                              for f in fichas) + "\n", encoding="utf-8")


def _correr(a, b, *extra):
    return subprocess.run([sys.executable, str(TOOL), str(a), str(b), *extra],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=120)


# ------------------------------------------------------- the fourth bucket

def test_a_field_both_passes_filled_is_counted_as_replaced():
    m = _mod()
    vieja = _ficha("1", {"descripcion": "una descripcion larga y detallada"})
    nueva = _ficha("1", {"descripcion": "corta"})
    _, cuentas = m.fusionar(vieja, nueva)
    assert cuentas["reemplazados"] == ["vision.descripcion"]
    assert cuentas["encogidos"] == ["vision.descripcion"]
    assert cuentas["mejorados"] == [] and cuentas["heredados"] == []


def test_an_identical_value_is_not_a_replacement():
    """Counting no-ops as replacements would drown the number that matters."""
    m = _mod()
    f = {"descripcion": "igual"}
    _, cuentas = m.fusionar(_ficha("1", f), _ficha("1", dict(f)))
    assert cuentas["reemplazados"] == []


def test_a_longer_new_value_is_replaced_but_not_shrunk():
    m = _mod()
    _, cuentas = m.fusionar(_ficha("1", {"descripcion": "corta"}),
                            _ficha("1", {"descripcion": "mucho mas larga"}))
    assert cuentas["reemplazados"] == ["vision.descripcion"]
    assert cuentas["encogidos"] == []


def test_a_list_losing_items_counts_as_shrunk():
    """`materiales` going from four entries to one is loss by any reading, and
    a presence test cannot see it."""
    m = _mod()
    _, cuentas = m.fusionar(
        _ficha("1", {"materiales": ["oleo", "ceniza", "lino", "hilo"]}),
        _ficha("1", {"materiales": ["pintura"]}))
    assert cuentas["encogidos"] == ["vision.materiales"]


def test_the_report_names_the_replacements(tmp_path):
    a, b = tmp_path / "a.jsonl", tmp_path / "b.jsonl"
    _escribir(a, [_ficha("1", {"descripcion": "una descripcion larga"})])
    _escribir(b, [_ficha("1", {"descripcion": "corta"})])
    r = _correr(a, b)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "REEMPLAZADOS): 1" in r.stdout
    assert "MAS CHICOS" in r.stdout
    assert "campos perdidos: 0" not in r.stdout, (
        "ese titulo se leia como 'no se perdio nada' sobre miles de valores "
        "pisados; si vuelve, vuelve la mentira")
    assert "campos que quedan vacios habiendo tenido valor: 0" in r.stdout, (
        "el cero sigue existiendo, pero diciendo lo que realmente mide")


# ------------------------------------------------------- attribution per field

def test_inheritance_records_which_engine_produced_each_field():
    m = _mod()
    vieja = _ficha("1", {"oportunidad_codigo": "algo"}, motor="ollama")
    nueva = _ficha("1", {"tecnica": "collage"}, motor="watsonx")
    fusion, _ = m.fusionar(vieja, nueva)
    vis = fusion["medicion"]["vision"]
    assert vis["heredado"] == {"vision.oportunidad_codigo": "ollama"}
    assert vis["motor"] == "watsonx"
    assert "motor_heredado" not in vis, (
        "un motor por ficha pierde el rastro apenas corre una segunda fusion")


def test_a_second_merge_keeps_the_original_engine():
    """The use this tool was written for is repeated passes. If the second one
    re-signs as its own what a third engine measured, the trail is gone."""
    m = _mod()
    v1 = _ficha("1", {"oportunidad_codigo": "algo"}, motor="ollama")
    fusion1, _ = m.fusionar(v1, _ficha("1", {"tecnica": "x"}, motor="watsonx"))
    fusion2, _ = m.fusionar(fusion1,
                            _ficha("1", {"tecnica": "y"}, motor="gemini"))
    assert fusion2["medicion"]["vision"]["heredado"] == {
        "vision.oportunidad_codigo": "ollama"}


def test_nothing_inherited_leaves_no_marker():
    m = _mod()
    fusion, _ = m.fusionar(_ficha("1", {}), _ficha("1", {"tecnica": "x"}))
    assert "heredado" not in fusion["medicion"]["vision"]


def test_the_measurement_block_stops_contradicting_its_own_ficha():
    """`medicion` came from the NEW pass and described the new pass. After the
    merge it listed as absent the very keys the merge had just filled."""
    m = _mod()
    vieja = _ficha("1", {"oportunidad_codigo": "algo"}, motor="ollama")
    nueva = _ficha("1", {"tecnica": "collage"}, motor="watsonx")
    nueva["medicion"]["vision"]["claves_ausentes"] = ["oportunidad_codigo"]
    nueva["medicion"]["vision"]["detalle"] = "1"
    fusion, _ = m.fusionar(vieja, nueva)
    vis = fusion["medicion"]["vision"]
    assert "claves_ausentes" not in vis
    assert vis["detalle"] == "2", "dos campos llenos tras la fusion"


# ------------------------------------------------------- the write itself

def test_a_dry_run_writes_nothing(tmp_path):
    a, b = tmp_path / "a.jsonl", tmp_path / "b.jsonl"
    _escribir(a, [_ficha("1", {"tecnica": "x"})])
    _escribir(b, [_ficha("1", {"tecnica": "y"})])
    antes = a.read_text(encoding="utf-8")
    r = _correr(a, b)
    assert "ensayo" in r.stdout
    assert a.read_text(encoding="utf-8") == antes


def test_applying_leaves_a_backup_and_the_merged_file(tmp_path):
    a, b = tmp_path / "a.jsonl", tmp_path / "b.jsonl"
    _escribir(a, [_ficha("1", {"tecnica": "vieja", "colores": ["rojo"]})])
    _escribir(b, [_ficha("1", {"tecnica": "nueva"})])
    r = _correr(a, b, "--aplicar")
    assert r.returncode == 0, r.stdout + r.stderr
    respaldos = list(tmp_path.glob("*.bak-*"))
    assert len(respaldos) == 1
    fusion = json.loads(a.read_text(encoding="utf-8").strip())
    assert fusion["vision"]["tecnica"] == "nueva"
    assert fusion["vision"]["colores"] == ["rojo"], "lo heredado sobrevive"


def test_the_temp_file_does_not_collide_with_the_perception_one():
    """`percepcion.py` writes `<archivo>.tmp` over the same file. Two processes
    on the same temp name overwrite each other without saying anything."""
    fuente = TOOL.read_text(encoding="utf-8")
    assert ".jsonl.consolidar.tmp" in fuente
    assert 'with_suffix(".jsonl.tmp")' not in fuente


def test_it_refuses_to_write_while_a_perception_is_running():
    """A ficha appended between the read and the overwrite disappears from the
    live file AND stays marked in `procesados.txt`: a hole no retry rescues. It
    is the only irreversible part of the operation -- everything else is
    covered by the backup."""
    fuente = TOOL.read_text(encoding="utf-8")
    assert "_hay_percepcion_corriendo" in fuente
    assert "percepcion.py correr" in fuente
    assert "flock" in fuente and "LOCK_NB" in fuente
