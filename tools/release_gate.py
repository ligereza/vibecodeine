#!/usr/bin/env python3
"""Decide whether the LOCAL state of /home/mak is ready for commit and push.

Scope, stated up front so the verdict cannot be over-read:

* This gate judges **local repository coherence**: branch profiles, required
  files per ref, hub boundaries, lane map readability, runtime soundness, the
  adapter dependency, and the classification of the dirty working tree.
* It does NOT run the test suite.  ``tests_deferred`` is always true and the
  push plan starts by running the tests.  ``READY_TO_PUSH`` therefore means
  "the local state is coherent and nothing blocks a commit", never "the tests
  are green".
* It performs no checkout, no commit, no push, no branch creation, no service
  restart and no write of its own.  Branch content is read with
  ``git archive`` into a temporary directory and analysed with the ``ast``
  module; nothing is executed from a ref.
* Git is version reference, not physical authority.  The remote is consulted
  only to compare SHAs.

Examples::

    python3 tools/release_gate.py --format text
    python3 tools/release_gate.py --format json
    python3 tools/release_gate.py --check
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "mak-release-gate-v1"
PHYSICAL_ROOT = Path("/home/mak")
# /home/mak/flujo is the physical FLUJO checkout, not an adapter. The old
# constant name is kept as an alias because the checkout-report helper still
# uses it.
FLUJO_CHECKOUT = "flujo"
FLUJO_SOURCE_ROOT = "flujo/src"
ADAPTER_NAME = FLUJO_CHECKOUT
REMOTE = "vibecodeine-legacy"
# Every subprocess is bounded.  A slow probe becomes a recorded TIMEOUT, never
# an implicit pass.
COMMAND_TIMEOUT = 20.0

VERDICT_READY = "READY_TO_PUSH"
VERDICT_IMPLEMENTED = "IMPLEMENTATION_COMPLETE_TESTS_DEFERRED"
VERDICT_NOT_READY = "NOT_READY"
VERDICT_UNKNOWN = "UNKNOWN_EXTERNAL"

# The precondition suites. READY_TO_PUSH requires evidence that these ran
# green; without it the honest state is IMPLEMENTATION_COMPLETE_TESTS_DEFERRED.
# The previous gate returned READY_TO_PUSH while explaining that it "never
# means the tests are green", which made the strongest word in the vocabulary
# mean the weakest thing.
PRECONDITION_SUITES = {
    "MAK": "python3 -m pytest tests/ -m mak -q",
    "FLUJO": "python3 -m pytest tests/ -m flujo -q",
}

# What each branch owns, and therefore what the other must not carry.
BRANCH_SURFACES = {
    "MAK": {
        "own_hub": "cultura/mak_plataforma/hub.py",
        "foreign_hub": "src/flujo/web/hub.py",
        "physical_root": "/home/mak",
        "foreign_entrypoint": "src/flujo/cli.py",
        "own_capabilities": "CAPACIDADES_MAK.md",
        "foreign_capabilities": "CAPACIDADES_FLUJO.md",
        "own_requirements": "requirements-mak.txt",
        "foreign_requirements": "requirements-flujo.txt",
        "own_lane": "mak",
        "foreign_lane": "flujo",
        "entrypoints": ("cultura/mak_plataforma/hub.py", "tools/runtime_preflight.py"),
    },
    "FLUJO": {
        "own_hub": "src/flujo/web/hub.py",
        "foreign_hub": "cultura/mak_plataforma/hub.py",
        "physical_root": "/home/mak/flujo",
        "foreign_entrypoint": "cultura/mak_research/interfaz.py",
        "own_capabilities": "CAPACIDADES_FLUJO.md",
        "foreign_capabilities": "CAPACIDADES_MAK.md",
        "own_requirements": "requirements-flujo.txt",
        "foreign_requirements": "requirements-mak.txt",
        "own_lane": "flujo",
        "foreign_lane": "mak",
        "entrypoints": ("src/flujo/cli.py", "src/flujo/web/hub.py"),
    },
}

SEV_OK = "ok"
SEV_INFO = "info"
SEV_DEPENDENCY = "dependency"
SEV_WARN = "warn"
SEV_BLOCKER = "blocker"
SEV_UNKNOWN = "unknown"

OPERATIONAL_BRANCHES = ("MAK", "FLUJO")
HISTORICAL_BRANCHES = ("main", "historia")
ALL_BRANCHES = OPERATIONAL_BRANCHES + HISTORICAL_BRANCHES

# An operational ref must carry the tooling that runs it.
BASELINE_REQUIRED_OPERATIONAL = (
    "branch_profile.json",
    "pyproject.toml",
    "requirements.txt",
    "tools/test_lane_map.py",
)

# A historical ref is a frozen evidence snapshot, not a deployment target.
# Demanding the current tooling from it contradicts what `kind: historical`
# means: `historia` legitimately predates tools/test_lane_map.py, and calling
# that a release blocker would be a manufactured finding.  What it must carry
# is the profile that declares it historical.
BASELINE_REQUIRED_HISTORICAL = ("branch_profile.json",)

# The two hub implementations.  Each side may consume the other's typed
# contracts; importing the other side's hub module is the boundary violation
# the branch profiles forbid.
MAK_HUB = "cultura/mak_plataforma/hub.py"
FLUJO_HUB = "src/flujo/web/hub.py"
FORBIDDEN_HUB_IMPORTS = {
    MAK_HUB: ("flujo.web.hub", "src.flujo.web.hub"),
    FLUJO_HUB: (
        "cultura.mak_plataforma.hub",
        "mak_plataforma.hub",
        "plataforma.hub",
    ),
}
# The other side's hub, given one hub path.  A ref carries both files, so the
# gate has to know which one the branch actually owns: analysing both as
# primary authority reported the MAK hub's boundary twice, once under each
# branch, and made FLUJO look responsible for MAK's imports.
OPPOSITE_HUB = {MAK_HUB: FLUJO_HUB, FLUJO_HUB: MAK_HUB}

# Files the operator owns.  They are excluded from every release plan and are
# not a branch-coherence problem: they never reach a ref.
OPERATOR_OWNED = ("inventario_mak.sh", "inventario_externo.sh")


@dataclass
class Finding:
    code: str
    severity: str
    detail: str
    evidence: str | None = None


@dataclass
class Gate:
    findings: list[Finding] = field(default_factory=list)
    data: dict[str, object] = field(default_factory=dict)

    def add(self, code: str, severity: str, detail: str, evidence: str | None = None) -> None:
        self.findings.append(Finding(code, severity, detail, evidence))

    def of(self, severity: str) -> list[Finding]:
        return [f for f in self.findings if f.severity == severity]


# ---------------------------------------------------------------- primitives


def run(command: list[str], cwd: Path | None = None, timeout: float = COMMAND_TIMEOUT) -> tuple[int, str, str]:
    """Run one bounded command.  Return code 124 marks a recorded TIMEOUT."""

    try:
        result = subprocess.run(
            command,
            cwd=str(cwd) if cwd else None,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return 124, "", f"TIMEOUT after {timeout}s: {' '.join(command)}"
    except (FileNotFoundError, OSError) as exc:
        return 127, "", str(exc)
    return result.returncode, result.stdout, result.stderr


def git(root: Path, *args: str, timeout: float = COMMAND_TIMEOUT) -> tuple[int, str, str]:
    return run(["git", "-C", str(root), *args], timeout=timeout)


def ref_sha(root: Path, ref: str) -> str | None:
    code, out, _ = git(root, "rev-parse", "--verify", "--quiet", ref)
    return out.strip() or None if code == 0 else None


def ahead_behind(root: Path, local: str, remote: str) -> dict[str, object]:
    code, out, err = git(root, "rev-list", "--left-right", "--count", f"{remote}...{local}")
    if code == 124:
        return {"behind": None, "ahead": None, "note": err}
    if code != 0:
        return {"behind": None, "ahead": None, "note": "remote ref absent"}
    parts = out.split()
    if len(parts) != 2:
        return {"behind": None, "ahead": None, "note": "unparsed rev-list output"}
    behind, ahead = int(parts[0]), int(parts[1])
    code_anc, _, _ = git(root, "merge-base", "--is-ancestor", remote, local)
    return {
        "behind": behind,
        "ahead": ahead,
        "fast_forwardable": behind == 0 and code_anc == 0,
    }


def file_in_ref(root: Path, ref: str, path: str) -> bool:
    code, _, _ = git(root, "cat-file", "-e", f"{ref}:{path}")
    return code == 0


def json_from_ref(root: Path, ref: str, path: str) -> tuple[dict[str, object] | None, str | None]:
    code, out, err = git(root, "show", f"{ref}:{path}")
    if code == 124:
        return None, err
    if code != 0:
        return None, f"{ref}:{path} not readable"
    try:
        payload = json.loads(out)
    except json.JSONDecodeError as exc:
        return None, f"{ref}:{path} is not valid JSON: {exc}"
    return payload if isinstance(payload, dict) else None, None


def archive_ref(root: Path, ref: str, paths: list[str], destination: Path) -> tuple[bool, str | None]:
    """Extract selected paths of a ref with git archive.  No checkout."""

    present = [path for path in paths if file_in_ref(root, ref, path)]
    if not present:
        return False, "none of the requested paths exist in the ref"
    destination.mkdir(parents=True, exist_ok=True)
    code, out, err = git(root, "archive", "--format=tar", f"--output={destination / 'ref.tar'}", ref, "--", *present)
    if code != 0:
        return False, err.strip() or f"git archive exited {code}"
    code, _, err = run(["tar", "-xf", str(destination / "ref.tar"), "-C", str(destination)])
    if code != 0:
        return False, err.strip() or f"tar exited {code}"
    return True, None


def imported_modules(path: Path) -> tuple[set[str], str | None]:
    """Collect every imported module name, including imports inside functions.

    The MAK hub imports its shared contracts inside try blocks, so a
    module-level-only scan would miss the very edges this gate must police.
    """

    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
    except (OSError, SyntaxError) as exc:
        return set(), str(exc)
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module and not node.level:
                modules.add(node.module)
    return modules, None


# ------------------------------------------------------------- branch profiles


def check_branch(gate: Gate, root: Path, branch: str) -> dict[str, object]:
    row: dict[str, object] = {
        "branch": branch,
        "local_sha": ref_sha(root, branch),
        "remote_ref": f"{REMOTE}/{branch}",
        "remote_sha": ref_sha(root, f"{REMOTE}/{branch}"),
        "expected_kind": "operational" if branch in OPERATIONAL_BRANCHES else "historical",
        "profile": None,
        "profile_kind": None,
        "selector": None,
        "hub_module": None,
        "hub_default_port": None,
        "required_missing": [],
    }
    if row["local_sha"] is None:
        gate.add(
            "branch_missing",
            SEV_BLOCKER,
            f"local branch {branch} does not exist",
            evidence=f"git rev-parse --verify {branch}",
        )
        return row
    row["sync"] = ahead_behind(root, branch, f"{REMOTE}/{branch}")

    profile, error = json_from_ref(root, branch, "branch_profile.json")
    if profile is None:
        gate.add(
            "branch_profile_unreadable",
            SEV_BLOCKER,
            f"{branch}: {error}",
            evidence=f"git show {branch}:branch_profile.json",
        )
        return row
    row["profile"] = profile
    declared_branch = profile.get("branch")
    kind = profile.get("kind", "runtime")
    row["profile_kind"] = kind
    row["selector"] = profile.get("default_test_selector")
    hub = profile.get("hub") if isinstance(profile.get("hub"), dict) else None
    row["hub_module"] = hub.get("module") if hub else None
    row["hub_default_port"] = hub.get("default_port") if hub else None

    if declared_branch != branch:
        gate.add(
            "profile_branch_mismatch",
            SEV_BLOCKER,
            f"{branch}: branch_profile.json declares branch={declared_branch!r}",
            evidence=f"git show {branch}:branch_profile.json",
        )

    required = list(
        BASELINE_REQUIRED_OPERATIONAL
        if branch in OPERATIONAL_BRANCHES
        else BASELINE_REQUIRED_HISTORICAL
    )
    if branch in OPERATIONAL_BRANCHES:
        if kind == "historical":
            gate.add(
                "operational_branch_marked_historical",
                SEV_BLOCKER,
                f"{branch} is an operational profile but declares kind=historical",
            )
        if not isinstance(row["selector"], str) or not row["selector"]:
            gate.add(
                "operational_selector_missing",
                SEV_BLOCKER,
                f"{branch} declares no default_test_selector",
            )
        if row["hub_module"] is None:
            gate.add(
                "operational_hub_missing",
                SEV_BLOCKER,
                f"{branch} declares no hub module",
            )
        for key in ("capabilities", "requirements"):
            value = profile.get(key)
            if isinstance(value, str) and value:
                required.append(value)
            else:
                gate.add(
                    f"profile_{key}_undeclared",
                    SEV_BLOCKER,
                    f"{branch} declares no {key} document",
                )
        if isinstance(row["hub_module"], str):
            required.append(row["hub_module"])
        # A compatibility module is a runtime projection on the box, not repo
        # material: `plataforma/` is excluded in .git/info/exclude on purpose.
        # It is verified on the physical filesystem, never demanded from a ref.
        compat = hub.get("compatibility_module") if hub else None
        if isinstance(compat, str):
            compat_path = root / compat
            row["compatibility_module"] = compat
            row["compatibility_module_on_disk"] = compat_path.is_file()
            row["compatibility_module_tracked"] = file_in_ref(root, branch, compat)
            if not compat_path.is_file():
                gate.add(
                    "compatibility_module_absent_on_disk",
                    SEV_BLOCKER,
                    f"{branch} declares compatibility module {compat}, absent from the box",
                    evidence=f"stat {compat_path}",
                )
            elif not row["compatibility_module_tracked"]:
                gate.add(
                    "compatibility_module_untracked_by_design",
                    SEV_INFO,
                    f"{branch}: {compat} exists on the box and is deliberately not tracked "
                    "in git; it is a runtime projection, not release material",
                    evidence=".git/info/exclude",
                )
        # Shared consumers are contract surfaces.  Only source files are
        # required in a ref: a declared database is a runtime artifact and is
        # gitignored, so demanding it here would be a manufactured blocker.
        # A consumed contract is not a carried file. MAK reads the motor from
        # the FLUJO checkout, so those paths are verified on the physical
        # filesystem instead of being demanded from this ref.
        for consumer in profile.get("shared_consumers", []) or []:
            if not isinstance(consumer, str) or not consumer.endswith(".py"):
                continue
            if consumer.startswith(f"{FLUJO_CHECKOUT}/"):
                if not (root / consumer).is_file():
                    gate.add(
                        "consumed_contract_absent_on_disk",
                        SEV_BLOCKER,
                        f"{branch} consumes {consumer}, absent from the FLUJO checkout",
                        evidence=f"stat {root / consumer}",
                    )
            else:
                required.append(consumer)
    else:
        if kind != "historical":
            gate.add(
                "historical_branch_not_marked",
                SEV_BLOCKER,
                f"{branch} must declare kind=historical; it declares {kind!r}",
                evidence=f"git show {branch}:branch_profile.json",
            )
        if row["selector"] is not None:
            gate.add(
                "historical_selector_declared",
                SEV_BLOCKER,
                f"{branch} is historical but declares selector {row['selector']!r}",
            )
        if row["hub_module"] is not None:
            gate.add(
                "historical_hub_declared",
                SEV_BLOCKER,
                f"{branch} is historical but declares hub {row['hub_module']!r}",
            )

    missing = [path for path in dict.fromkeys(required) if not file_in_ref(root, branch, path)]
    row["required_missing"] = missing
    row["required_checked"] = list(dict.fromkeys(required))
    if missing:
        gate.add(
            "required_files_missing",
            SEV_BLOCKER,
            f"{branch} is missing declared files: {', '.join(missing)}",
            evidence=f"git cat-file -e {branch}:<path>",
        )

    if branch in OPERATIONAL_BRANCHES and isinstance(row["selector"], str):
        check_selector(gate, root, branch, row["selector"])
    return row


def check_selector(gate: Gate, root: Path, branch: str, selector: str) -> None:
    """A selector must name a marker the ref's own pyproject registers."""

    marker = selector.replace("-m", "").strip()
    code, out, err = git(root, "show", f"{branch}:pyproject.toml")
    if code != 0:
        gate.add(
            "selector_unverifiable",
            SEV_UNKNOWN,
            f"{branch}: pyproject.toml not readable, selector {selector!r} unverified",
            evidence=err.strip() or f"git show {branch}:pyproject.toml",
        )
        return
    registered = [
        line.strip().strip('",').split(":", 1)[0].strip('"')
        for line in out.splitlines()
        if line.strip().startswith('"') and ":" in line
    ]
    if marker not in registered:
        gate.add(
            "selector_marker_unregistered",
            SEV_BLOCKER,
            f"{branch} selector {selector!r} names marker {marker!r}, "
            "which its own pyproject does not register",
            evidence=f"git show {branch}:pyproject.toml",
        )


