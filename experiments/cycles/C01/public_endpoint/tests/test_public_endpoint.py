from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from fixtures import ARCHIVE_ID, write_synthetic_fixture
from public_endpoint import (
    EDGE_SCHEMA,
    FixtureError,
    PrecomputedEmbeddingRetriever,
    compare_fixture,
    extract_fixture,
)


class PublicEndpointTests(unittest.TestCase):
    def setUp(self) -> None:
        temp_parent = Path(__file__).parents[1] / ".tmp"
        temp_parent.mkdir(exist_ok=True)
        self.temp_root = Path(tempfile.mkdtemp(prefix="c01-public-", dir=temp_parent))
        self.fixture_root = write_synthetic_fixture(self.temp_root / "fixture")
        self.extracted = extract_fixture(self.fixture_root, ARCHIVE_ID)

    def tearDown(self) -> None:
        for path in sorted(self.temp_root.rglob("*"), reverse=True):
            if path.is_file() or path.is_symlink():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
        self.temp_root.rmdir()

    def test_archive_id_is_declared_not_inferred(self) -> None:
        with self.assertRaises(FixtureError):
            extract_fixture(self.fixture_root, "artist-999")

    def test_case_1_exact_match_is_confirmed(self) -> None:
        result = compare_fixture(self.extracted)
        matches = [match for match in result.direct_matches if match.publication_id == "pub-post-exact"]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].method, "exact_sha256")
        self.assertEqual(matches[0].status, "confirmed")
        self.assertTrue(matches[0].evidence_refs)

    def test_case_2_reencode_is_technical_candidate_only(self) -> None:
        result = compare_fixture(self.extracted)
        matches = [match for match in result.direct_matches if match.publication_id == "pub-reel-reencoded"]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].method, "technical")
        self.assertEqual(matches[0].status, "candidate")
        self.assertNotEqual(matches[0].score, 1.0)
        self.assertNotIn("confirmed", {match.status for match in matches if match.method == "technical"})

    def test_case_3_public_item_without_source_is_explicit(self) -> None:
        result = compare_fixture(self.extracted)
        self.assertIn("pub-story-no-source", result.unmatched_publications)
        self.assertFalse(any(match.publication_id == "pub-story-no-source" for match in result.direct_matches))

    def test_case_4_deliverable_without_public_item_is_explicit(self) -> None:
        result = compare_fixture(self.extracted)
        self.assertIn("del-local-only", result.unmatched_deliverables)

    def test_case_5_carousel_keeps_media_cardinality(self) -> None:
        result = compare_fixture(self.extracted)
        matches = [match for match in result.direct_matches if match.publication_id == "pub-carousel"]
        self.assertEqual({match.exported_media_id for match in matches}, {"media-carousel-a", "media-carousel-b"})
        self.assertEqual({match.deliverable_id for match in matches}, {"del-carousel-a", "del-carousel-b"})
        self.assertTrue(all(match.status == "confirmed" for match in matches))

    def test_embedding_is_optional_and_never_confirms(self) -> None:
        result = compare_fixture(self.extracted, PrecomputedEmbeddingRetriever(top_k=1, minimum_score=0.8))
        self.assertTrue(result.retrieval_matches)
        self.assertTrue(all(match.status == "candidate" for match in result.retrieval_matches))
        self.assertTrue(all(match.method == "precomputed_embedding" for match in result.retrieval_matches))

    def test_activity_mediated_paths_are_separate_from_direct_join(self) -> None:
        direct = compare_fixture(self.extracted)
        mediated = {path["deliverable_id"]: path for path in direct.mediated_paths}
        self.assertEqual(set(mediated), {"del-post-exact", "del-reel-reencoded", "del-carousel-a", "del-carousel-b"})
        reel_direct = next(match for match in direct.direct_matches if match.publication_id == "pub-reel-reencoded")
        self.assertEqual(reel_direct.status, "candidate")
        self.assertEqual(mediated["del-reel-reencoded"]["path_status"], "supported")
        self.assertEqual(len(mediated["del-reel-reencoded"]["path"]), 2)

    def test_contract_edges_have_evidence_and_schema(self) -> None:
        result = compare_fixture(self.extracted, PrecomputedEmbeddingRetriever(top_k=1))
        payload = result.to_dict()
        self.assertEqual(payload["schema"], EDGE_SCHEMA)
        for edge in payload["edges"]:
            self.assertEqual(edge["schema"], EDGE_SCHEMA)
            self.assertTrue(edge["evidence_refs"])
            self.assertIn(edge["status"], {"confirmed", "supported", "candidate", "contradicted", "unknown"})
        json.dumps(payload)


if __name__ == "__main__":
    unittest.main()
