"""Join the real C02 AEP declaration with the real C04 media observation.

This is a bounded integration runner for one explicitly named declaration and
one explicitly named artifact. It does not scan the ARICA directory and it
does not infer an export event.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
FLUJO = ROOT.parents[2]
AEP_OBSERVATION = FLUJO / "experiments/cycles/C02/aep_endpoint/observation.json"
MEDIA = Path("/home/mak/curatoria_inbox/ARICA/tottem_ojo.mp4")
MEDIA_SHA256 = "b7253320e7a23917439dd6ad2fa084a68510469517b76b6428c54f9856ca0776"
AEP_SHA256 = "99247d6506c6d1d9ce3023f4a1e044da47c806e3cd606d47b61e70fb32f5c460"
TARGET_BASENAME = "tottem_ojo.mp4"


def _imports():
    sys.path.insert(0, str(ROOT / "evidence_evaluator"))
    from evidence_evaluator import evaluate
    sys.path.insert(0, str(ROOT / "media_observer"))
    from media_observer import observe_media
    return evaluate, observe_media


def _aep_reference() -> tuple[dict[str, Any], dict[str, Any]]:
    payload = json.loads(AEP_OBSERVATION.read_text(encoding="utf-8"))
    if payload.get("input", {}).get("actual_sha256") != AEP_SHA256:
        raise ValueError("aep_digest_mismatch")
    references = payload.get("local_resolution", {}).get("references", [])
    matches = [
        reference for reference in references
        if str(reference.get("declared_basename", "")).casefold() == TARGET_BASENAME
    ]
    if len(matches) != 1:
        raise ValueError(f"expected_one_explicit_aep_reference:{len(matches)}")
    return payload, matches[0]


def build_real_evidence() -> dict[str, Any]:
    evaluate, observe_media = _imports()
    aep_payload, reference = _aep_reference()
    media_observation = observe_media(MEDIA)
    if media_observation.get("status") != "ok":
        raise RuntimeError(f"media_observation_blocked:{media_observation.get('block_reason')}")
    if media_observation.get("artifact", {}).get("sha256") != MEDIA_SHA256:
        raise ValueError("media_digest_mismatch")

    media = media_observation["media"]
    video_stream = next(
        (stream for stream in media.get("streams", []) if stream.get("type") == "video"),
        {},
    )
    evidence_input = {
        "schema": "mak-cycle-c04-evidence-input-v1",
        "case_id": "real-arica-aep-tottem-ojo",
        "native_aep": {
            "document_id": "authoring:aep:ARICA/ARICA.aep",
            "evidence_refs": [
                "C02/aep_endpoint/observation.json#/input",
                "C02/aep_endpoint/observation.json#/local_resolution/references/3",
            ],
            "declarations": [{
                "declaration_id": f"aep:fullpath:{reference['aep_record']['byte_offset']}",
                "declared_path": reference["declared_path"],
                "target_is_folder": reference.get("declared_target_is_folder", False),
                "evidence_refs": [
                    f"C02/aep_endpoint/observation.json#/local_resolution/references/3",
                    f"aep://byte-offset/{reference['aep_record']['byte_offset']}",
                ],
            }],
        },
        "local_media_observation": {
            "artifact_id": "artifact:tottem_ojo.mp4",
            "evidence_refs": [
                "C04/media_observer/real-observation",
                "C04/media_observer/sha256=b7253320e7a23917439dd6ad2fa084a68510469517b76b6428c54f9856ca0776",
            ],
            "observations": [{
                "observation_id": "media:tottem_ojo.mp4",
                "path": str(MEDIA),
                "declared_path": reference["declared_path"],
                "exists": True,
                "is_file": True,
                "sha256": media_observation["artifact"]["sha256"],
                "bytes": media_observation["artifact"]["bytes"],
                "dimensions": media.get("dimensions"),
                "streams": media.get("streams"),
                "evidence_refs": [
                    "C04/media_observer/real-observation",
                    "C04/media_observer/ffprobe-exit=0",
                ],
            }],
        },
        # No export event was observed. Leaving it absent must keep output role
        # unknown in the evaluator.
    }
    evaluation = evaluate(evidence_input)
    return {
        "schema": "mak-cycle-c04-real-evidence-v1",
        "status": "observed",
        "archive_id": "archive-arica-001",
        "source_documents": {
            "aep_sha256": AEP_SHA256,
            "aep_reference_basename": reference["declared_basename"],
            "aep_reference_offset": reference["aep_record"]["byte_offset"],
        },
        "artifact": {
            "name": MEDIA.name,
            "sha256": MEDIA_SHA256,
            "bytes": media_observation["artifact"]["bytes"],
            "dimensions": media.get("dimensions"),
            "video_codec": video_stream.get("codec"),
            "container": media.get("container"),
            "duration_seconds": media.get("duration_seconds"),
        },
        "evaluation": evaluation,
        "limits": {
            "export_event_observed": False,
            "uses_claim": evaluation["claims"]["uses"],
            "output_role_claim": evaluation["claims"]["output_role"],
            "generated_or_renders_to_relations": evaluation["relations"],
            "claim_limit": "AEP reference plus media metadata does not prove export causality",
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "real_evidence.json")
    args = parser.parse_args(argv)
    payload = build_real_evidence()
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "schema": payload["schema"],
        "status": payload["status"],
        "uses_status": payload["limits"]["uses_claim"]["status"],
        "output_role_status": payload["limits"]["output_role_claim"]["status"],
        "dimensions": payload["artifact"]["dimensions"],
        "relations": len(payload["evaluation"]["relations"]),
        "output": str(args.output),
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