# ----------------------------------------------------------------- hub bounds


def check_hub_boundaries(gate: Gate, root: Path, rows: list[dict[str, object]], workdir: Path) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for row in rows:
        branch = str(row["branch"])
        if branch not in OPERATIONAL_BRANCHES:
            continue
        destination = workdir / branch
        ok, error = archive_ref(root, branch, [MAK_HUB, FLUJO_HUB], destination)
        if not ok:
            gate.add(
                "hub_archive_failed",
                SEV_UNKNOWN,
                f"{branch}: could not extract the hub sources ({error})",
                evidence=f"git archive {branch} -- {MAK_HUB} {FLUJO_HUB}",
            )
            continue
        declared_consumers = set()
        profile = row.get("profile")
        if isinstance(profile, dict):
            declared_consumers = {
                str(item) for item in (profile.get("shared_consumers") or []) if isinstance(item, str)
            }
        # Only the hub the branch declares is analysed as its authority.  The
        # opposite hub is recorded as present-but-not-owned.
        declared_hub = row.get("hub_module")
        if not isinstance(declared_hub, str) or declared_hub not in FORBIDDEN_HUB_IMPORTS:
            gate.add(
                "declared_hub_unrecognised",
                SEV_UNKNOWN,
                f"{branch} declares hub {declared_hub!r}, which is not a known hub path",
            )
            continue
        opposite = OPPOSITE_HUB[declared_hub]
        results.append(
            {
                "branch": branch,
                "hub": opposite,
                "role": "present_not_owned",
                "note": "carried by the ref for the shared tree; not this branch's authority",
                "forbidden_imports_found": [],
                "undeclared_cross_imports": [],
            }
        )
        for hub_path, forbidden in ((declared_hub, FORBIDDEN_HUB_IMPORTS[declared_hub]),):
            source = destination / hub_path
            if not source.is_file():
                gate.add(
                    "declared_hub_absent_from_ref",
                    SEV_BLOCKER,
                    f"{branch} declares hub {hub_path}, absent from the ref",
                    evidence=f"git archive {branch} -- {hub_path}",
                )
                continue
            modules, error = imported_modules(source)
            if error:
                gate.add(
                    "hub_unparsable",
                    SEV_UNKNOWN,
                    f"{branch}:{hub_path} could not be parsed ({error})",
                )
                continue
            crossed = sorted(
                module
                for module in modules
                if any(module == name or module.startswith(name + ".") for name in forbidden)
            )
            # Cross-side imports that are not the other hub: allowed by the
            # transfer contract, but only the declared consumers are covered
            # by it, so the rest is reported as drift rather than silence.
            other_side = "flujo." if hub_path == MAK_HUB else "cultura."
            undeclared = sorted(
                module
                for module in modules
                if module.startswith(other_side)
                and module not in crossed
                and not any(
                    consumer.replace("src/", "").replace("/", ".").removesuffix(".py").startswith(module)
                    or module.startswith(consumer.replace("src/", "").replace("/", ".").removesuffix(".py"))
                    for consumer in declared_consumers
                )
            )
            results.append(
                {
                    "branch": branch,
                    "hub": hub_path,
                    "role": "declared_authority",
                    "forbidden_imports_found": crossed,
                    "undeclared_cross_imports": undeclared,
                }
            )
            if crossed:
                gate.add(
                    "hub_boundary_violation",
                    SEV_BLOCKER,
                    f"{branch}:{hub_path} imports the other side's hub implementation: "
                    + ", ".join(crossed),
                    evidence=f"git archive {branch} -- {hub_path} | ast",
                )
            if undeclared:
                gate.add(
                    "undeclared_cross_import",
                    SEV_WARN,
                    f"{branch}:{hub_path} imports {', '.join(undeclared)}, which the "
                    "profile's shared_consumers does not declare",
                    evidence=f"git archive {branch} -- {hub_path} | ast",
                )
    return results


