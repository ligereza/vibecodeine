"""Tests for the persisted reconstruction -> Project IR bridge."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from flujo.knowledge.project_router import route_project
from flujo.knowledge.reconstruction_adapter import (
    ADAPTER_SCHEMA,
    adapt_reconstruction,
    project_irs_from_reconstruction,
)
from tests.test_project_reconstruction import make_index
from flujo.knowledge.project_reconstruction import reconstruct, to_payload


def test_reconstruction_units_become_reviewable_ir_without_dependencies(tmp_path: Path) -> None:
    index = tmp_path / "index.sqlite"
    make_index(index)
    payload = to_payload(reconstruct(index, "DREFGIRA"))
    records = project_irs_from_reconstruction(payload, source_ref="fixture/reconstruction.json")

    assert [record["title"] for record in records] == ["DREFGIRA", "DREFGIRA/SHOW"]
    assert all(record["schema"] == "mak-project-ir-v1" for record in records)
    assert all(record["state"] == "review_required" for record in records)
    assert all(record["source"]["kind"] == "portable_ssd_index" for record in records)
    assert all("physical_source_mount_unverified" in record["unknowns"] for record in records)
    assert all(record["consumer_policy"]["portfolio"] == "never_auto_publish" for record in records)
    assert all(route_project(record)["reason"] == "project_state_requires_evidence"
               for record in records)
    # The dependency remains visible as an indexed artifact of its owning
    # unit; it is not promoted to a second Project IR record.
    assert len(records) == 2
    assert not any(record["title"].endswith("waves_55443377") for record in records)


def test_adapter_reads_persisted_json_and_preserves_index_hash(tmp_path: Path) -> None:
    index = tmp_path / "index.sqlite"
    make_index(index)
    payload = to_payload(reconstruct(index, "DREFGIRA"))
    reconstruction = tmp_path / "reconstruction.json"
    reconstruction.write_text(json.dumps(payload), encoding="utf-8")

    records = adapt_reconstruction(reconstruction)

    assert len(records) == 2
    assert records[0]["evidence"][0]["index_fingerprint"] == payload["index_fingerprint"]
    assert records[0]["reconstruction"]["schema"] == "mak-project-reconstruction-v1"


def test_adapter_does_not_mutate_source_index(tmp_path: Path) -> None:
    index = tmp_path / "index.sqlite"
    make_index(index)
    before = index.read_bytes()
    payload = to_payload(reconstruct(index, "DREFGIRA"))
    project_irs_from_reconstruction(payload)
    assert index.read_bytes() == before
