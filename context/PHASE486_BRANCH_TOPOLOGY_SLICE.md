# Phase 486 — Branch topology consumer slice

## Source and target

- Source evidence: source/mak at 814b74c1f5335170bf5ed1ee8c054565d6e3fc3e
- Target branch: work/mak-ownership
- Target consumer: flujo.autonomia branch-state and Git web contracts

The source copy was not rewritten. Its branch-state improvement was
reimplemented as a bounded target slice after comparison with current main.

## Changes

- src/flujo/autonomia.py now has one canonical branch, main.
- source/* is reported as source_copy, not as a canonical runtime branch.
- work/*, integration/*, codex/* and dependabot/* are temporary work.
- old department names are legacy_transition, not current authority.
- unknown remote refs are explicit unclassified blockers.
- CI and branch-audit workflow contracts target main only.
- README SVG refresh code describes the current branch topology.
- The local disabled Claude workflow is now versioned as a no-write manual
  contract; it does not activate automation.

## Verification

The command path below is normalized to the current canonical checkout; the
pass count and exit code are historical evidence from this phase.

    PYTHONPATH=src:. /home/mak/flujo/.venv/bin/pytest -q tests/test_autonomia_cli.py tests/test_git_web_contract.py tests/test_readme_svg.py

Result: 19 passed, exit 0.

    python3 -m py_compile src/flujo/autonomia.py tools/update_readme_svg.py

Result: exit 0.

## Safety

No SSH, network provider, service, database writer, WIN mutation or physical
MAK mirror write was run. The worktree remained isolated at
/tmp/mak-branch-topology. The source branch and single archive tag remain
unchanged.

## Next

Publish and merge this bounded policy slice, then select the next source copy
only after checking its physical consumer and current main parity.