# ------------------------------------------------------------------- lane map



def check_separation(gate: Gate, root: Path, branch: str, profile: dict[str, object] | None) -> dict[str, object]:
    """Measure physical separation, not the declaration of it.

    Every item here was a real defect at some point in this repository: the
    foreign Hub present in both refs, 387 of 388 test files shared, the CLI
    entrypoint declared on a branch that no longer carried it, and requirements
    that forced one branch to install the other's stack.
    """

    surface = BRANCH_SURFACES.get(branch)
    row: dict[str, object] = {"branch": branch}
    if surface is None:
        return row

    row["own_hub_present"] = file_in_ref(root, branch, surface["own_hub"])
    row["foreign_hub_present"] = file_in_ref(root, branch, surface["foreign_hub"])
    if not row["own_hub_present"]:
        gate.add("own_hub_absent", SEV_BLOCKER,
                 f"{branch} does not carry its own hub {surface['own_hub']}",
                 evidence=f"git cat-file -e {branch}:{surface['own_hub']}")
    if row["foreign_hub_present"]:
        gate.add("foreign_hub_present", SEV_BLOCKER,
                 f"{branch} still carries the other branch's hub implementation "
                 f"{surface['foreign_hub']}",
                 evidence=f"git cat-file -e {branch}:{surface['foreign_hub']}")

    missing_entrypoints = [e for e in surface["entrypoints"] if not file_in_ref(root, branch, e)]
    row["entrypoints"] = list(surface["entrypoints"])
    row["missing_entrypoints"] = missing_entrypoints
    if missing_entrypoints:
        gate.add("entrypoint_absent", SEV_BLOCKER,
                 f"{branch} declares entrypoints it does not carry: {', '.join(missing_entrypoints)}")

    row["own_capabilities_present"] = file_in_ref(root, branch, surface["own_capabilities"])
    row["foreign_capabilities_present"] = file_in_ref(root, branch, surface["foreign_capabilities"])
    row["own_requirements_present"] = file_in_ref(root, branch, surface["own_requirements"])
    row["foreign_requirements_present"] = file_in_ref(root, branch, surface["foreign_requirements"])
    if row["foreign_capabilities_present"]:
        gate.add("foreign_capabilities_present", SEV_BLOCKER,
                 f"{branch} carries {surface['foreign_capabilities']}")
    if row["foreign_requirements_present"]:
        gate.add("foreign_requirements_mixed", SEV_BLOCKER,
                 f"{branch} carries {surface['foreign_requirements']}")

    # Foreign tests: presence, not marker selection. pytest imports a module
    # before it can deselect it, so a lane marker never made a foreign test
    # harmless.
    lanes, error = json_from_ref(root, branch, "context/test_lane_map.json")
    foreign_tests: list[str] = []
    own_tests: list[str] = []
    if lanes is None:
        gate.add("lane_contract_unreadable", SEV_UNKNOWN, f"{branch}: {error}")
    else:
        assignments = lanes.get("assignments") or {}
        assert isinstance(assignments, dict)
        for path, meta in assignments.items():
            lane = meta.get("lane") if isinstance(meta, dict) else None
            if lane == surface["foreign_lane"]:
                foreign_tests.append(str(path))
            elif lane == surface["own_lane"]:
                own_tests.append(str(path))
        code, out, _ = git(root, "ls-tree", "-r", "--name-only", branch, "tests/")
        tracked = {line for line in out.splitlines() if line.endswith(".py")}
        present_foreign = sorted(set(foreign_tests) & tracked)
        row["foreign_tests_declared"] = len(foreign_tests)
        row["foreign_tests_present"] = present_foreign
        row["own_tests_declared"] = len(own_tests)
        row["test_files_tracked"] = len(tracked)
        if present_foreign:
            gate.add("foreign_tests_present", SEV_BLOCKER,
                     f"{branch} carries {len(present_foreign)} test files declared for the "
                     f"{surface['foreign_lane']} lane: {', '.join(present_foreign[:5])}"
                     + (" ..." if len(present_foreign) > 5 else ""),
                     evidence=f"git ls-tree -r {branch} tests/ vs context/test_lane_map.json")

    # Shared contracts must be declared AND neutral.
    declared = set()
    if isinstance(profile, dict):
        declared = {str(x) for x in (profile.get("shared_consumers") or []) if isinstance(x, str)}
    row["shared_consumers_declared"] = sorted(declared)
    undeclared_present: list[str] = []
    if branch == "MAK":
        # MAK must carry no motor copy at all; check_physical_layout blocks on
        # that. Anything still present here is undeclared by construction.
        code, out, _ = git(root, "ls-tree", "-r", "--name-only", branch, "src/")
        carried = [line for line in out.splitlines() if line.endswith(".py")]
        row["foreign_src_files_carried"] = len(carried)
        skeleton = {"src/flujo/__init__.py", "src/flujo/version.py"}
        for path in carried:
            if path in skeleton or path.endswith("__init__.py"):
                continue
            if path not in declared:
                undeclared_present.append(path)
        row["undeclared_shared_contracts"] = undeclared_present
        if undeclared_present:
            gate.add("undeclared_shared_contract", SEV_BLOCKER,
                     f"{branch} carries {len(undeclared_present)} src/flujo files its profile "
                     f"does not declare as shared consumers: {', '.join(undeclared_present[:5])}"
                     + (" ..." if len(undeclared_present) > 5 else ""),
                     evidence=f"git ls-tree -r {branch} src/ vs branch_profile.json shared_consumers")
    return row



