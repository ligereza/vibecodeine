"""The routing table a fresh agent is handed has to point at files that exist.

`context/diagnostics/domains.json` is what `/api/diagnostics` and
`flujo diagnose` read to tell an agent what to open for an incident. Nothing
checked it against the tree, and measured 2026-09-02 it was a verbatim copy of
the motor's built-in defaults:

- 4 of its 23 `read_paths` did not exist in this checkout. All four were
  `src/flujo/*`, which by the two-checkout topology MAK cannot carry, and the
  report published them under `missing_read_paths` -- an absence presented as a
  finding, which is how an agent concludes a file was lost and rebuilds it.
- `core` routed the first read to the lowercase `agents.md`, the 2026-08-31
  contract, and later to `AGENTS.md`. Both are gone: the operator deleted the
  last contract file on 2026-09-05 and did not replace it.
- 1 of 10 `checks` named `tests/test_rd_informe.py`, which is not in this
  branch, and 6 more invoked `python3 -m flujo` / `python3 -m pytest`, neither
  of which resolves on this box.

These assertions are about the checkout, not the box: nothing here requires the
local virtualenv, the sibling FLUJO worktree or a running Hub, so the CI matrix
measures the same thing a laptop does.
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
    """`flujo/` is a separate worktree, excluded from this branch and absent in CI.

    Pointing a read there works on the box and vanishes everywhere else, which
    is the shape of the defect this file exists to stop. The motor's location
    belongs in the prose contract, where it is explained.
    """
    for name, cfg in _domains().items():
        for path in cfg.get("read_paths", []):
            first = Path(path).parts[0] if Path(path).parts else ""
            assert first != "flujo", (name, path)
            assert not path.startswith("src/flujo"), (name, path)


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
    """There is no contract file at the root, and `core` must not name one.

    Every contract this repository had was deleted by the operator's order:
    `CLAUDE.md`, the lowercase `agents.md` and the three
    `contracts/departments/*/agents.md` on 2026-09-03, and `AGENTS.md` itself on
    2026-09-05. Routing `core` at any of them sends an agent to a file that is
    gone, and a routed absence reads as a lost file rather than as a decision.

    Nothing replaced it on purpose. Decisions live in `DECISIONES.md`; facts are
    asked of `tools/mak_status.py`, not of a document.
    """
    core = _domains()["core"]
    assert "AGENTS.md" not in core["read_paths"], core["read_paths"]
    assert "DECISIONES.md" in core["read_paths"], core["read_paths"]
    for deleted in ("CLAUDE.md", "agents.md", "AGENTS.md",
                    "context/LAST_HANDOFF.md"):
        assert deleted not in core["read_paths"], deleted
    assert not (ROOT / "CLAUDE.md").exists(), "it was deleted, not renamed"
    assert not (ROOT / "agents.md").exists()
    # History is not a first read. Routing the record as reading turns it back
    # into state, which is exactly what renaming it was meant to stop.
    for name, cfg in _domains().items():
        assert "context/HANDOFF_HISTORICO.md" not in cfg["read_paths"], name


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
    """Two entry points differing only in case was the trap; it is gone.

    `AGENTS.md` and `agents.md` were both tracked at this root and each was
    written as the entry point, so on a case-sensitive filesystem they were two
    files and an agent could be routed to either. On 2026-09-03 the operator
    ordered every contract file deleted and one `AGENTS.md` written from zero;
    on 2026-09-05 he ordered that one deleted too.

    What this pins is the property and not the names, and the property is now
    stronger: no contract file at the root, in any case variant. Zero is a
    decision, so a new one appearing is what should fail here.
    """
    variants = sorted(path.name for path in ROOT.iterdir()
                      if path.is_file() and path.name.lower() in
                      ("agents.md", "claude.md"))
    assert variants == [], variants
    # And the departments no longer carry their own competing copies.
    assert not sorted((ROOT / "contracts").rglob("[aA][gG][eE][nN][tT][sS].md"))
