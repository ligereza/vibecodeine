#!/usr/bin/env python3
"""tests/test_resolume_composition.py -- which assets a real show used.

Controlled worlds where the answer is known, then the four real .avc
compositions in the SSD index, which were saved years before this code existed.

The abstention is the point. A composition stores absolute paths from another
machine, so the only join key is the basename, and a basename shared by several
assets is an ambiguity rather than a match. Measured spread across the four real
files: 1/1, 28/52, 0/81 and 0/1 unambiguous. A single "how well this works"
number would misrepresent every one of them, so the rate is per composition.
"""
from __future__ import annotations

import json
import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from flujo.venues.resolume_composition import (
    AMBIGUOUS,
    NOT_FOUND,
    RESOLVED_UNIQUE,
    anonymize_path,
    index_basenames,
    is_absolute_windows,
    orphan_candidates,
    parse_composition,
    resolve_references,
    usage_report,
)

REAL_DIR = Path("/media/mak/PortableSSD")
REAL_INDEX = Path("/home/mak/labs/portable-ssd-index-20260813/archivo_index.sqlite")
CAUPOLICAN = REAL_DIR / "DREFGIRA/IMPORT CLAUDIO/SHOWCAUPOLICAN FINAL ANTES DE CAUPO.avc"


def _composition(tmp_path: Path, name: str, refs, relative: bool = False,
                 canvas=(1920, 1080)):
    root = ET.Element("Composition", {
        "name": "Composition", "numDecks": "2", "numLayers": "3",
        "numColumns": "8", "compositionIsRelative": "1" if relative else "0"})
    ET.SubElement(root, "versionInfo", {
        "name": "Resolume Arena", "majorVersion": "7", "minorVersion": "21"})
    ET.SubElement(root, "CompositionInfo", {
        "name": Path(name).stem, "description": "",
        "width": str(canvas[0]), "height": str(canvas[1])})
    for tag, path in refs:
        ET.SubElement(root, tag, {"value": path})
    out = tmp_path / name
    ET.ElementTree(root).write(out, encoding="utf-8", xml_declaration=True)
    return parse_composition(out)


def _index(tmp_path: Path, relative_paths):
    path = tmp_path / "index.sqlite"
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE assets (asset_id TEXT, relative_path TEXT, bytes INTEGER)")
    con.executemany("INSERT INTO assets VALUES (?,?,?)",
                    [(f"a{i}", rel, 1000 + i)
                     for i, rel in enumerate(relative_paths)])
    con.commit()
    con.close()
    return path


# --- privacy: a real username must never leave this module ----------------

def test_a_windows_username_is_anonymised():
    raw = r"C:\Users\alguien\OneDrive\Escritorio\listas\clip.mov"
    safe = anonymize_path(raw)
    assert "alguien" not in safe
    assert "<usuario>" in safe
    assert safe.endswith(r"listas\clip.mov")


def test_anonymisation_survives_forward_slashes_and_case():
    assert "alguien" not in anonymize_path("c:/USERS/alguien/x.mov")
    assert anonymize_path("") == ""
    assert anonymize_path("relative/clip.mov") == "relative/clip.mov"


def test_no_reference_leaves_the_record_with_a_raw_username(tmp_path):
    record = _composition(tmp_path, "show.avc", [
        ("VideoFile", r"C:\Users\alguien\Desktop\a.mov")])
    blob = json.dumps([r.__dict__ for r in []]) + json.dumps(
        usage_report(record, resolve_references(record, {})), ensure_ascii=False)
    assert "alguien" not in blob
    assert "<usuario>" in blob


def test_absolute_windows_paths_are_recognised():
    assert is_absolute_windows(r"C:\Users\ejemplo\a.mov")
    assert is_absolute_windows(r"\\server\share\a.mov")
    assert not is_absolute_windows("Media/a.mov")
    assert not is_absolute_windows("")


# --- the abstention -------------------------------------------------------