def check_physical_layout(gate: Gate, root: Path) -> dict[str, object]:
    """Prove the layout decision on disk, not in a document.

    /home/mak is the MAK checkout, /home/mak/flujo is the FLUJO checkout,
    .claude/worktrees is never runtime, and MAK consumes the motor from
    /home/mak/flujo/src without copying src/flujo. Each of these was violated
    at some point today, and only the last one was visible before this check.
    """

    flujo_root = root / FLUJO_CHECKOUT
    code, out, _ = git(root, "branch", "--show-current")
    mak_branch = out.strip() if code == 0 else None
    code_f, out_f, _ = run(["git", "-C", str(flujo_root), "branch", "--show-current"])
    flujo_branch = out_f.strip() if code_f == 0 else None

    row: dict[str, object] = {
        "mak_checkout": str(root),
        "mak_branch": mak_branch,
        "flujo_checkout": str(flujo_root),
        "flujo_branch": flujo_branch,
        "flujo_source_root": str(root / FLUJO_SOURCE_ROOT),
    }
    if mak_branch != "MAK":
        gate.add("mak_checkout_not_on_mak", SEV_BLOCKER,
                 f"{root} is on {mak_branch!r}; the physical MAK checkout must be on MAK",
                 evidence=f"git -C {root} branch --show-current")
    if flujo_branch != "FLUJO":
        gate.add("flujo_checkout_not_on_flujo", SEV_BLOCKER,
                 f"{flujo_root} is on {flujo_branch!r}; it must be the FLUJO checkout",
                 evidence=f"git -C {flujo_root} branch --show-current")

    # MAK must not carry a second copy of the motor.
    code, out, _ = git(root, "ls-tree", "-r", "--name-only", "MAK", "src/")
    mak_src = [line for line in out.splitlines() if line.endswith(".py")]
    row["mak_src_files"] = len(mak_src)
    if mak_src:
        gate.add("mak_carries_a_motor_copy", SEV_BLOCKER,
                 f"MAK tracks {len(mak_src)} files under src/; it consumes the motor from "
                 f"{root / FLUJO_SOURCE_ROOT} instead of copying it",
                 evidence=f"git ls-tree -r MAK src/")

    # No live process may run from a Claude worktree, and the motor must
    # resolve inside the FLUJO checkout.
    worktree_marker = "/.claude/worktrees/"
    offenders: list[dict[str, object]] = []
    for entry in sorted(Path("/proc").iterdir()):
        if not entry.name.isdigit():
            continue
        pid = int(entry.name)
        argv = _proc_cmdline_gate(pid)
        if not argv:
            continue
        joined = " ".join(argv)
        if not any(token in joined for token in ("mak_plataforma", "mak_research", "mak_codex", "flujo")):
            continue
        try:
            cwd = os.readlink(f"/proc/{pid}/cwd")
        except OSError:
            cwd = ""
        if worktree_marker in joined or worktree_marker in cwd:
            offenders.append({"pid": pid, "cwd": cwd, "cmdline": joined})
    row["runtime_from_worktree"] = offenders
    for item in offenders:
        gate.add("runtime_from_claude_worktree", SEV_BLOCKER,
                 f"pid {item['pid']} runs from a Claude worktree (cwd={item['cwd']})",
                 evidence="/proc/<pid>/cwd and cmdline")

    # The editable hook must name the FLUJO checkout, never a stale adapter.
    hooks: list[str] = []
    for pth in sorted((root / ".venv" / "lib").glob("python3*/site-packages/*.pth")):
        try:
            for line in pth.read_text(encoding="utf-8", errors="replace").splitlines():
                if line.strip():
                    hooks.append(line.strip())
        except OSError:
            continue
    row["path_hooks"] = hooks
    motor_hooks = [h for h in hooks if h.endswith("/src") or "/flujo" in h]
    expected = str(root / FLUJO_SOURCE_ROOT)
    for hook in motor_hooks:
        if hook != expected:
            gate.add("motor_hook_outside_flujo_checkout", SEV_BLOCKER,
                     f"an editable hook resolves the motor from {hook}; expected {expected}",
                     evidence="site-packages/*.pth")
    return row


