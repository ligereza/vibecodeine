"""The routing table a fresh agent receives must point at current, existing sources.

The core bootstrap is deliberately small: `AGENTS.md` -> `REAL_INFO.md`.
Historical handoffs, PHASE reports and compatibility redirects must never be
first-read context. The remaining routed paths are implementation evidence for
the diagnosed domain and must exist in the checkout.
"""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).parents[1]
DOMAINS = ROOT / "context" / "diagnostics" / "domains.json"


def _domains():
    data = json.loads(DOMAINS.read_text(encoding="utf-8"))
    domains = data.get("domains")
    assert isinstance(domains, dict) and domains, "the map must declare domains"
    return domains


def test_every_routed_read_path_exists_in_this_checkout():
    """A routed path that is not there reads as a deleted file, not as topology."""
    missing = {}
    for name, cfg in _domains().items():
        absent = [path for path in cfg.get("read_paths", [])
                  if not (ROOT / path).exists()]
        if absent:
            missing[name] = absent
    assert not missing, "routed read_paths absent from the checkout: %s" % missing


def test_no_domain_routes_a_read_into_the_sibling_motor_checkout():
    """Do not route through a machine-specific sibling checkout spelling.

    Integrated main carries `src/flujo` locally. A top-level `flujo/` path is
    a workstation topology detail and is not portable CI context.
    """
    for name, cfg in _domains().items():
        for path in cfg.get("read_paths", []):
            first = Path(path).parts[0] if Path(path).parts else ""
            assert first != "flujo", (name, path)
            # Integrated main carries the FLUJO source tree locally; only the
            # sibling checkout spelling is forbidden here.


def test_every_domain_contract_file_exists():
    for name, cfg in _domains().items():
        contract = cfg.get("contract", "")
        assert contract, "%s declares no contract" % name
        assert (ROOT / contract).is_file(), (name, contract)


def test_a_declared_check_never_names_a_test_file_this_branch_lacks():
    """`python3 -m pytest -q tests/test_rd_informe.py` was routed advice for a
    file that is not here. A check an agent cannot run is worse than none: it
    reads as a broken suite instead of a stale instruction."""
    for name, cfg in _domains().items():
        for check in cfg.get("checks", []):
            for token in check.split():
                if token.startswith("tests/") and token.endswith(".py"):
                    assert (ROOT / token).is_file(), (name, check, token)


def test_the_core_domain_routes_to_the_only_contract_that_exists():
    """Core starts from the single contract and the durable current model."""
    core = _domains()["core"]
    assert core["read_paths"][:2] == ["AGENTS.md", "REAL_INFO.md"], core["read_paths"]
    assert (ROOT / "AGENTS.md").is_file()
    assert (ROOT / "REAL_INFO.md").is_file()

    for retired in (
        "CLAUDE.md",
        "agents.md",
        "DECISIONES.md",
        "context/LAST_HANDOFF.md",
        "context/HANDOFF_HISTORICO.md",
        "HISTORICO.md",
    ):
        assert retired not in core["read_paths"], retired

    assert not (ROOT / "CLAUDE.md").exists()
    assert not (ROOT / "agents.md").exists()

    for name, cfg in _domains().items():
        assert "context/HANDOFF_HISTORICO.md" not in cfg["read_paths"], name
        assert "HISTORICO.md" not in cfg["read_paths"], name

def test_no_domain_tells_an_agent_to_avoid_a_machine_that_is_gone():
    """`WIN raw archive` sat in all five `do_not_read` lists.

    There is no Windows node: the operator confirmed on 2026-09-03 that it was
    an old computer and is gone. An instruction to avoid a surface that does
    not exist teaches the topology wrong, and the real bulk surface to keep out
    of a first read is the mounted SSD.
    """
    for name, cfg in _domains().items():
        avoid = cfg.get("do_not_read", [])
        assert avoid, "%s must still declare what to keep out of a first read" % name
        for entry in avoid:
            assert "WIN" not in entry, (name, entry)
            assert "Windows" not in entry, (name, entry)


def test_there_is_exactly_one_contract_file_and_no_case_variant():
    """Exactly one root agent contract exists, with no case-variant competitor."""
    variants = sorted(
        path.name
        for path in ROOT.iterdir()
        if path.is_file() and path.name.lower() in ("agents.md", "claude.md")
    )
    assert variants == ["AGENTS.md"], variants
    assert not sorted((ROOT / "contracts").rglob("[aA][gG][eE][nN][tT][sS].md"))
