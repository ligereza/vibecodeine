# MAK System Directive

Status: **mission doctrine, dated 2026-08-25. Not in the read order.**

This file says what MAK is trying to become. It does not say what MAK currently
is, and it is not loaded by `tools/agent_bootstrap.py`. The read order is
`agents.md` -> `docs/MAK_CURRENT_STATE.md` -> `context/LAST_HANDOFF.md`; see
`docs/AUTORIDAD.md` for why this header no longer says "canonical".

Until 2026-08-28 it read "canonical direction for agents", which put it in
competition with two documents that the loader does read. Nine documents in this
repo made that same claim.

## Mission

MAK is not a single portfolio task and it is not an ARICA-specific workflow.
MAK is an autonomous, reusable operating system for artistic and cultural
archives. It must be able to ingest an arbitrary SSD, directory tree or large
archive belonging to any artist or person, learn from the evidence already
present in that archive, reconstruct works and projects over time, and compile
fit-for-purpose cultural products.

The system covers one continuous evidence chain:

```text
physical archive
  -> immutable observations and temporal memory
  -> autonomous reconstruction of works, projects and processes
  -> cultural and curatorial knowledge
  -> portfolio, application and research compilers
  -> evaluation and learning from completed outcomes
```

ARICA, ISKVW, RAYU and MYRA are cases and evidence sources. They are never the
architecture, the tenant model or the final product.

## Non-negotiable operating principles

1. The archive is the primary input. Years of completed work, exports, native
   documents, manifests, publications, references, sequences and historical
   selections are supervision already present in the archive.
2. User review is optional evidence, not a required pipeline gate. Uncertainty
   changes wording, ranking and product selection; it must not stop the system
   from completing a bounded reconstruction or draft.
3. Observation is not interpretation. A file, hash, path, timestamp or native
   reference is evidence. A work, project, phase, series or cultural claim is a
   derived hypothesis with provenance and alternatives.
4. Project IR is an interchange projection, not the authority. Immutable
   archive observations, artifact states and transformation witnesses remain
   the factual base.
5. A product compiler consumes the shared cultural model. Portfolio,
   application, research and curatorial outputs must not each reconstruct the
   archive independently.
6. Exact duplicates remain separate physical artifacts. Content identity and
   physical identity are different concepts.
7. Filesystem noise is not artistic evolution. A changed mtime without a
   semantic change does not create a new work, project or snapshot identity.
8. The system fails closed at contract boundaries, preserves uncertainty and
   never upgrades a candidate into a fact without evidence.
9. Existing implementations are reused before new frameworks are introduced.
10. Every stage must have an executable consumer, deterministic replay and an
    adversarial test. A document or status field is not integration evidence.

## Canonical architecture

### 1. Physical archive observer

`src/flujo/knowledge/archive_observer.py` performs deterministic, read-only
observation of an explicitly supplied root. It emits
`mak-archive-observation-batch-v1` with tenant-scoped physical identities,
content identities when bytes are readable, candidate structural observations
and an incremental change set.

It does not infer authorship, works, projects, series or transformations.

### 2. Temporal archive memory

`src/flujo/knowledge/archive_memory.py` validates the observer contract before
opening the database and materializes it in the existing `LearningStore`.
The additive v2 tables preserve physical artifacts, immutable states by
snapshot, candidate observations and replay. Legacy tables remain untouched.

This is the factual authority for downstream reconstruction.

### 3. Autonomous reconstruction

The next active stage must consume archive-memory replay, not rescan the source
and not require a hand-labelled gold set. It must reuse the proven concepts in
`project_reconstruction.py` and `reconstruction_adapter.py`:

- project units, subprojects, exported products, libraries and shared resources;
- directed relations with declared inverses;
- evidence for and against each decision;
- alternatives and explicit unresolved ties;
- asset assignment with balance checks;
- Project IR as a downstream projection.

Natural supervision must come from archive evidence such as explicit export
witnesses, native references, manifests, repeated delivery structures, public
manifestations, chronological states and prior completed product selections.

### 4. Operating-world model

Reconstructed units form a temporal cultural graph. Nodes may represent native
documents, components, sources, versions, phases, manifestations, deliverables,
works, projects and series. Relations must retain evidence, confidence,
alternatives and the probe that could reduce uncertainty.

### 5. Product compilers

Portfolio, application, curatorial and research compilers receive a goal and
constraints, then select and narrate from the shared model. They do not modify
the factual archive memory and do not make one case the universal template.

### 6. Evaluation and learning

Learning uses reproducible outcomes and natural archive supervision. It
evaluates reconstruction consistency, witness recovery, temporal stability,
coverage, contradiction rate and product fitness. Human corrections may be
recorded when available, but the absence of a correction never blocks the
autonomous path.

## Validated checkpoint

Stages 1 and 2A-2D are complete:

- strict observer validation occurs before database creation or writes;
- duplicate bytes at different paths remain different physical artifacts;
- directories, symlinks, special entries and failures may have null content;
- the same physical path retains identity across byte changes;
- byte changes create new snapshot states;
- mtime-only changes are idempotent and preserve the first volatile state;
- archive tenants remain isolated;
- replay produces a valid, deterministically serializable observer batch;
- schema migration is additive and legacy rows are not destroyed.

- `archive_reconstruction.py` projects strict archive-memory replay into a
  deterministic, lossless reconstruction-input vocabulary without rescanning
  the source or claiming works/projects;
- `archive_relation_inference.py` emits bounded physical and cultural relation
  candidates with declared inverses, counterevidence, alternatives, missing
  evidence and next probes;