def _proc_cmdline_gate(pid: int) -> list[str]:
    try:
        raw = Path(f"/proc/{pid}/cmdline").read_bytes()
    except OSError:
        return []
    return [p.decode("utf-8", "replace") for p in raw.split(b"\0") if p]


def check_lane_map(gate: Gate, root: Path) -> dict[str, object]:
    path = root / "tools" / "test_lane_map.py"
    row: dict[str, object] = {"path": str(path), "readable": False, "lanes": [], "entries": 0}
    if not path.is_file():
        gate.add("lane_map_missing", SEV_BLOCKER, f"{path} is absent")
        return row
    # Parsed, never executed: reading the contract must have no side effect.
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
    except (OSError, SyntaxError) as exc:
        gate.add("lane_map_unparsable", SEV_BLOCKER, f"{path}: {exc}")
        return row
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not isinstance(target, ast.Name):
                continue
            if target.id == "LANES":
                try:
                    row["lanes"] = list(ast.literal_eval(node.value))
                except (ValueError, SyntaxError):
                    pass
            elif target.id == "PERSISTED_LANE_DATA":
                try:
                    data = ast.literal_eval(node.value)
                    row["entries"] = len(data)
                    counts: dict[str, int] = {}
                    for lane in data.values():
                        counts[str(lane)] = counts.get(str(lane), 0) + 1
                    row["per_lane"] = counts
                except (ValueError, SyntaxError):
                    pass
    row["readable"] = bool(row["lanes"]) and int(row["entries"]) > 0
    if not row["readable"]:
        gate.add(
            "lane_map_unreadable",
            SEV_UNKNOWN,
            f"{path} parsed but LANES or PERSISTED_LANE_DATA could not be read",
        )
    return row


# -------------------------------------------------------------------- runtime


def check_runtime(gate: Gate, root: Path) -> dict[str, object]:
    tool = root / "tools" / "runtime_preflight.py"
    row: dict[str, object] = {"tool": str(tool), "ran": False}
    if not tool.is_file():
        gate.add("runtime_preflight_missing", SEV_BLOCKER, f"{tool} is absent")
        return row
    code, out, err = run([sys.executable, str(tool), "--format", "json"], cwd=root)
    if code == 124:
        row["timeout"] = True
        gate.add("runtime_preflight_timeout", SEV_UNKNOWN, err, evidence=str(tool))
        return row
    if code != 0 or not out.strip():
        gate.add(
            "runtime_preflight_unrunnable",
            SEV_BLOCKER,
            f"{tool} exited {code}: {err.strip()[:200]}",
        )
        return row
    try:
        report = json.loads(out)
    except json.JSONDecodeError as exc:
        gate.add("runtime_preflight_output_invalid", SEV_BLOCKER, str(exc))
        return row

    row["ran"] = True
    row["schema"] = report.get("schema")
    row["summary"] = report.get("summary")
    row["conditions"] = report.get("conditions")
    row["surfaces"] = [
        {
            "surface_id": surface.get("surface_id"),
            "status": surface.get("status"),
            "declared_port": surface.get("declared_port"),
            "effective_port": surface.get("effective_port"),
            "fallback_port": surface.get("fallback_port"),
            "source_resolved": surface.get("source_resolved"),
            "import_probe": surface.get("import_probe"),
            "codes": [finding.get("code") for finding in surface.get("findings", [])],
        }
        for surface in report.get("surfaces", [])
    ]

    conditions = report.get("conditions") or {}
    if conditions.get("error"):
        gate.add(
            "runtime_error",
            SEV_BLOCKER,
            f"runtime_preflight reports {conditions['error']} surface(s) with an executed-source error",
            evidence="python3 tools/runtime_preflight.py --check",
        )
    if conditions.get("unknown"):
        gate.add(
            "runtime_unknown",
            SEV_UNKNOWN,
            f"runtime_preflight reports {conditions['unknown']} surface(s) with an unknown unit",
        )
    return row


