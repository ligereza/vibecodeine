#!/usr/bin/env python3
"""tests/test_research_registry_contract.py -- both hubs must agree.

MAK serves the research catalog from two independent surfaces: the platform hub
(`cultura/mak_plataforma/hub.py`, port 8900) and the serve hub
(`src/flujo/web/hub.py`, behind `flujo serve`). On 2026-08-21 the identical
defect was measured in both: each response hardcoded
`"registry": "research/jardines_interpretativos/jardines_interpretativos.sqlite"`,
a relative string that resolves from no working directory, because the registry
lives outside the repository under $HOME and MAK_RESEARCH_REGISTRY can move it.
A caller that took the reported path and opened it always failed.

Fixing one surface and leaving the other is how the bug survived the first
repair, so this file pins the contract on BOTH and asserts they agree. The same
applies to the `/api/research/job` id contract: a missing id used to surface as
the raw `int()` ValueError, making a forgotten parameter indistinguishable from
a broken job.
"""
from __future__ import annotations

import importlib.util
import os
import sqlite3
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
PLATFORM_HUB = REPO / "cultura" / "mak_plataforma" / "hub.py"


def _load_platform_hub():
    """Load the platform hub by path: it is not an importable package."""
    sys.path.insert(0, str(PLATFORM_HUB.parent))
    spec = importlib.util.spec_from_file_location("_test_platform_hub", PLATFORM_HUB)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _seed_registry(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE domain_adapters (id INTEGER PRIMARY KEY, "
                     "slug TEXT, label TEXT, description TEXT, "
                     "input_examples TEXT, source_policy TEXT, "
                     "constraint_policy TEXT)")
        conn.execute("CREATE TABLE research_jobs (id INTEGER PRIMARY KEY, "
                     "adapter_id INTEGER)")
        conn.execute("INSERT INTO domain_adapters VALUES "
                     "(1,'curatoria','Curatoria','d','e','s','c')")
        conn.execute("INSERT INTO research_jobs VALUES (1, 1)")


def _serve_hub_catalog():
    from flujo.web.hub import HubRequestHandler

    handler = HubRequestHandler.__new__(HubRequestHandler)
    return handler._get_research_catalog()


def test_serve_hub_reports_an_openable_registry_path(tmp_path, monkeypatch):
    db = tmp_path / "registry.sqlite"
    monkeypatch.setenv("MAK_RESEARCH_REGISTRY", str(db))
    catalog = _serve_hub_catalog()
    assert catalog["available"] is False
    assert catalog["registry"] == "not_created"

    _seed_registry(db)
    catalog = _serve_hub_catalog()
    assert catalog["available"] is True
    assert os.path.isabs(catalog["registry"]), catalog["registry"]
    assert Path(catalog["registry"]).is_file()
    assert catalog["registry_exists"] is True
    assert catalog["registry_source"] == "MAK_RESEARCH_REGISTRY"
    assert [a["slug"] for a in catalog["adapters"]] == ["curatoria"]
    assert catalog["jobs"] == 1


def test_both_hubs_publish_the_same_registry_contract(tmp_path, monkeypatch):
    """The defect survived its first repair because nothing compared them."""
    db = tmp_path / "shared.sqlite"
    monkeypatch.setenv("MAK_RESEARCH_REGISTRY", str(db))
    _seed_registry(db)

    platform = _load_platform_hub()._research_catalog()
    serve = _serve_hub_catalog()

    keys = {"available", "adapters", "jobs", "registry", "registry_exists",
            "registry_source"}
    assert keys <= set(platform), sorted(keys - set(platform))
    assert keys <= set(serve), sorted(keys - set(serve))
    for key in ("available", "jobs", "registry", "registry_exists",
                "registry_source"):
        assert platform[key] == serve[key], (
            f"hubs disagree on {key!r}: {platform[key]!r} != {serve[key]!r}")
    assert ([a["slug"] for a in platform["adapters"]]
            == [a["slug"] for a in serve["adapters"]])


def test_default_registry_is_absolute_on_both_surfaces(monkeypatch):
    monkeypatch.delenv("MAK_RESEARCH_REGISTRY", raising=False)
    from flujo.web.hub import HubRequestHandler

    serve_path = HubRequestHandler.__new__(HubRequestHandler)._research_registry_path()
    platform_path = _load_platform_hub()._research_registry_path()
    assert serve_path.is_absolute()
    assert platform_path.is_absolute()
    assert serve_path == platform_path, (
        f"the two hubs would open different registries: {serve_path} vs "
        f"{platform_path}")


def test_a_missing_job_id_is_a_contract_error_on_both_surfaces():
    """Neither surface may leak the raw int() ValueError for a missing id."""
    platform = PLATFORM_HUB.read_text(encoding="utf-8")
    serve = (REPO / "src" / "flujo" / "web" / "hub.py").read_text(encoding="utf-8")
    for name, text in (("platform hub", platform), ("serve hub", serve)):
        assert "id_requerido" in text, (
            f"{name} does not declare the id_requerido contract error")
        assert "raw_id.isdigit()" in text, (
            f"{name} still converts the id without validating it first")
