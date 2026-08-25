# C01 — Native provenance endpoint

## Scope and safety

This is a self-contained synthetic experiment for the native endpoint. It
uses the fixed fixture value `archive_id=artist-001`; authorship is not
inferred. The extractor reads only `fixtures/cases.json`, does not open native
source files, does not call Blender or After Effects, does not use the real
database, and has no production consumer or write path.

The contract has no `version` node kind. A version is therefore represented
as a `deliverable` node with `deliverable_id` and `version` attributes, for
example `deliverable-6:v2`. This keeps every emitted edge compatible with the
shared C01 schema.

## Changed files

All files are inside this endpoint directory:

- `native_endpoint.py` — typed nodes, contract edges, read-only fixture
  extraction, direct baseline, and activity-mediated comparison.
- `fixtures/cases.json` — synthetic cases 6, 7, and 8.
- `test_native_endpoint.py` — executable standard-library tests.
- `run_experiment.py` — JSON evidence runner for the fixture bundle.
- `REPORT.md` — this report.

No file outside `experiments/cycles/C01/native_endpoint/` was modified.

## Commands and exit codes

Run from this directory:

```text
python3 -m py_compile native_endpoint.py run_experiment.py test_native_endpoint.py
EXIT 0

python3 -m unittest -v
EXIT 1  # first run exposed a stale expected edge count in the test
EXIT 0  # after correcting that test expectation; 6 tests passed

python3 run_experiment.py
EXIT 0  # JSON contract output for all three cases

python3 -c 'from pathlib import Path; from native_endpoint import load_cases, compare_models; cases=load_cases(Path("fixtures/cases.json")); print([(r["case_id"], len(r["edges"]), len(r["direct_join"]["edges"]), len(r["mediated_links"])) for r in (compare_models(c) for c in cases)])'
EXIT 0  # case summary: 15, 14, and 7 extracted edges

python3 -c 'from collections import Counter; from pathlib import Path; from native_endpoint import load_cases, compare_models; [print(r["case_id"], dict(Counter(e["relation"] for e in r["edges"])), dict(Counter(e["status"] for e in r["edges"]))) for r in (compare_models(c) for c in load_cases(Path("fixtures/cases.json")))]'
EXIT 0  # relation/status counts independently inspected
```

The clean-fixture test copies the synthetic JSON bundle into a temporary
directory and executes the extractor there. It does not use a repository
fixture path during extraction.

## Extracted model

The input direction is explicit:

```text
source/component/authoring -> activity --generated--> deliverable(version)
                                      ^
                                      uses
deliverable(version) --derived_from--> authoring
deliverable(version) --specializes--> prior deliverable(version)
```

`uses` edges point from a declared technical input to an activity. Activities
carry `activity_type`, a complete `state_history`, final `status`, observation
references, and `read_only=true`. `generated` edges are `supported` for a
completed activity, `contradicted` for a failed activity, and `unknown` for an
activity whose final state is unknown. Every non-unknown edge has at least one
observation reference. Retrieval `score` is always `null`.

The direct baseline emits only `candidate_match` edges when a deliverable has
the explicit `declared_authoring_id` field. It does not infer a link from a
filename, extension, timestamp, archive ID, or textual similarity.

## Results by case

| Case | Technical graph | Direct join | Mediated links | Observed result |
|---|---:|---:|---:|---|
| 6 — one document, multiple versions | 10 nodes / 15 edges | 2 | 2 | One authoring document reaches `v1` and `v2` through separate render/export activity paths. `v2` has `derived_from` and `specializes(v1)`; all 5 activities are `completed`. |
| 7 — one shared source, two outputs | 10 nodes / 14 edges | 2 | 2 | The same `source-7-shared` is a technical input on both mediated paths. The direct baseline returns the two authoring/output candidates but has no place for shared-source fan-out or activity identity. |
| 8 — native graph without identifiable output | 7 nodes / 7 edges | 0 | 0 | Edit and render complete; export ends `failed`. The generated edge to `unidentified-output-8` is `contradicted`, the placeholder is explicitly unidentifiable, and the direct join leaves it unanchored. The native graph remains observable even though no output link is asserted. |

Relation counts from the extracted edges:

- Case 6: `uses=10`, `generated=2`, `derived_from=2`, `specializes=1`; all 15 statuses are `supported`.
- Case 7: `uses=10`, `generated=2`, `derived_from=2`; all 14 statuses are `supported`.
- Case 8: `uses=6`, `generated=1`; 6 are `supported` and the failed generation is `contradicted`.

## What this endpoint can observe

- Declared typed nodes for native documents, components, sources, activities,
  and identifiable or placeholder deliverables.
- Declared edit/render/export activity order, activity type, state history,
  terminal status, and observation references.
- Activity fan-out: one authoring document to multiple versioned deliverables.
- Shared technical inputs: one source used by two output paths.
- Version lineage through `derived_from` and `specializes`.
- Explicit failure, unknown, unanchored, and placeholder states without
  converting them into matches.
- Compatible C01 evidence edges with fixed archive identity and null scores.

## What this endpoint cannot observe

- Whether a real Blender/After Effects/native file exists, opens, or contains
  the declared graph; no native file is opened in this experiment.
- Whether an activity actually ran, rendered the intended pixels, or produced
  byte-identical output. There are no filesystem hashes, render previews,
  publication records, or re-encoding measurements here.
- Authorship beyond the fixed fixture `archive_id`; the extractor never
  derives authorship from a path, name, extension, or time.
- Semantic artwork identity, visual equivalence, publication-side carousel
  structure, or a public-to-local match. Those belong to the other endpoint.
- Causal truth beyond the supplied observations. The fixture declarations are
  evidence for this experiment, not proof about an external archive.

## Does the mediated model add expressive value?

Yes, for the tested technical relationships. The direct join can return the
same two authoring/output pairs in cases 6 and 7 when an explicit authoring ID
is present, but it cannot express why they are related, which edit/render/
export activities mediated the relation, that one source is shared by both
outputs, that `v2` specializes `v1`, or that an export failed without an
identifiable output.

The mediated model adds structural and state expressivity, not automatic
truth. Its `uses/generated/derived_from/specializes` edges remain only as
strong as their cited observations. In case 8 this distinction matters: the
model preserves the native activity graph and the failed generation event,
but emits no identifiable authoring-to-deliverable link. A shorter direct path
would not be evidence of a better provenance claim.

## Limits and next action

This experiment covers only C01 cases 6–8, as allowed for the native endpoint.
It does not claim integration with the public endpoint or production. The next
safe action is an independent review of the emitted edge semantics against the
other endpoint's contract before any integration; no production change is
needed for this slice.
