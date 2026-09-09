from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
GRAPH = ROOT / "rd_grafo_relaciones_2026-08-11.json"
CATALOG = ROOT / "rd_fuentes_catalogo_2026-08-11.json"
OUTPUT = ROOT / "rd_indice_integracion_relaciones_2026-08-11.json"


def canonicalize_url(url: str) -> str:
    return url.replace("https://reduciendano.cl/", "https://reduciendodano.cl/")


def main() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    by_url = {canonicalize_url(item["url"]): item for item in catalog["records"]}
    index = []
    for relation in graph["relations"]:
        groups = {
            "rd_pages": [],
            "testing_guides": [],
            "product_resources": [],
            "research_posts": [],
            "scientific_sources": [],
            "other_sources": [],
        }
        for raw_url in relation.get("evidence_urls", []):
            url = canonicalize_url(raw_url)
            source_type = by_url.get(url, {}).get("source_type", "general_source")
            if source_type == "substance_sheet":
                groups["rd_pages"].append(url)
            elif source_type == "testing_guide":
                groups["testing_guides"].append(url)
            elif source_type == "product_or_test_resource":
                groups["product_resources"].append(url)
            elif source_type == "research_or_editorial":
                groups["research_posts"].append(url)
            elif url.startswith("https://dancesafe.org/") or url.startswith("https://testkits.nuaa.org.au/"):
                groups["scientific_sources"].append(url)
            else:
                groups["other_sources"].append(url)
        index.append({
            "relation_id": relation["id"],
            "source_ref": relation["source_ref"],
            "target_ref": relation["target_ref"],
            "relation_type": relation["relation_type"],
            "status": relation["status"],
            "matrix_relevance": relation["matrix_relevance"],
            "evidence_contract": "presumptive_presence_only" if relation["relation_type"] == "presumptive_presence_signal_for" else "context_or_relation_only",
            **{key: sorted(set(value)) for key, value in groups.items()},
            "testing_refs": relation.get("testing_refs", []),
            "notes": relation.get("notes", ""),
        })
    result = {
        "schema_version": "rd-relation-integration-index-v0.1",
        "generated_at": "2026-08-11",
        "language": "en",
        "status": "candidate_index_pending_source_review",
        "source_graph": GRAPH.name,
        "source_catalog": CATALOG.name,
        "principle": "POST, Research, web, and testing views consume this index; they do not reclassify relations or sources.",
        "records": index,
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(f"wrote={OUTPUT}")
    print(f"relations={len(index)}")
    for key in ("rd_pages", "testing_guides", "product_resources", "research_posts", "scientific_sources", "other_sources"):
        print(f"{key}={sum(bool(item[key]) for item in index)}")


if __name__ == "__main__":
    main()
