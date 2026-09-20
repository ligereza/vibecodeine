#!/usr/bin/env python3
"""tests/test_physical_projections.py -- the physical MAK roots must project.

Measured on 2026-08-21: six files under the active roots (/home/mak/plataforma,
/home/mak/research, /home/mak/codex) held their own diverged copy of a module
that also lives in this repository. Two of them were the ExecStart of a running
service, so the published provider retirement never reached the surface a user
actually sees: Codex on 8891 still rendered an `azure` node and Research on
8890 still drew Cerebras as the active provider with Gemini inactive.

A copy is either the canonical implementation or a thin projection of it. This
test pins that rule for the paths that were repaired, and skips cleanly on a
machine that does not carry the physical roots (a CI clone), because the rule
is about this box, not about the repository contents.
"""
import hashlib
import os
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
PHYSICAL_ROOT = Path("/home/mak")

# live path -> canonical path inside this repository
PROJECTED = {
    "plataforma/providers.py": "cultura/mak_plataforma/providers.py",
    "plataforma/copilot.py": "cultura/mak_plataforma/copilot.py",
    "plataforma/rescue_adjudicator.py": "cultura/mak_plataforma/rescue_adjudicator.py",
    "research/formato_ensayo.py": "cultura/mak_research/formato_ensayo.py",
    "research/interfaz.py": "cultura/mak_research/interfaz.py",
    "codex/interfaz_codex.py": "cultura/mak_codex/interfaz_codex.py",
}
# A projection is small on purpose: it resolves the canonical file and re-exports
# it. Anything much larger is a copy that has started to drift again.
MAX_PROJECTION_BYTES = 4096


def _physical_pairs():
    pairs = []
    for live, canonical in sorted(PROJECTED.items()):
        live_path = PHYSICAL_ROOT / live
        canonical_path = REPO / canonical
        if live_path.is_file() and canonical_path.is_file():
            pairs.append((live, live_path, canonical_path))
    return pairs


@pytest.mark.parametrize("live", sorted(PROJECTED))
def test_live_copy_is_a_projection_not_a_second_implementation(live):
    live_path = PHYSICAL_ROOT / live
    canonical_path = REPO / PROJECTED[live]
    if not live_path.is_file():
        pytest.skip(f"physical root not present on this machine: {live_path}")
    if not canonical_path.is_file():
        pytest.skip(f"canonical file absent: {canonical_path}")
    text = live_path.read_text(encoding="utf-8", errors="replace")
    size = live_path.stat().st_size
    assert size <= MAX_PROJECTION_BYTES, (
        f"{live_path} is {size} bytes: that is a second implementation, not a "
        f"projection of {canonical_path}. Re-point it at the canonical file "
        f"and archive the copy under /home/mak/_archive/.")
    assert "spec_from_file_location" in text, (
        f"{live_path} does not resolve a canonical module")
    assert str(canonical_path.name) in text, (
        f"{live_path} does not name {canonical_path.name}")


def test_no_projected_path_still_declares_a_retired_provider():
    """The whole point of the repair: retired names must not survive here."""
    pairs = _physical_pairs()
    if not pairs:
        pytest.skip("physical MAK roots are not present on this machine")
    retired = ("watsonx", "bedrock", "aws_", "azure")
    offenders = []
    for live, live_path, _canonical in pairs:
        lowered = live_path.read_text(encoding="utf-8", errors="replace").lower()
        hits = [token for token in retired if token in lowered]
        if hits:
            offenders.append(f"{live}: {hits}")
    assert not offenders, (
        "projected physical copy still names a retired provider: "
        + "; ".join(offenders))


def test_the_archived_pre_projection_copies_are_still_recoverable():
    """Evidence is preserved, not deleted: the manifest must resolve."""
    archive = PHYSICAL_ROOT / "_archive" / "shadow-copies-20260821"
    manifest = archive / "MANIFEST.json"
    if not manifest.is_file():
        pytest.skip(f"archive not present on this machine: {manifest}")
    import json

    data = json.loads(manifest.read_text(encoding="utf-8"))
    assert data["schema"] == "mak-shadow-archive-v1"
    assert len(data["entries"]) == len(PROJECTED)
    for entry in data["entries"]:
        copy = Path(entry["archived_copy"])
        assert copy.is_file(), f"archived evidence missing: {copy}"
        digest = hashlib.sha256(copy.read_bytes()).hexdigest()
        assert digest == entry["sha256_archived"], (
            f"archived copy changed after the fact: {copy}")
        assert os.path.isabs(entry["live_path"])
        assert os.path.isabs(entry["canonical_path"])
