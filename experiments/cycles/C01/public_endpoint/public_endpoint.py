"""Read-only public publication/deliverable matching for cycle C01.

The module deliberately uses only the Python standard library.  It extracts
observations from a synthetic fixture directory and compares them using two
different, explicitly labelled strategies:

* exact SHA-256 equality, which can confirm an observed byte-identical match;
* technical compatibility, which can only produce a candidate;
* optional retrieval over vectors that were already supplied by the fixture.

No method in this module infers authorship or treats similarity as provenance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


EDGE_SCHEMA = "mak-cycle-c01-edge-v1"
FIXTURE_SCHEMA = "mak-cycle-c01-public-fixture-v1"
EXTRACTOR_VERSION = "public-endpoint-1.0"
PUBLICATION_TYPES = {"post", "reel", "story", "carousel"}


class FixtureError(ValueError):
    """Raised when the synthetic fixture is malformed or out of scope."""


def _refs(*groups: Iterable[str]) -> list[str]:
    """Merge evidence references deterministically without duplicates."""

    result: list[str] = []
    for group in groups:
        for ref in group:
            if ref not in result:
                result.append(ref)
    return result


def _required(mapping: Mapping[str, Any], key: str, context: str) -> Any:
    if key not in mapping:
        raise FixtureError(f"{context} is missing required field {key!r}")
    return mapping[key]


def _string_list(value: Any, context: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise FixtureError(f"{context} must be a list of strings")
    return list(value)


def _vector(value: Any, context: str) -> tuple[float, ...] | None:
    if value is None:
        return None
    if not isinstance(value, list) or not value:
        raise FixtureError(f"{context} must be a non-empty numeric list")
    try:
        vector = tuple(float(item) for item in value)
    except (TypeError, ValueError) as exc:
        raise FixtureError(f"{context} must contain only numbers") from exc
    if not all(math.isfinite(item) for item in vector):
        raise FixtureError(f"{context} must contain finite numbers")
    return vector


@dataclass(frozen=True)
class Publication:
    id: str
    kind: str
    media_ids: tuple[str, ...]
    activity_id: str | None
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class ExportedMedia:
    id: str
    publication_id: str
    archive_id: str
    path: Path
    media_kind: str
    technical: Mapping[str, Any]
    embedding: tuple[float, ...] | None
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class Deliverable:
    id: str
    archive_id: str
    path: Path
    media_kind: str
    technical: Mapping[str, Any]
    activity_id: str | None
    embedding: tuple[float, ...] | None
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class PublicationActivity:
    id: str
    publication_id: str
    deliverable_ids: tuple[str, ...]
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class ExtractedFixture:
    archive_id: str
    root: Path
    publications: tuple[Publication, ...]
    exported_media: tuple[ExportedMedia, ...]
    deliverables: tuple[Deliverable, ...]
    activities: tuple[PublicationActivity, ...]


@dataclass(frozen=True)
class Edge:
    source_kind: str
    source_id: str
    target_kind: str
    target_id: str
    relation: str
    status: str
    evidence_refs: tuple[str, ...]
    score: float | None
    extractor_version: str = EXTRACTOR_VERSION

    def to_dict(self, archive_id: str) -> dict[str, Any]:
        return {
            "schema": EDGE_SCHEMA,
            "archive_id": archive_id,
            "source": {"kind": self.source_kind, "id": self.source_id},
            "target": {"kind": self.target_kind, "id": self.target_id},
            "relation": self.relation,
            "status": self.status,
            "evidence_refs": list(self.evidence_refs),
            "score": self.score,
            "extractor_version": self.extractor_version,
        }


@dataclass(frozen=True)
class Match:
    publication_id: str
    exported_media_id: str
    deliverable_id: str
    method: str
    status: str
    score: float | None
    evidence_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "publication_id": self.publication_id,
            "exported_media_id": self.exported_media_id,
            "deliverable_id": self.deliverable_id,
            "method": self.method,
            "status": self.status,
            "score": self.score,
            "evidence_refs": list(self.evidence_refs),
        }


@dataclass(frozen=True)
class ComparisonResult:
    archive_id: str
    edges: tuple[Edge, ...]
    direct_matches: tuple[Match, ...]
    retrieval_matches: tuple[Match, ...]
    mediated_paths: tuple[dict[str, Any], ...]
    unmatched_publications: tuple[str, ...]
    unmatched_deliverables: tuple[str, ...]
    ambiguous_media: tuple[dict[str, Any], ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": EDGE_SCHEMA,
            "archive_id": self.archive_id,
            "extractor_version": EXTRACTOR_VERSION,
            "edges": [edge.to_dict(self.archive_id) for edge in self.edges],
            "direct_join": [match.to_dict() for match in self.direct_matches],
            "retrieval_join": [match.to_dict() for match in self.retrieval_matches],
            "mediated_join": list(self.mediated_paths),
            "unmatched_publications": list(self.unmatched_publications),
            "unmatched_deliverables": list(self.unmatched_deliverables),
            "ambiguous_media": list(self.ambiguous_media),
            "observability": {
                "confirmed_means": "byte-identical SHA-256 with one unique deliverable candidate",
                "candidate_means": "technical compatibility or optional precomputed-vector retrieval",
                "score_is_proof": False,
            },
        }


class PrecomputedEmbeddingRetriever:
    """Optional retrieval over fixture-provided vectors; it loads no model."""

    def __init__(self, top_k: int = 3, minimum_score: float = -1.0) -> None:
        if top_k < 1:
            raise ValueError("top_k must be positive")
        self.top_k = top_k
        self.minimum_score = minimum_score

    @staticmethod
    def cosine(left: Sequence[float], right: Sequence[float]) -> float | None:
        if len(left) != len(right):
            return None
        left_norm = math.sqrt(sum(value * value for value in left))
        right_norm = math.sqrt(sum(value * value for value in right))
        if left_norm == 0 or right_norm == 0:
            return None
        return sum(a * b for a, b in zip(left, right)) / (left_norm * right_norm)

    def retrieve(
        self,
        media: ExportedMedia,
        deliverables: Sequence[Deliverable],
    ) -> list[tuple[Deliverable, float]]:
        if media.embedding is None:
            return []
        scored: list[tuple[Deliverable, float]] = []
        for deliverable in deliverables:
            if deliverable.embedding is None:
                continue
            score = self.cosine(media.embedding, deliverable.embedding)
            if score is not None and score >= self.minimum_score:
                scored.append((deliverable, score))
        scored.sort(key=lambda pair: (-pair[1], pair[0].id))
        return scored[: self.top_k]


def _file_observations(path: Path, item_id: str) -> tuple[str, tuple[str, ...]]:
    """Read bytes and return a content observation plus its evidence ref."""

    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise FixtureError(f"cannot read fixture file for {item_id}: {path}") from exc
    digest = hashlib.sha256(payload).hexdigest()
    return digest, (f"fixture:file:{item_id}:sha256={digest}",)


def extract_fixture(root: str | Path, archive_id: str) -> ExtractedFixture:
    """Extract only declared observations from a fixture, without writing."""

    root_path = Path(root).resolve()
    manifest_path = root_path / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FixtureError(f"cannot read manifest: {manifest_path}") from exc
    if manifest.get("schema") != FIXTURE_SCHEMA:
        raise FixtureError("unsupported fixture schema")
    declared_archive_id = _required(manifest, "archive_id", "manifest")
    if declared_archive_id != archive_id:
        raise FixtureError(
            f"archive_id mismatch: requested {archive_id!r}, fixture declares {declared_archive_id!r}"
        )

    publications: list[Publication] = []
    for raw in _required(manifest, "publications", "manifest"):
        context = f"publication {raw.get('id', '<missing>')}"
        publication_id = _required(raw, "id", context)
        kind = _required(raw, "type", context)
        if kind not in PUBLICATION_TYPES:
            raise FixtureError(f"{context} has unsupported type {kind!r}")
        publications.append(
            Publication(
                id=publication_id,
                kind=kind,
                media_ids=tuple(_string_list(_required(raw, "media_ids", context), context)),
                activity_id=raw.get("activity_id"),
                evidence_refs=tuple(
                    _refs(
                        [f"fixture:publication:{publication_id}"],
                        _string_list(raw.get("evidence_refs"), context),
                    )
                ),
            )
        )

    exported_media: list[ExportedMedia] = []
    for raw in _required(manifest, "exported_media", "manifest"):
        context = f"exported media {raw.get('id', '<missing>')}"
        media_id = _required(raw, "id", context)
        media_path = root_path / _required(raw, "file", context)
        technical = _required(raw, "technical", context)
        media_archive_id = _required(raw, "archive_id", context)
        if media_archive_id != archive_id:
            raise FixtureError(
                f"{context} declares archive_id {media_archive_id!r}, expected {archive_id!r}"
            )
        exported_media.append(
            ExportedMedia(
                id=media_id,
                publication_id=_required(raw, "publication_id", context),
                archive_id=media_archive_id,
                path=media_path,
                media_kind=_required(raw, "media_kind", context),
                technical=technical,
                embedding=_vector(raw.get("embedding"), f"{context}.embedding"),
                evidence_refs=tuple(
                    _refs(
                        [f"fixture:exported_media:{media_id}"],
                        _string_list(raw.get("evidence_refs"), context),
                        _file_observations(media_path, media_id)[1],
                    )
                ),
            )
        )

    deliverables: list[Deliverable] = []
    for raw in _required(manifest, "deliverables", "manifest"):
        context = f"deliverable {raw.get('id', '<missing>')}"
        deliverable_id = _required(raw, "id", context)
        deliverable_path = root_path / _required(raw, "file", context)
        technical = _required(raw, "technical", context)
        deliverable_archive_id = _required(raw, "archive_id", context)
        if deliverable_archive_id != archive_id:
            raise FixtureError(
                f"{context} declares archive_id {deliverable_archive_id!r}, expected {archive_id!r}"
            )
        deliverables.append(
            Deliverable(
                id=deliverable_id,
                archive_id=deliverable_archive_id,
                path=deliverable_path,
                media_kind=_required(raw, "media_kind", context),
                technical=technical,
                activity_id=raw.get("activity_id"),
                embedding=_vector(raw.get("embedding"), f"{context}.embedding"),
                evidence_refs=tuple(
                    _refs(
                        [f"fixture:deliverable:{deliverable_id}"],
                        _string_list(raw.get("evidence_refs"), context),
                        _file_observations(deliverable_path, deliverable_id)[1],
                    )
                ),
            )
        )

    activities: list[PublicationActivity] = []
    for raw in manifest.get("activities", []):
        context = f"activity {raw.get('id', '<missing>')}"
        activity_id = _required(raw, "id", context)
        activities.append(
            PublicationActivity(
                id=activity_id,
                publication_id=_required(raw, "publication_id", context),
                deliverable_ids=tuple(
                    _string_list(_required(raw, "deliverable_ids", context), context)
                ),
                evidence_refs=tuple(
                    _refs(
                        [f"fixture:activity:{activity_id}"],
                        _string_list(raw.get("evidence_refs"), context),
                    )
                ),
            )
        )

    return ExtractedFixture(
        archive_id=archive_id,
        root=root_path,
        publications=tuple(publications),
        exported_media=tuple(exported_media),
        deliverables=tuple(deliverables),
        activities=tuple(activities),
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _technical_score(media: ExportedMedia, deliverable: Deliverable) -> float:
    """Technical baseline score, intentionally independent of byte content.

    The ceiling is below 1.0 because 1.0 is reserved for unique exact
    SHA-256 equality in this experiment.
    """

    if media.media_kind != deliverable.media_kind:
        return 0.0
    media_tech = media.technical
    deliverable_tech = deliverable.technical
    score = 0.0
    if media_tech.get("width") == deliverable_tech.get("width") and media_tech.get(
        "height"
    ) == deliverable_tech.get("height"):
        score += 0.70
    if "duration_ms" in media_tech or "duration_ms" in deliverable_tech:
        if media_tech.get("duration_ms") == deliverable_tech.get("duration_ms"):
            score += 0.20
    else:
        score += 0.20
    return score


def _technical_compatible(media: ExportedMedia, deliverable: Deliverable) -> bool:
    if media.media_kind != deliverable.media_kind:
        return False
    media_tech = media.technical
    deliverable_tech = deliverable.technical
    if media_tech.get("width") != deliverable_tech.get("width"):
        return False
    if media_tech.get("height") != deliverable_tech.get("height"):
        return False
    if "duration_ms" in media_tech or "duration_ms" in deliverable_tech:
        return media_tech.get("duration_ms") == deliverable_tech.get("duration_ms")
    return True


def compare_fixture(
    extracted: ExtractedFixture,
    retriever: PrecomputedEmbeddingRetriever | None = None,
) -> ComparisonResult:
    """Compare public exports with local deliverables and emit contract edges."""

    publications_by_id = {publication.id: publication for publication in extracted.publications}
    media_by_id = {media.id: media for media in extracted.exported_media}
    deliverables_by_id = {item.id: item for item in extracted.deliverables}
    activities_by_id = {activity.id: activity for activity in extracted.activities}
    if len(publications_by_id) != len(extracted.publications):
        raise FixtureError("duplicate publication id")
    if len(media_by_id) != len(extracted.exported_media):
        raise FixtureError("duplicate exported media id")
    if len(deliverables_by_id) != len(extracted.deliverables):
        raise FixtureError("duplicate deliverable id")
    if len(activities_by_id) != len(extracted.activities):
        raise FixtureError("duplicate activity id")

    edges: list[Edge] = []
    direct_matches: list[Match] = []
    retrieval_matches: list[Match] = []
    matched_deliverable_ids: set[str] = set()
    matched_publication_ids: set[str] = set()
    ambiguous_media: list[dict[str, Any]] = []

    for publication in extracted.publications:
        for media_id in publication.media_ids:
            media = media_by_id.get(media_id)
            if media is None or media.publication_id != publication.id:
                raise FixtureError(
                    f"publication {publication.id} references inconsistent media {media_id}"
                )
            edges.append(
                Edge(
                    "publication",
                    publication.id,
                    "source",
                    media.id,
                    "contains",
                    "confirmed",
                    tuple(_refs(publication.evidence_refs, media.evidence_refs)),
                    None,
                )
            )

            exact_candidates = [
                deliverable
                for deliverable in extracted.deliverables
                if deliverable.archive_id == extracted.archive_id
                and _sha256(media.path) == _sha256(deliverable.path)
            ]
            technical_candidates = [
                deliverable
                for deliverable in extracted.deliverables
                if deliverable.archive_id == extracted.archive_id
                and _technical_compatible(media, deliverable)
            ]

            if len(exact_candidates) > 1:
                ambiguous_media.append(
                    {
                        "exported_media_id": media.id,
                        "reason": "multiple_exact_deliverables",
                        "deliverable_ids": sorted(item.id for item in exact_candidates),
                    }
                )

            baseline_candidates = exact_candidates or technical_candidates
            for deliverable in baseline_candidates:
                is_unique_exact = len(exact_candidates) == 1
                method = "exact_sha256" if exact_candidates else "technical"
                status = "confirmed" if is_unique_exact else "candidate"
                score = 1.0 if exact_candidates else _technical_score(media, deliverable)
                evidence = tuple(
                    _refs(
                        media.evidence_refs,
                        deliverable.evidence_refs,
                        [
                            f"comparison:{method}:media={media.id}:deliverable={deliverable.id}"
                        ],
                    )
                )
                match = Match(
                    publication.id,
                    media.id,
                    deliverable.id,
                    method,
                    status,
                    score,
                    evidence,
                )
                direct_matches.append(match)
                edges.append(
                    Edge(
                        "source",
                        media.id,
                        "deliverable",
                        deliverable.id,
                        "candidate_match",
                        status,
                        evidence,
                        score,
                    )
                )
                edges.append(
                    Edge(
                        "publication",
                        publication.id,
                        "deliverable",
                        deliverable.id,
                        "candidate_match",
                        status,
                        evidence,
                        score,
                    )
                )
                matched_deliverable_ids.add(deliverable.id)
                matched_publication_ids.add(publication.id)

            if retriever is not None:
                for deliverable, score in retriever.retrieve(media, extracted.deliverables):
                    evidence = tuple(
                        _refs(
                            media.evidence_refs,
                            deliverable.evidence_refs,
                            [
                                f"comparison:precomputed_embedding:media={media.id}:deliverable={deliverable.id}"
                            ],
                        )
                    )
                    retrieval_match = Match(
                        publication.id,
                        media.id,
                        deliverable.id,
                        "precomputed_embedding",
                        "candidate",
                        score,
                        evidence,
                    )
                    retrieval_matches.append(retrieval_match)
                    edges.append(
                        Edge(
                            "source",
                            media.id,
                            "deliverable",
                            deliverable.id,
                            "candidate_match",
                            "candidate",
                            evidence,
                            score,
                        )
                    )

    mediated_paths: list[dict[str, Any]] = []
    for activity in extracted.activities:
        publication = publications_by_id.get(activity.publication_id)
        if publication is None:
            raise FixtureError(f"activity {activity.id} references unknown publication")
        if publication.activity_id != activity.id:
            raise FixtureError(
                f"activity {activity.id} is not declared by publication {publication.id}"
            )
        publication_activity_refs = tuple(_refs(publication.evidence_refs, activity.evidence_refs))
        publication_activity_edge = Edge(
            "publication",
            publication.id,
            "activity",
            activity.id,
            "uses",
            "confirmed",
            publication_activity_refs,
            None,
        )
        edges.append(publication_activity_edge)
        for deliverable_id in activity.deliverable_ids:
            deliverable = deliverables_by_id.get(deliverable_id)
            if deliverable is None:
                raise FixtureError(f"activity {activity.id} references unknown deliverable")
            if deliverable.activity_id != activity.id:
                raise FixtureError(
                    f"deliverable {deliverable.id} does not declare activity {activity.id}"
                )
            activity_deliverable_refs = tuple(_refs(activity.evidence_refs, deliverable.evidence_refs))
            activity_deliverable_edge = Edge(
                "activity",
                activity.id,
                "deliverable",
                deliverable.id,
                "generated",
                "confirmed",
                activity_deliverable_refs,
                None,
            )
            edges.append(activity_deliverable_edge)
            mediated_paths.append(
                {
                    "publication_id": publication.id,
                    "deliverable_id": deliverable.id,
                    "activity_id": activity.id,
                    "path": [
                        publication_activity_edge.to_dict(extracted.archive_id),
                        activity_deliverable_edge.to_dict(extracted.archive_id),
                    ],
                    "path_status": "supported",
                    "evidence_refs": list(
                        _refs(publication_activity_refs, activity_deliverable_refs)
                    ),
                }
            )

    referenced_media = {media_id for publication in extracted.publications for media_id in publication.media_ids}
    unmatched_publications = tuple(
        sorted(
            publication.id
            for publication in extracted.publications
            if publication.id not in matched_publication_ids
            or not any(media_id in referenced_media for media_id in publication.media_ids)
        )
    )
    unmatched_deliverables = tuple(
        sorted(item.id for item in extracted.deliverables if item.id not in matched_deliverable_ids)
    )
    return ComparisonResult(
        archive_id=extracted.archive_id,
        edges=tuple(edges),
        direct_matches=tuple(direct_matches),
        retrieval_matches=tuple(retrieval_matches),
        mediated_paths=tuple(mediated_paths),
        unmatched_publications=unmatched_publications,
        unmatched_deliverables=unmatched_deliverables,
        ambiguous_media=tuple(ambiguous_media),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture_dir", type=Path)
    parser.add_argument("--archive-id", required=True)
    parser.add_argument("--embedding", action="store_true", help="use only vectors already in the fixture")
    args = parser.parse_args(argv)
    extracted = extract_fixture(args.fixture_dir, args.archive_id)
    result = compare_fixture(
        extracted,
        PrecomputedEmbeddingRetriever() if args.embedding else None,
    )
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