def check_adapter_dependency(gate: Gate, root: Path, runtime: dict[str, object]) -> dict[str, object]:
    """Record how the motor is consumed, and from where.

    This used to report adapter indirection as debt. Under the layout decision
    /home/mak/flujo IS the FLUJO checkout, so consuming the motor from
    flujo/src is the contract and is reported as such. What must never
    disappear is the location: check_physical_layout blocks when a hook or a
    surface resolves the motor anywhere else.
    """

    row: dict[str, object] = {
        "adapter_path": str(root / ADAPTER_NAME),
        "role": "compatibility_adapter",
        "pth_hooks": [],
        "surfaces_depending": [],
        "port_fallbacks": [],
    }
    for pth in sorted((root / ".venv" / "lib").glob("python3*/site-packages/*.pth")):
        try:
            lines = pth.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for line in lines:
            if f"{root}/{FLUJO_SOURCE_ROOT}" in line:
                row["pth_hooks"].append({"file": str(pth), "line": line.strip()})

    for surface in runtime.get("surfaces", []) or []:
        probe = surface.get("import_probe")
        if isinstance(probe, str) and probe.startswith(f"{root}/{FLUJO_SOURCE_ROOT}/"):
            row["surfaces_depending"].append(
                {"surface_id": surface.get("surface_id"), "import_probe": probe}
            )
        if surface.get("fallback_port"):
            row["port_fallbacks"].append(
                {
                    "surface_id": surface.get("surface_id"),
                    "declared_port": surface.get("declared_port"),
                    "effective_port": surface.get("effective_port"),
                }
            )

    for hook in row["pth_hooks"]:
        gate.add(
            "motor_hook_in_flujo_checkout",
            SEV_DEPENDENCY,
            f"the editable hook resolves the motor inside the FLUJO checkout: {hook['line']}",
            evidence=hook["file"],
        )
    for surface in row["surfaces_depending"]:
        gate.add(
            "surface_consumes_flujo_checkout",
            SEV_DEPENDENCY,
            f"{surface['surface_id']} consumes the motor from the FLUJO checkout: {surface['import_probe']}",
            evidence="python3 tools/runtime_preflight.py --check --check-adapter",
        )
    for fallback in row["port_fallbacks"]:
        gate.add(
            "port_fallback_active",
            SEV_DEPENDENCY,
            f"{fallback['surface_id']} declares port {fallback['declared_port']} "
            f"but answers on {fallback['effective_port']}",
            evidence="python3 tools/runtime_preflight.py --check --strict",
        )
    if not row["pth_hooks"] and not row["surfaces_depending"] and not row["port_fallbacks"]:
        gate.add(
            "adapter_dependency_absent",
            SEV_INFO,
            "no adapter path hook, adapter-resolved surface or port fallback was measured",
        )
    return row


# ------------------------------------------------------------- working tree


# Classification is explicit.  An unmatched entry becomes unknown, because a
# release must not carry a file nobody classified.
DIRTY_RULES = (
    ("context/coordination/", "session_dossier", "coordination dossier written this session"),
    ("tools/runtime_preflight.py", "release_candidate", "runtime preflight tool"),
    ("tools/release_gate.py", "release_candidate", "this gate"),
    ("tests/test_runtime_preflight.py", "release_candidate", "tests for the preflight"),
    ("context/LAST_HANDOFF.md", "checkpoint", "single session checkpoint"),
    ("docs/MAK_CURRENT_STATE.md", "durable_doc", "current-state document"),
    ("cultura/", "operational_code", "MAK box source"),
    ("inventario_mak.sh", "operator_owned", "operator inventory script, excluded from every plan"),
    ("inventario_externo.sh", "operator_owned", "operator inventory script, excluded from every plan"),
    ("context/python_census_", "generated_data", "generated census, not release material"),
    ("context/git_history_local_", "generated_data", "generated history export, not release material"),
)


def classify_worktree(gate: Gate, root: Path) -> dict[str, object]:
    code, out, err = git(root, "status", "--porcelain")
    row: dict[str, object] = {"entries": [], "by_class": {}, "auto_included": False}
    if code == 124:
        gate.add("worktree_status_timeout", SEV_UNKNOWN, err)
        return row
    if code != 0:
        gate.add("worktree_status_failed", SEV_UNKNOWN, err.strip() or f"git status exited {code}")
        return row

    head_code, head_out, _ = git(root, "branch", "--show-current")
    head = head_out.strip() if head_code == 0 else None
    row["head_branch"] = head
    row["head_is_historical"] = head in HISTORICAL_BRANCHES

    for line in out.splitlines():
        if len(line) < 4:
            continue
        state, path = line[:2], line[3:].strip()
        kind = "untracked" if state.strip() == "??" else "tracked_modified"
        classification = None
        note = None
        for prefix, name, description in DIRTY_RULES:
            if path.startswith(prefix):
                classification, note = name, description
                break
        if classification is None:
            # A bare script or report at the repository root is exactly what
            # the repo rules forbid shipping, and it is also unclassifiable
            # release material.
            if "/" not in path.rstrip("/") and path.endswith((".sh", ".ps1", ".bat")):
                classification, note = "root_agent_script", "one-off script at the repository root"
            else:
                classification, note = "unclassified", "no rule matched this path"
        entry = {"state": state, "path": path, "kind": kind, "class": classification, "note": note}
        row["entries"].append(entry)
        counts = row["by_class"]
        assert isinstance(counts, dict)
        counts[classification] = counts.get(classification, 0) + 1

    if row["head_is_historical"] and any(
        entry["kind"] == "tracked_modified" for entry in row["entries"]
    ):
        modified = [e["path"] for e in row["entries"] if e["kind"] == "tracked_modified"]
        gate.add(
            "uncommitted_work_on_historical_branch",
            SEV_WARN,
            f"HEAD is {head}, declared kind=historical, and carries tracked modifications: "
            + ", ".join(modified)
            + ". This is checkout hygiene, not branch incoherence: none of it reaches "
            "MAK or FLUJO unless a human attributes each path.",
            evidence="git branch --show-current; git status --porcelain",
        )
    for entry in row["entries"]:
        if entry["class"] == "operator_owned":
            gate.add(
                "operator_owned_excluded",
                SEV_INFO,
                f"{entry['path']} is operator-owned and excluded from every release plan; "
                "it never reaches a ref, so it does not block a branch",
                evidence="git status --porcelain",
            )
        elif entry["class"] == "root_agent_script":
            gate.add(
                "root_agent_script_present",
                SEV_WARN,
                f"{entry['path']} is a one-off script at the repository root",
                evidence="git status --porcelain",
            )
        elif entry["class"] == "unclassified":
            gate.add(
                "unclassified_worktree_entry",
                SEV_UNKNOWN,
                f"{entry['path']} matched no classification rule",
                evidence="git status --porcelain",
            )
        elif entry["class"] == "generated_data":
            gate.add(
                "generated_data_untracked",
                SEV_WARN,
                f"{entry['path']} is generated output; it must stay out of a release",
                evidence="git status --porcelain",
            )
    return row