- `archive_relation_evaluator.py` independently falsifies candidate IDs,
  endpoints, evidence refs, inverse orientation, status, score, bounds,
  diagnostics and archive isolation;
- `archive_unit_reconstruction.py` turns candidates into balanced provisional
  units while leaving shared ancestors ambiguous, physical duplicates separate,
  dependencies outside membership and every artifact explicitly assigned,
  ambiguous or unassigned;
- `archive_unit_evaluator.py` independently verifies provenance hashes, IDs,
  endpoints, membership, output-only constraints, zero truth promotion and
  exact reconciliation;
- `archive_project_ir_adapter.py` projects each balanced unit exactly once into
  a provisional `mak-project-ir-v1` record while preserving dependencies,
  uncertainty and archive provenance; its independent evaluator rejects loss,
  fabrication, truth promotion and reconciliation drift;
- a read-only MYRA run produced 10 units from 1,517 artifacts and left 192
  artifacts explicitly unassigned under the 512-candidate bound; this is
  uncertainty, not evidence of artistic non-membership;
- director acceptance on 2026-08-25: 171 focused tests across archive stages,
  Project IR, Copilot, departments, organs, Curatoria triangulation and
  Conductor passed; compilation,
  path-limited `git diff --check` and the independent end-to-end cross-smoke
  exited 0; the real source remained unchanged.

## Lessons from the three-agent integration

### Director

- Separate modules passing independently is not integration. The first real
  observer-to-memory smoke exposed incompatible schemas immediately.
- Fixing only the schema name would have preserved a false model. The decisive
  correction was separating physical identity from byte identity and moving
  changing content into snapshot state.
- Acceptance must include the inverse path: replay must satisfy the same strict
  contract that ingestion accepts.
- Independent cross-smokes are contract tests: Stage 2B and Stage 2C both
  exposed hash, field and reconciliation mismatches that isolated suites missed.
- Work must remain a bounded vertical slice while still respecting the full
  mission. The correct next step is reconstruction over memory, not a portfolio
  page and not another archive-specific experiment.

### Context integrator

- Database evolution must be additive because an earlier content-addressed
  schema cannot safely represent physical duplicates.
- Occurrences belong to snapshots. Stable candidate observation IDs may recur
  across different snapshots without becoming duplicate facts.
- Volatile ingestion time and mtime must not participate in semantic identity.
- Existing Project IR, learning ledgers and legacy tables can be preserved while
  a corrected materialization becomes canonical.
- Unit construction must be balanced before Project IR materialization. Shared
  ancestry, duplicates and missing bindings remain explicit uncertainty instead
  of being forced into convenient projects.

### Physical observer

- `artifact_id`, `physical_id` and `artifact_ref` are tenant-and-path scoped;
  `content_id` is byte scoped and may be shared.
- A path may keep physical identity while its bytes change.
- Candidate observations reference physical artifact refs and never assert an
  artistic truth.
- `change_set` is diagnostic, especially when scan limits differ; it is not an
  automatic transformation witness.
- Roots, wall-clock time and volatile mtime must not silently redefine semantic
  archive identity.

## Directed implementation plan

### Stage 2A: archive-memory projection (implemented)

Build one read-only projection from a selected archive snapshot into the
feature vocabulary required by the existing reconstruction engine. It must
preserve every artifact reference, content state, candidate observation and
snapshot provenance. No second database and no source rescan.

### Stage 2B: autonomous relation inference (implemented)

Produce ranked candidates for containment, version, component, dependency,
export/manifestation and series continuity. Each candidate must contain
positive evidence, counterevidence, alternatives, missing evidence and a stable
reason code. No mandatory user decision.

### Stage 2C: reconstructed project units (implemented)

Reuse the existing reconstruction roles and inverse-relation contract to group
artifacts into balanced project units. Libraries and shared resources remain
dependencies rather than becoming fake projects. Emit a replayable unit
reconstruction with complete assignment reconciliation.

### Stage 2D: Project IR projection and autonomous evaluation (implemented)

Project accepted units into additive Project IR records with archive-memory
provenance and no fact promotion. Independently evaluate structural invariants,
deterministic replay, assignment balance and reconciliation; then compare with
the current lexicographic/index baseline.

### Stage 3A: organism circulation (current)

Connect provisional Project IR records to MAK's existing curatorial and
department capabilities. `copilot.py` is the candidate-ranking, atlas and
bounded-learning engine; `triangular.py` and its Conductor branch provide the
reference circulation pattern from observed evidence to a sourced question and
back. Reconcile the overlapping department/organ maps through capabilities and
handoffs; do not create another registry.

### Stage 3B: cultural model and product compilers

Only after Stage 2 passes on generic fixtures and at least one bounded real
archive snapshot should Portfolio, Application, Curatorial and Research
compilers be connected. Their first output is always a goal-driven draft from
the shared model, never a hard-coded ARICA product.

## Immediate next action

Implement and independently evaluate the smallest read-only circulation bridge
from accepted Project IR records into the existing Copilot vocabulary and
Curatoria/Research evidence-gap packets. No automatic dispatch or promotion;
Portfolio and other product compilers remain disconnected.
The gate is one real pipeline:

```text
observe_archive
  -> ingest_observation_batch
  -> replay_snapshot
  -> autonomous reconstruction candidates
  -> deterministic reconstruction replay
```

The first implementation must use temporary databases and fixtures, then one
bounded real archive root read-only. It must not connect Portfolio, mutate the
production database, start services or request user labels.
