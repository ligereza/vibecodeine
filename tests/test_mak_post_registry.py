import json

from cultura.mak_conductor.handler_registry import handler_for_stage
from cultura.mak_conductor.producer_catalog import catalog_by_producer


def test_post_is_a_registered_durable_boundary():
    assert "post.pipeline.build_post_package" in catalog_by_producer()
    assert handler_for_stage("post_package") is not None


def test_post_handler_keeps_human_gate_for_candidate():
    handler = handler_for_stage("post_package")
    result = handler({
        "payload_json": json.dumps({
            "spec": {
                "post_id": "post-test",
                "source_document": "source.pdf",
                "source_integrity": {
                    "source_order_preserved": True,
                    "text_blocks_preserved_verbatim": True,
                },
                "slides": [{"text_blocks": ["source"]}],
            },
        }),
    })
    assert result["validated"] is True
    assert result["result"]["public_gate"] == "human_required"