def build_push_plans(branches: list[dict[str, object]]) -> dict[str, object]:
    """One independent plan per operational branch, pushing itself to itself.

    The previous version produced a single plan aimed at an invented branch and
    staged whatever the checkout happened to be carrying.  A release plan is a
    property of a branch, not of the dirty tree: each operational branch pushes
    its own ref, and the working tree of `main` never decides what a branch
    ships.
    """

    plans: dict[str, object] = {}
    for row in branches:
        branch = str(row["branch"])
        if branch not in OPERATIONAL_BRANCHES:
            plans[branch] = {
                "publishable": False,
                "why": f"{branch} declares kind=historical; it is not a deployment target",
                "steps": [],
                "executed": False,
            }
            continue
        sync = row.get("sync") or {}
        plans[branch] = {
            "publishable": True,
            "target_ref": f"{REMOTE}/{branch}",
            "source_ref": branch,
            "worktree": f".claude/worktrees/{branch.lower()}-closeout",
            "sync_before_push": sync,
            "ahead": sync.get("ahead"),
            "fast_forwardable": sync.get("fast_forwardable"),
            "never": ["git add -A", "git add .", "git commit -a", "git push --force", "new branches"],
            "steps": [
                f"python3 -m pytest tests/ {row.get('selector')} -q   # deferred here; this is the missing verdict",
                f"git -C .claude/worktrees/{branch.lower()}-closeout log --oneline {REMOTE}/{branch}..{branch}",
                f"git push {REMOTE} {branch}:{branch}   # same ref to same ref, requires explicit human approval",
            ],
            "executed": False,
        }
    return plans


def classify_checkout_hygiene(worktree: dict[str, object]) -> dict[str, object]:
    """Checkout hygiene, kept apart from branch coherence.

    A dirty `main` is an operator matter.  It does not make MAK or FLUJO
    incoherent, and conflating the two is what made the first gate refuse a
    branch for a file that never reaches it.
    """

    entries = worktree.get("entries", [])
    assert isinstance(entries, list)
    buckets: dict[str, list[str]] = {}
    for entry in entries:
        buckets.setdefault(str(entry["class"]), []).append(str(entry["path"]))
    return {
        "scope": "operator checkout, not branch content",
        "affects_branch_coherence": False,
        "by_class": buckets,
        "operator_owned_excluded": [
            path for path in buckets.get("operator_owned", []) + buckets.get("root_agent_script", [])
        ],
        "generated_excluded": buckets.get("generated_data", []),
        "requires_explicit_attribution": buckets.get("release_candidate", [])
        + buckets.get("session_dossier", [])
        + buckets.get("checkpoint", [])
        + buckets.get("durable_doc", [])
        + buckets.get("operational_code", []),
    }


# ---------------------------------------------------------------- assembly


def build_report(root: Path) -> dict[str, object]:
    gate = Gate()
    workdir = Path(tempfile.mkdtemp(prefix="release_gate_"))
    try:
        branches = [check_branch(gate, root, branch) for branch in ALL_BRANCHES]
        hubs = check_hub_boundaries(gate, root, branches, workdir)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    separation = []
    for row in branches:
        if str(row["branch"]) in BRANCH_SURFACES:
            per_branch = Gate()
            separation.append(check_separation(per_branch, root, str(row["branch"]),
                                               row.get("profile")))
            row["separation_findings"] = [
                {"code": f.code, "severity": f.severity, "detail": f.detail, "evidence": f.evidence}
                for f in per_branch.findings]
            gate.findings.extend(per_branch.findings)
    physical_layout = check_physical_layout(gate, root)
    lane_map = check_lane_map(gate, root)
    runtime = check_runtime(gate, root)
    adapter = check_adapter_dependency(gate, root, runtime)
    worktree = classify_worktree(gate, root)
    push_plans = build_push_plans(branches)
    hygiene = classify_checkout_hygiene(worktree)

    blockers = gate.of(SEV_BLOCKER)
    unknowns = gate.of(SEV_UNKNOWN)

    def branch_verdict(name: str) -> str:
        rows = next((r for r in branches if r["branch"] == name), {})
        findings = rows.get("separation_findings") or []
        assert isinstance(findings, list)
        if any(f["severity"] == SEV_BLOCKER for f in findings):
            return VERDICT_NOT_READY
        if any(f["severity"] == SEV_UNKNOWN for f in findings):
            return VERDICT_UNKNOWN
        sync = rows.get("sync") or {}
        if sync.get("behind"):
            return VERDICT_UNKNOWN
        # Implementation can be complete while the precondition suite is
        # unrun. That state has its own name.
        return VERDICT_IMPLEMENTED

    verdict_mak = branch_verdict("MAK")
    verdict_flujo = branch_verdict("FLUJO")
    if blockers or VERDICT_NOT_READY in (verdict_mak, verdict_flujo):
        verdict = VERDICT_NOT_READY
    elif unknowns or VERDICT_UNKNOWN in (verdict_mak, verdict_flujo):
        verdict = VERDICT_UNKNOWN
    else:
        verdict = VERDICT_IMPLEMENTED

    return {
        "schema": SCHEMA,
        "task_id": "release-gate-20260902",
        "date": datetime.now(timezone.utc).isoformat(),
        "physical_root": str(root),
        "verdict": verdict,
        "verdict_overall": verdict,
        "verdict_MAK": verdict_mak,
        "verdict_FLUJO": verdict_flujo,
        "ready_to_push": verdict == VERDICT_READY,
        "verdict_scope": "physical and contractual separation of the operational branches, "
        "plus runtime and adapter evidence",
        "separation": separation,
        "precondition_suites": PRECONDITION_SUITES,
        "precondition_suites_executed": False,
        "tests_deferred": True,
        "tests_deferred_reason": "this gate does not run pytest; READY_TO_PUSH requires "
        "evidence that the precondition suites ran green, so the reachable state here is "
        "IMPLEMENTATION_COMPLETE_TESTS_DEFERRED",
        "branches": branches,
        "hub_boundaries": hubs,
        "physical_layout": physical_layout,
        "lane_map": lane_map,
        "runtime": runtime,
        "adapter_dependency": adapter,
        "worktree": worktree,
        "push_plans": push_plans,
        "checkout_hygiene": hygiene,
        "blockers": [
            {"code": f.code, "detail": f.detail, "evidence": f.evidence} for f in blockers
        ],
        "unknowns": [
            {"code": f.code, "detail": f.detail, "evidence": f.evidence} for f in unknowns
        ],
        "dependencies": [
            {"code": f.code, "detail": f.detail, "evidence": f.evidence}
            for f in gate.of(SEV_DEPENDENCY)
        ],
        "warnings": [
            {"code": f.code, "detail": f.detail, "evidence": f.evidence} for f in gate.of(SEV_WARN)
        ],
        "findings": [
            {"code": f.code, "severity": f.severity, "detail": f.detail, "evidence": f.evidence}
            for f in gate.findings
        ],
    }


