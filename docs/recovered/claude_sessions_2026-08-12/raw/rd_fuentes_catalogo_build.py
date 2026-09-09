from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent
GRAPH_PATH = ROOT / "rd_grafo_relaciones_2026-08-11.json"
REGISTRY_PATH = ROOT / "rd_universo_entidades_2026-08-11.json"
REAGENT_PATH = ROOT / "rd_reactivos_normalizados_2026-08-11.json"
OUTPUT_PATH = ROOT / "rd_fuentes_catalogo_2026-08-11.json"


def classify_url(url: str) -> str:
    path = urlparse(url).path.lower()
    if "/tienda/" in path:
        return "product_or_test_resource"
    if any(token in path for token in ("como-testear", "como_usar", "reactivo", "testear", "teste", "tiras")):
        return "testing_guide"
    if "/sustancias/" in path:
        return "substance_sheet"
    if any(token in path for token in ("chemsex", "mdma-y", "cocaina-y", "kit-mdma-vs")):
        return "research_or_editorial"
    return "general_source"


def canonicalize_url(url: str) -> str:
    return url.replace("https://reduciendano.cl/", "https://reduciendodano.cl/")


def add_url(catalog: dict[str, dict], url: str, source_refs: set[str], source_kind: str) -> None:
    if not url:
        return
    url = canonicalize_url(url)
    record = catalog.setdefault(url, {"url": url, "source_type": classify_url(url), "source_refs": [], "source_kinds": []})
    if source_refs:
        record["source_refs"] = sorted(set(record["source_refs"]) | source_refs)
    if source_kind:
        record["source_kinds"] = sorted(set(record["source_kinds"]) | {source_kind})


def as_urls(value: object) -> list[str]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str) and item]
    if isinstance(value, str):
        return value.split()
    return []


def main() -> None:
    graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    reagents = json.loads(REAGENT_PATH.read_text(encoding="utf-8"))
    catalog: dict[str, dict] = {}
    for item in registry["records"]:
        urls = as_urls(item.get("source_urls", []))
        for url in urls:
            add_url(catalog, url, {item["id"]}, "registry")
    for relation in graph["relations"]:
        refs = {relation["id"], relation["source_ref"], relation["target_ref"]}
        for url in relation.get("evidence_urls", []):
            add_url(catalog, url, refs, "relation")
    for reagent in reagents["reagents"]:
        refs = {"reagent:" + reagent["id"]}
        for field in ("source_url", "guide_url"):
            add_url(catalog, reagent.get(field, ""), refs, "reagent_library")
    urls = sorted(catalog.values(), key=lambda item: item["url"])
    result = {
        "schema_version": "rd-source-catalog-v0.1",
        "generated_at": "2026-08-11",
        "language": "en",
        "status": "candidate_catalog_pending_source_review",
        "principle": "A URL is a source pointer; its presence does not promote the page content to scientific certainty.",
        "source_type_values": ["substance_sheet", "testing_guide", "product_or_test_resource", "research_or_editorial", "general_source"],
        "records": urls,
        "integration_contract": {
            "registry": "A source may define or describe an entity.",
            "relation": "A source may support a relation, but the relation still carries its own status and scope limit.",
            "product": "A product URL is a resource pointer, not an automatic purchase recommendation.",
            "testing": "A guide or reagent URL describes a testing pathway; it does not establish complete sample composition.",
            "public_content": "Research and posts can be linked to a relation without becoming the relation itself."
        }
    }
    OUTPUT_PATH.write_text(json.dumps(result, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(f"wrote={OUTPUT_PATH}")
    print(f"source_records={len(urls)}")
    print("by_type=")
    for source_type in result["source_type_values"]:
        print(f"{source_type}={sum(item['source_type'] == source_type for item in urls)}")


if __name__ == "__main__":
    main()
