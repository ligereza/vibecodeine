from __future__ import annotations

import re

import pytest

from flujo.knowledge.operations_source_snapshot import (
    build_operations_source_snapshot,
    validate_operations_source_snapshot,
)

from test_operations_read_only_map import _snapshots
from flujo.knowledge.operations_read_only_map import build_operations_read_only_map


pytestmark = pytest.mark.mak


def _snapshot():
    operations_map = build_operations_read_only_map(_snapshots(), generated_at="fixture-map")
    return build_operations_source_snapshot(operations_map, generated_at="fixture-snapshot")


def test_source_snapshot_is_valid_and_deterministically_fingerprinted():
    payload = _snapshot()

    assert validate_operations_source_snapshot(payload)
    assert len(payload["entries"]) == 24
    assert all(re.fullmatch(r"sha256:[0-9a-f]{64}", item["source_fingerprint"]) for item in payload["entries"])
    assert payload["boundary"]["contract_parity_is_not_snapshot_parity"] is True
    assert payload["control"]["execution"] is False


def test_source_snapshot_rejects_host_paths():
    payload = _snapshot()
    payload["entries"][0]["source_ref"] = "/home/mak/private.json"

    with pytest.raises(ValueError, match="absolute_or_host_path"):
        validate_operations_source_snapshot(payload)