def render_text(report: dict[str, object]) -> str:
    lines = [
        f"RESULTADO_GATE: {report['verdict']}",
        f"verdict_MAK={report['verdict_MAK']} verdict_FLUJO={report['verdict_FLUJO']} "
        f"verdict_overall={report['verdict_overall']}",
        f"{report['schema']} | root={report['physical_root']} | {report['date']}",
        f"scope: {report['verdict_scope']}",
        f"tests_deferred: {report['tests_deferred']} ({report['tests_deferred_reason']})",
        "",
        "branches:",
    ]
    for row in report["branches"]:  # type: ignore[union-attr]
        assert isinstance(row, dict)
        sync = row.get("sync") or {}
        local = (row.get("local_sha") or "-")[:12]
        remote = (row.get("remote_sha") or "-")[:12]
        lines.append(
            f"  {row['branch']:<9} kind={row.get('profile_kind')} selector={row.get('selector')} "
            f"hub={row.get('hub_module')} local={local} remote={remote} "
            f"ahead={sync.get('ahead')} behind={sync.get('behind')} "
            f"missing={row.get('required_missing') or 'none'}"
        )
    lines.append("")
    lines.append("hub boundaries:")
    for row in report["hub_boundaries"]:  # type: ignore[union-attr]
        assert isinstance(row, dict)
        lines.append(
            f"  {row['branch']}:{row['hub']} forbidden={row['forbidden_imports_found'] or 'none'} "
            f"undeclared={row['undeclared_cross_imports'] or 'none'}"
        )
    lines.append("")
    lines.append("separation:")
    for row in report["separation"]:  # type: ignore[union-attr]
        assert isinstance(row, dict)
        lines.append(
            f"  {row['branch']}: own_hub={row.get('own_hub_present')} "
            f"foreign_hub={row.get('foreign_hub_present')} "
            f"foreign_tests={len(row.get('foreign_tests_present') or [])} "
            f"tests_tracked={row.get('test_files_tracked')} "
            f"foreign_reqs={row.get('foreign_requirements_present')} "
            f"missing_entrypoints={row.get('missing_entrypoints')} "
            f"undeclared_contracts={len(row.get('undeclared_shared_contracts') or [])}"
        )
    lane_map = report["lane_map"]
    assert isinstance(lane_map, dict)
    lines.extend(
        [
            "",
            f"lane map: readable={lane_map.get('readable')} lanes={lane_map.get('lanes')} "
            f"entries={lane_map.get('entries')} per_lane={lane_map.get('per_lane')}",
        ]
    )
    runtime = report["runtime"]
    assert isinstance(runtime, dict)
    lines.append(
        f"runtime: ran={runtime.get('ran')} summary={runtime.get('summary')} "
        f"conditions={runtime.get('conditions')}"
    )
    worktree = report["worktree"]
    assert isinstance(worktree, dict)
    lines.append(
        f"worktree: head={worktree.get('head_branch')} "
        f"head_is_historical={worktree.get('head_is_historical')} "
        f"classes={worktree.get('by_class')}"
    )
    for label, key in (
        ("BLOCKERS", "blockers"),
        ("UNKNOWNS", "unknowns"),
        ("DEPENDENCIES", "dependencies"),
        ("WARNINGS", "warnings"),
    ):
        rows = report[key]
        assert isinstance(rows, list)
        lines.append("")
        lines.append(f"{label} ({len(rows)}):")
        for item in rows:
            assert isinstance(item, dict)
            lines.append(f"  - {item['code']}: {item['detail']}")
            if item.get("evidence"):
                lines.append(f"      evidence: {item['evidence']}")
    hygiene = report["checkout_hygiene"]
    assert isinstance(hygiene, dict)
    lines.extend(
        [
            "",
            f"checkout hygiene ({hygiene['scope']}, affects_branch_coherence="
            f"{hygiene['affects_branch_coherence']}):",
            f"  operator_owned excluded: {hygiene['operator_owned_excluded']}",
            f"  generated excluded:      {hygiene['generated_excluded']}",
            f"  needs attribution:       {hygiene['requires_explicit_attribution']}",
            "",
            "push plans (NOT executed, one per branch):",
        ]
    )
    plans = report["push_plans"]
    assert isinstance(plans, dict)
    for branch, plan in plans.items():
        assert isinstance(plan, dict)
        if not plan.get("publishable"):
            lines.append(f"  {branch}: not publishable -- {plan.get('why')}")
            continue
        lines.append(
            f"  {branch} -> {plan['target_ref']} ahead={plan.get('ahead')} "
            f"fast_forwardable={plan.get('fast_forwardable')} worktree={plan.get('worktree')}"
        )
        for step in plan["steps"]:
            lines.append(f"      step: {step}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=PHYSICAL_ROOT)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit 1 when a blocker exists, 2 when an unknown remains, 0 when ready",
    )
    args = parser.parse_args(argv)

    root = Path(os.path.realpath(args.root))
    report = build_report(root)

    if args.format == "json":
        sys.stdout.write(json.dumps(report, ensure_ascii=True, indent=2) + "\n")
    else:
        sys.stdout.write(render_text(report))

    if args.check:
        if report["verdict"] == VERDICT_NOT_READY:
            return 1
        if report["verdict"] == VERDICT_UNKNOWN:
            return 2
        if report["verdict"] == VERDICT_IMPLEMENTED:
            # Not a failure: implementation is complete and the precondition
            # suites are still owed. A distinct code so a caller can tell it
            # apart from a fully green READY_TO_PUSH.
            return 5
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
