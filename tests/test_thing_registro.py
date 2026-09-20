"""Contract tests for the vendored thi.ng manifests.

The manifests are the machine-readable authority. A library marked en_uso must
name a real consumer that actually references its vendored bundle. Vendored
libraries may remain deliberately unused, but that state must be explicit.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
MANIFESTS = {
    "motor": REPO / "data" / "motor_librerias.json",
    "iskvw": REPO / "data" / "iskvw_librerias.json",
}
LIB_DIRS = {
    "motor": REPO / "docs" / "cultura" / "lib",
    "iskvw": REPO / "iskvw" / "piel" / "lib",
}
VALID_STATES = {"en_uso", "vendorizada_sin_consumidor", "descartada_con_medicion"}


def _entries(key: str) -> list[dict[str, object]]:
    payload = json.loads(MANIFESTS[key].read_text(encoding="utf-8"))
    return payload["librerias"]


def _is_vendored(js_path: Path) -> bool:
    return js_path.with_suffix("").with_suffix(".README.md").is_file()


@pytest.mark.parametrize("key", sorted(MANIFESTS))
def test_manifest_entries_are_explicit_and_pinned(key: str) -> None:
    entries = _entries(key)
    assert entries
    for entry in entries:
        version = str(entry.get("version", ""))
        assert re.fullmatch(r"\d+(\.\d+){1,3}", version), entry
        assert str(entry.get("para", "")).strip(), entry
        assert entry.get("estado") in VALID_STATES, entry
        consumers = entry.get("consumidores")
        assert isinstance(consumers, list), entry


@pytest.mark.parametrize("key", sorted(MANIFESTS))
def test_every_declared_bundle_exists(key: str) -> None:
    for entry in _entries(key):
        js = LIB_DIRS[key] / f"{entry['nombre']}.js"
        assert js.is_file(), f"{key}: falta {js}"


@pytest.mark.parametrize("key", sorted(MANIFESTS))
def test_no_vendored_bundle_is_orphaned_from_the_manifest(key: str) -> None:
    declared = {str(entry["nombre"]) for entry in _entries(key)}
    for js in LIB_DIRS[key].glob("*.js"):
        if _is_vendored(js):
            assert js.stem in declared, f"{key}: {js.name} no está declarado"


@pytest.mark.parametrize("key", sorted(MANIFESTS))
def test_in_use_libraries_name_real_consumers(key: str) -> None:
    for entry in _entries(key):
        consumers = [str(item) for item in entry.get("consumidores", [])]
        if entry["estado"] != "en_uso":
            assert not consumers, f"{entry['paquete']}: estado no activo con consumidores"
            continue

        assert consumers, f"{entry['paquete']}: EN USO sin consumidor"
        bundle_name = f"{entry['nombre']}.js"
        for relative in consumers:
            path = REPO / relative
            assert path.is_file(), f"{entry['paquete']}: consumidor inexistente {relative}"
            source = path.read_text(encoding="utf-8", errors="replace")
            assert bundle_name in source, (
                f"{entry['paquete']}: {relative} no referencia {bundle_name}"
            )


def test_mutation_in_use_without_consumer_is_rejected() -> None:
    entry = {"estado": "en_uso", "consumidores": []}
    with pytest.raises(AssertionError):
        assert entry["consumidores"], "EN USO debe declarar consumidor"
