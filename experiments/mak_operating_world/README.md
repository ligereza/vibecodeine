# MAK operating-world experiment

This is an isolated, read-only experiment. It does not change
`data/mak_knowledge.db`, the production router, the learning policy, or any
active state.

## Question

Can MAK represent and derive a validated multi-step operating plan from
Project IR and episode evidence, or is a one-label `tool_id` decision enough?

The experiment runs both conceptions over the same six Project IR cases:

- current `route_project` and current categorical learner;
- a typed capability graph with preconditions, effects, validator references,
  cost/risk fields, composition and explicit capability gaps.

The world-model registry is deliberately small. Its observed phase cards come
from verified episodes. The typed preconditions/effects are benchmark contracts
because the current ledger does not contain them formally; the report marks
`research.publish` as `observed_phase_available: false` for that reason.

## What the current data can represent

Project IR exposes identity, state, purpose, source, domains, artifacts,
unknowns, evidence and provenance. Verified episodes expose phase, action,
observation, outcome, validation, provider, model, cost, source references and
tool identity.

The current data does not yet provide a typed goal schema, formal positive or
negative effects, capability inputs/outputs, validated duration/risk costs,
causal dependencies, failure probabilities or independent validators for
unseen compositions. The experiment reports these gaps rather than inferring
them silently.

## Run

    PYTHONPATH=src .venv/bin/python -m experiments.mak_operating_world.run_experiment \
      --db data/mak_knowledge.db \
      --cases experiments/mak_operating_world/cases.json

The command reads the database using SQLite `mode=ro` and prints a JSON report.
The test suite is:

    .venv/bin/python -m pytest -q tests/test_operating_world_experiment.py

## Interpretation rule

This is architectural evidence, not a statistical claim. A compositional
planner wins only if it reaches the declared goal or explains the missing
precondition, while the current selector cannot express the multi-step plan.
The adversarial cases require a license fact or a rendering capability that is
not declared; guessing a tool is a failure.

## Result from the real database

Verified 2026-08-24 against `data/mak_knowledge.db`:

- `6` cases evaluated; `2` expected capability gaps.
- Typed world-model planner: `6/6` contract cases passed.
- Current router: `3/6` direct/safe cases; `0` gaps were explained as a missing
  precondition.
- Current learner: `2/6`; it correctly expressed only the two single-step
  cases and produced `research_job_router` for the blocked publication case.
- The planner produced five-step and four-step research plans, and reported
  `license_approved` plus `publication_permitted` as unreachable in the
  publication case.
- The learner/router comparison is architectural, not statistical: the typed
  preconditions/effects are benchmark contracts because the real ledger lacks
  them formally.

The isolated tests passed (`3 passed`) and the full repository suite passed
(`EXIT 0`). The database SHA-256, size and modification time were identical
before and after the experiment.