def test_one_asset_with_that_name_resolves(tmp_path):
    record = _composition(tmp_path, "s.avc", [
        ("VideoFile", r"C:\Users\ejemplo\Desktop\unico.mov")])
    resolutions = resolve_references(record, {"unico.mov": ["TOUR/unico.mov"]})
    assert [r.status for r in resolutions] == [RESOLVED_UNIQUE]
    assert resolutions[0].candidates == ("TOUR/unico.mov",)


def test_several_assets_with_that_name_abstain(tmp_path):
    """THE TRAP. Two different clips can share a filename, so a name match is
    not identity. Measured on the real index: 2.mov, 3.mov, 4.mov and
    'comp 2.mov' each name three distinct assets."""
    record = _composition(tmp_path, "s.avc", [
        ("VideoFile", r"C:\Users\ejemplo\Desktop\2.mov")])
    resolutions = resolve_references(
        record, {"2.mov": ["A/2.mov", "B/2.mov", "C/2.mov"]})
    assert resolutions[0].status == AMBIGUOUS
    assert len(resolutions[0].candidates) == 3
    report = usage_report(record, resolutions)
    # An ambiguity contributes nothing to the usage claim.
    assert report["assets_usados"] == []
    assert report["tasa_resolucion_inequivoca"] == 0.0
    assert any("sin decidir" in x for x in report["limites"])


def test_a_missing_reference_is_not_a_claim_that_the_file_never_existed(tmp_path):
    record = _composition(tmp_path, "s.avc", [
        ("VideoFile", r"C:\Users\ejemplo\Desktop\ausente.mov")])
    report = usage_report(record, resolve_references(record, {}))
    assert report["conteos"][NOT_FOUND] == 1
    assert any("NO prueba que el archivo no exista" in x
               for x in report["limites"])


def test_a_resolution_never_claims_identical_bytes(tmp_path):
    record = _composition(tmp_path, "s.avc", [
        ("VideoFile", r"C:\Users\ejemplo\Desktop\unico.mov")])
    report = usage_report(record, resolve_references(
        record, {"unico.mov": ["TOUR/unico.mov"]}))
    assert any("no identidad de bytes" in x or "candidata, no identidad" in x
               for x in report["limites"])
    assert "full_sha256" in " ".join(report["limites"])


def test_the_same_basename_from_two_directories_is_flagged(tmp_path):
    """Measured inside a real composition: 'Fire Transition 1.mov' is cited from
    two different folders, so the basename does not even separate them there."""
    record = _composition(tmp_path, "s.avc", [
        ("VideoFile", r"C:\Users\ejemplo\Footage\fire.mov"),
        ("VideoFile", r"C:\Users\ejemplo\Nueva carpeta\fire.mov")])
    assert len(record.references) == 2
    assert any("directorios distintos" in w for w in record.warnings)


def test_an_all_absolute_composition_is_flagged_as_not_self_contained(tmp_path):
    record = _composition(tmp_path, "s.avc", [
        ("VideoFile", r"C:\Users\ejemplo\a.mov"), ("VideoFile", r"D:\y\b.mov")])
    assert any("no es autocontenida" in w for w in record.warnings)


def test_a_composition_with_no_media_says_so(tmp_path):
    record = _composition(tmp_path, "empty.avc", [])
    assert record.references == []
    assert any("no cita ningun archivo" in w for w in record.warnings)


def test_a_document_that_is_not_a_composition_is_refused(tmp_path):
    path = tmp_path / "x.avc"
    path.write_text("<XmlState name='a'><ScreenSetup/></XmlState>", encoding="utf-8")
    with pytest.raises(ValueError):
        parse_composition(path)


def test_parsing_and_resolution_are_deterministic(tmp_path):
    refs = [("VideoFile", r"C:\Users\ejemplo\a.mov"), ("AudioFile", r"C:\Users\ejemplo\b.wav")]
    first = _composition(tmp_path, "s.avc", refs)
    second = parse_composition(tmp_path / "s.avc")
    base = {"a.mov": ["T/a.mov"]}
    assert (usage_report(first, resolve_references(first, base))
            == usage_report(second, resolve_references(second, base)))


