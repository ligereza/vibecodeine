# Cycle C01 — provenance-mediated archive join

## Objective

Determine whether an activity-centered provenance graph represents the
publication/production relationship better than a direct
`publication -> file` join for one artist's archive.

The artist is a fixed batch constraint, not a learned label. This cycle does
not infer authorship, reorganize files, use the real database, or change
production APIs.

## Shared edge contract

Both isolated endpoints emit compatible evidence edges:

```json
{
  "schema": "mak-cycle-c01-edge-v1",
  "archive_id": "artist-001",
  "source": {"kind": "publication|deliverable|authoring|component|source|activity", "id": "..."},
  "target": {"kind": "publication|deliverable|authoring|component|source|activity", "id": "..."},
  "relation": "uses|generated|derived_from|specializes|candidate_match|contains",
  "status": "confirmed|supported|candidate|contradicted|unknown",
  "evidence_refs": ["..."],
  "score": null,
  "extractor_version": "..."
}
```

`score` is a retrieval aid, never proof. Every non-unknown edge must cite at
least one observation. A direct join and a provenance-mediated path must be
reported separately; a shorter path is not automatically a better path.

## Frozen adversarial cases

The cycle must cover the following shapes, using small synthetic fixtures:

1. exact public export and local deliverable;
2. re-encoded public export with changed bytes;
3. public item with no local source;
4. local deliverable with no public item;
5. one publication with multiple carousel media;
6. one authoring document generating multiple deliverable versions;
7. one source shared by two outputs;
8. native document or source graph with no identifiable output.

The two endpoints may materialize only the cases relevant to their side, but
the identifiers, fixed `archive_id`, and expected relation semantics must stay
compatible.

## Acceptance gates

- writes are confined to the endpoint's own directory;
- no real archive, production API, database, or native source is modified;
- tests run from a clean temporary fixture;
- exact/technical baseline is compared with any embedding-like retrieval;
- missing, ambiguous, and unanchored states remain explicit;
- the report distinguishes observed evidence from inferred candidates;
- the result says whether the activity-centered model adds expressive value,
  not merely whether the code runs.

## Endpoint directories

- `public_endpoint/`: publication and deliverable matching;
- `native_endpoint/`: authoring, activity, version, component and source
  provenance.

The director will integrate only after both endpoint reports and tests pass.
