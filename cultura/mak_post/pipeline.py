#!/usr/bin/env python3
"""POST: assemble an attributed package without rewriting source content.

POST prepares Instagram posts and illustrated report packages. It does not
publish, promote, or turn an unverified editorial claim into a scientific
relation. Existing renderers and source files remain the implementation
surface; this module is only the durable department boundary and validator.
"""
from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path


REQUIRED_KEYS = (
    "post_id", "source_document", "source_integrity", "slides",
)


def load_post_spec(path: str | Path) -> dict[str, object]:
    """Load one archived POST spec without treating it as a public claim."""
    source = Path(path)
    value = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("POST spec must be a JSON object")
    return value


def validate_post_package(package: Mapping[str, object]) -> list[str]:
    """Return deterministic validation errors for a source-preserving POST."""
    errors: list[str] = []
    for key in REQUIRED_KEYS:
        if key not in package:
            errors.append("missing:%s" % key)
    integrity = package.get("source_integrity")
    if not isinstance(integrity, Mapping):
        errors.append("source_integrity:not_mapping")
    else:
        for key in ("source_order_preserved", "text_blocks_preserved_verbatim"):
            if integrity.get(key) is not True:
                errors.append("source_integrity:%s" % key)
    slides = package.get("slides")
    if not isinstance(slides, list) or not slides:
        errors.append("slides:nonempty_list_required")
    else:
        for index, slide in enumerate(slides, start=1):
            if not isinstance(slide, Mapping):
                errors.append("slide:%d:not_mapping" % index)
                continue
            if not slide.get("text_blocks"):
                errors.append("slide:%d:text_blocks_required" % index)
    return errors


def build_post_package(spec: Mapping[str, object]) -> dict[str, object]:
    """Return a validated, immutable-by-convention POST package candidate."""
    errors = validate_post_package(spec)
    return {
        "schema": "mak-post-package-v1",
        "status": "candidate" if not errors else "rejected",
        "errors": errors,
        "source": dict(spec),
        "public_gate": "human_required",
    }