def test_the_rate_is_per_composition_and_counts_reconcile(tmp_path):
    record = _composition(tmp_path, "s.avc", [
        ("VideoFile", r"C:\Users\ejemplo\one.mov"),
        ("VideoFile", r"C:\Users\ejemplo\two.mov"),
        ("VideoFile", r"C:\Users\ejemplo\three.mov"),
        ("VideoFile", r"C:\Users\ejemplo\four.mov")])
    report = usage_report(record, resolve_references(record, {
        "one.mov": ["A/one.mov"],
        "two.mov": ["A/two.mov", "B/two.mov"]}))
    counts = report["conteos"]
    assert counts[RESOLVED_UNIQUE] == 1
    assert counts[AMBIGUOUS] == 1
    assert counts[NOT_FOUND] == 2
    assert (counts[RESOLVED_UNIQUE] + counts[AMBIGUOUS] + counts[NOT_FOUND]
            == counts["referencias"])
    assert report["tasa_resolucion_inequivoca"] == pytest.approx(0.25)


# --- orphan candidates: a starting list, never a delete list --------------

def test_orphan_candidates_never_claim_an_asset_is_unused(tmp_path):
    index = _index(tmp_path, ["TOUR/used.mov", "TOUR/idle.mov", "OTHER/x.mov"])
    result = orphan_candidates("TOUR", {"TOUR/used.mov"}, index)
    assert result["assets_en_el_contenedor"] == 2
    assert result["referenciados_por_una_composicion_leida"] == 1
    assert result["sin_referencia_conocida"] == 1
    assert "no significa inutilizado" in result["advertencia"].casefold()
    assert "no una lista de borrado" in result["advertencia"]
    assert [o["asset"] for o in result["mayores_sin_referencia"]] == ["TOUR/idle.mov"]


def test_orphan_candidates_stay_inside_the_named_container(tmp_path):
    index = _index(tmp_path, ["TOUR/a.mov", "OTHER/b.mov"])
    result = orphan_candidates("TOUR", set(), index)
    assert result["assets_en_el_contenedor"] == 1


# --- real input -----------------------------------------------------------

def _skip_unless_real():
    if not CAUPOLICAN.is_file() or not REAL_INDEX.is_file():
        pytest.skip("SSD not mounted or index absent")


def test_the_real_caupolican_show_resolves_its_setlist():
    """Numbers measured on 2026-08-21, so a regression is visible."""
    _skip_unless_real()
    record = parse_composition(CAUPOLICAN)
    assert record.composition_name == "SHOWCAUPOLICAN FINAL ANTES DE CAUPO"
    assert record.canvas == (1920, 1080)
    assert record.layers == 6 and record.columns == 24
    assert not record.relative_paths_declared
    report = usage_report(record, resolve_references(
        record, index_basenames(REAL_INDEX)))
    counts = report["conteos"]
    assert counts["referencias"] == 52
    assert counts[RESOLVED_UNIQUE] == 28
    assert counts[AMBIGUOUS] == 6
    assert counts[NOT_FOUND] == 18
    # It pulled material from a second container, which folder structure alone
    # would not have shown.
    assert report["contenedores_tocados"] == ["DREFGIRA",
                                              "descargas hasta RDFLYER 2050"]
    setlist = [a for a in report["assets_usados"] if "BLOQUE 01 LSDR" in a]
    assert len(setlist) >= 8, setlist


def test_a_real_composition_pointing_at_another_machine_resolves_nothing():
    """The honest opposite case, kept: sampier.avc cites another machine's
    Desktop, so nothing resolves and the tool must not pretend otherwise."""
    path = REAL_DIR / "LYON/sampier.avc"
    if not path.is_file() or not REAL_INDEX.is_file():
        pytest.skip("SSD not mounted")
    record = parse_composition(path)
    report = usage_report(record, resolve_references(
        record, index_basenames(REAL_INDEX)))
    assert report["conteos"][RESOLVED_UNIQUE] == 0
    assert report["tasa_resolucion_inequivoca"] == 0.0
    assert report["assets_usados"] == []
    assert any("no es autocontenida" in w
               for w in report["composicion"]["avisos"])
