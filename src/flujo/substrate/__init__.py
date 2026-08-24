"""The minimum identity substrate: five entities, kept apart on purpose.

    Content        byte identity. Proof, and the only proof here.
    ArtifactState  one incarnation of a document.
    Lineage        documentary continuity across states whose bytes differ.
    Observation    where and when a state was seen. Plural, dated, never identity.
    Evidence       why a relation is believed. Every edge needs one.

No PROJECT, no practice model, no global classification. Those are built on top
once this substrate survives attack.
"""

from .ingest import ingest_archive, ingest_file, state_key, walk_root
from .resolution import (Absent, AmbiguousResolutionError, Many, Resolution,
                        Unique, admits, candidate_count, class_strength,
                        individuating_deficit, is_present, require_unique,
                        resolve)
from .schema import (
    AUTHORITIES,
    CROSS_DOCUMENT,
    DERIVED_FROM,
    OBSERVED_AT,
    PANTRY_COPY_OF,
    PREDICATES,
    REFERENCES,
    REVISION_IN_LINEAGE,
    SAME_CONTENT,
    SAME_LINEAGE,
    SELF_CONTINUITY,
    USES,
    ArtifactState,
    Content,
    Evidence,
    Lineage,
    Observation,
    Substrate,
    SubstrateError,
)
from .xmp import BOUNDED, EXHAUSTIVE, XmpFields, XmpResult, extract, parse_packet

__all__ = [
    "Content", "ArtifactState", "Lineage", "Observation", "Evidence", "Substrate",
    "SubstrateError", "AUTHORITIES", "PREDICATES", "SELF_CONTINUITY",
    "CROSS_DOCUMENT", "SAME_CONTENT", "SAME_LINEAGE", "DERIVED_FROM",
    "REVISION_IN_LINEAGE", "USES", "PANTRY_COPY_OF", "REFERENCES", "OBSERVED_AT",
    "ingest_file", "ingest_archive", "walk_root", "state_key",
    "extract", "parse_packet", "XmpFields", "XmpResult", "EXHAUSTIVE", "BOUNDED",
    # A resolution carries its cardinality, so an individuating claim cannot be
    # built from an ambiguous one. Exported because the alternative is every
    # caller reaching into a private path for the one type that gates the single
    # unsound step in the layer.
    "Resolution", "Unique", "Many", "Absent", "resolve", "is_present",
    "candidate_count", "admits", "require_unique", "individuating_deficit",
    "class_strength", "AmbiguousResolutionError",
]
