# LUNA A — Public Endpoint report

## Scope

This isolated experiment implements the public-side C01 join using only small
synthetic fixtures. It reads a declared `archive_id`; it never infers
authorship from a path, filename, timestamp, or content. It does not access
`/home/mak/WIN`, a real database, a production API, models, dependencies, or a
GPU.

The extraction adapter is read-only. Fixture creation exists only in the test
helper and writes beneath the endpoint's temporary test directory.

## Files changed

- `public_endpoint.py` — fixture extraction, exact/technical comparison,
  optional precomputed-vector retrieval, contract edges, and CLI.
- `__init__.py` — public package exports.
- `fixtures.py` — synthetic fixture builder.
- `experiments/cycles/C01/public_endpoint/tests/test_public_endpoint.py` — executable tests and clean temporary
  fixture lifecycle.
- `experiments/cycles/C01/public_endpoint/tests/__init__.py` — test package marker.
- `REPORT.md` — this report.

## Commands and exit codes

All commands were run from `experiments/cycles/C01/public_endpoint/`:

```text
python3 -m unittest discover -s tests -v
exit 0

python3 -m py_compile public_endpoint.py fixtures.py tests/test_public_endpoint.py
exit 0
```

The test suite ran 9 tests, creates and removes a clean temporary fixture for
each test, and there is no checked-in or real-data fixture. `py_compile` also
completed successfully.

## Results by case

| Case | Synthetic shape | Direct baseline result | Public endpoint state |
|---|---|---|---|
| 1 | `post` → one exported image → byte-identical deliverable | unique SHA-256 equality | `candidate_match`, `confirmed`; evidence includes both file observations |
| 2 | `reel` → re-encoded video → local deliverable | same kind/dimensions/duration, different bytes | `candidate_match`, `candidate`, method `technical`; never confirmed |
| 3 | `story` → exported image, no local deliverable | no baseline candidate | `pub-story-no-source` remains in `unmatched_publications` |
| 4 | local deliverable with no public item | no baseline candidate | `del-local-only` remains in `unmatched_deliverables` |
| 5 | `carousel` → two exported media → two deliverables | two independent exact joins | media cardinality is preserved; both matches are `confirmed` |

Cases 6–8 in the common charter concern authoring/version, shared-source,
and source-without-output provenance. They are intentionally not materialized
by this public endpoint; they belong to the native endpoint. The public-side
result therefore does not claim to observe them.

## Contract edges

The result uses `mak-cycle-c01-edge-v1`. It emits:

- `publication --contains--> source` for the declared publication/exported
  media observation, with `confirmed` status and fixture evidence;
- `source --candidate_match--> deliverable` for the media-level comparison;
- `publication --candidate_match--> deliverable` for the direct join;
- `publication --uses--> activity` and `activity --generated--> deliverable`
  only when those activity declarations are present in the fixture.

Exact equality can make a `candidate_match` edge `confirmed` only when there is
one unique exact deliverable. Technical compatibility and vector retrieval
remain `candidate`. Every emitted non-unknown edge contains at least one
`evidence_refs` value. Scores are retrieval aids only; a similarity score never
demonstrates provenance.

## Observability

This endpoint can observe declared publication type and media membership,
bytes/hash, declared technical fields, optional precomputed vectors, declared
deliverable files, explicit archive IDs, and explicit activity IDs supplied by
the fixture. It can compare a direct media join and report unmatched or
ambiguous states.

It cannot observe authorship, intent, editing history, source documents,
versions, shared native components, publication causality, or whether a local
file was actually used to publish merely because bytes or technical fields are
similar. It also cannot validate the native endpoint's activity semantics.

## Direct versus activity-mediated representation

The direct join is a one-step comparison:

```text
publication → exported media → deliverable
```

The fixture also contains explicit publication activities for the anchored
examples. The mediated representation is emitted separately as:

```text
publication --uses--> activity --generated--> deliverable
```

For the re-encoded reel, the direct result is only a technical `candidate`,
while the explicitly declared activity path is `supported` by its two
observed edges. Thus the activity-shaped representation adds expressive value
for representing an explicit production/publication event even when byte
comparison cannot confirm a match. That is not proof that the activity is true
outside the fixture, and it does not turn the technical candidate into a
provenance fact. For the exact post and carousel media, the activity path adds
structure but no stronger byte evidence than the direct confirmed match.
