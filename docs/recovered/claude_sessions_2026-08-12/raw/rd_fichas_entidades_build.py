from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REGISTRY_PATH = ROOT / "rd_universo_entidades_2026-08-11.json"
GRAPH_PATH = ROOT / "rd_grafo_relaciones_2026-08-11.json"
CATALOG_PATH = ROOT / "rd_fuentes_catalogo_2026-08-11.json"
INDEX_PATH = ROOT / "rd_indice_integracion_relaciones_2026-08-11.json"
REAGENT_PATH = ROOT / "rd_reactivos_normalizados_2026-08-11.json"
JSON_OUTPUT = ROOT / "rd_fichas_entidades_2026-08-11.json"
HTML_OUTPUT = ROOT / "rd_fichas_entidades_2026-08-11.html"


def canonicalize_url(url: str) -> str:
    return url.replace("https://reduciendano.cl/", "https://reduciendodano.cl/")


def as_urls(value: object) -> list[str]:
    if isinstance(value, list):
        return [canonicalize_url(item) for item in value if isinstance(item, str) and item]
    if isinstance(value, str):
        return [canonicalize_url(item) for item in value.split()]
    return []


def ref_label(ref: str, names: dict[str, str], records: dict[str, dict]) -> str:
    if ref.startswith("reagent:"):
        return names.get(ref[8:], ref[8:])
    if ref.startswith("specific_strip:"):
        return "Specific strip: " + ref[15:]
    if ref.startswith("method:"):
        return "Method: " + ref[7:]
    return records.get(ref, {}).get("display_name", ref)


def source_groups(urls: list[str], catalog: dict[str, dict]) -> dict[str, list[str]]:
    groups = {
        "substance_sheets": [],
        "testing_guides": [],
        "product_resources": [],
        "research_posts": [],
        "scientific_sources": [],
        "other_sources": [],
    }
    mapping = {
        "substance_sheet": "substance_sheets",
        "testing_guide": "testing_guides",
        "product_or_test_resource": "product_resources",
        "research_or_editorial": "research_posts",
    }
    for raw_url in urls:
        url = canonicalize_url(raw_url)
        source_type = catalog.get(url, {}).get("source_type", "general_source")
        if source_type in mapping:
            groups[mapping[source_type]].append(url)
        elif url.startswith("https://dancesafe.org/") or url.startswith("https://testkits.nuaa.org.au/"):
            groups["scientific_sources"].append(url)
        else:
            groups["other_sources"].append(url)
    return {key: sorted(set(value)) for key, value in groups.items()}


def public_contract(test_status: str, display_name: str) -> dict[str, object]:
    if test_status in {"colorimetric_reagent", "specific_strip", "specific_non_colorimetric_test"}:
        return {
            "claim_mode": "presumptive_presence_only",
            "allowed": [
                f"Resultado compatible con presencia presumible de {display_name}.",
                f"La muestra puede contener {display_name}; el test no determina cantidad, pureza ni composicion completa.",
            ],
            "not_inferred": ["quantity", "purity", "potency", "safety", "complete_sample_composition"],
        }
    if test_status == "laboratory_only":
        return {
            "claim_mode": "laboratory_only_in_scope",
            "allowed": [f"Esta entidad queda fuera de una confirmacion de campo: {display_name}."],
            "not_inferred": ["field_presence", "quantity", "purity", "potency", "safety"],
        }
    if test_status == "no_known_test_in_scope":
        return {
            "claim_mode": "no_known_test_in_scope",
            "allowed": [f"No hay un test documentado en el alcance actual para {display_name}."],
            "not_inferred": ["presence", "absence", "quantity", "purity", "potency", "safety"],
        }
    return {
        "claim_mode": "not_reviewed",
        "allowed": [f"{display_name} permanece en el universo, pendiente de una relacion o fuente especifica."],
        "not_inferred": ["presence", "absence", "quantity", "purity", "potency", "safety"],
    }


def main() -> None:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    catalog_data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    index_data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    reagent_data = json.loads(REAGENT_PATH.read_text(encoding="utf-8"))
    records = {item["id"]: item for item in registry["records"]}
    catalog = {canonicalize_url(item["url"]): item for item in catalog_data["records"]}
    integration = {item["relation_id"]: item for item in index_data["records"]}
    reagent_names = {item["id"]: item["name"] for item in reagent_data["reagents"]}

    profiles = []
    for record in registry["records"]:
        entity_id = record["id"]
        urls = as_urls(record.get("source_urls", []))
        relations = []
        relation_types = Counter()
        relation_statuses = Counter()
        for relation in graph["relations"]:
            if relation["source_ref"] != entity_id and relation["target_ref"] != entity_id:
                continue
            if relation["source_ref"] == entity_id:
                direction = "outgoing"
                other_ref = relation["target_ref"]
            else:
                direction = "incoming"
                other_ref = relation["source_ref"]
            relation_types[relation["relation_type"]] += 1
            relation_statuses[relation["status"]] += 1
            urls.extend(as_urls(relation.get("evidence_urls", [])))
            linked = integration.get(relation["id"], {})
            relations.append({
                "relation_id": relation["id"],
                "direction": direction,
                "other_ref": other_ref,
                "other_label": ref_label(other_ref, reagent_names, records),
                "relation_type": relation["relation_type"],
                "status": relation["status"],
                "confidence": relation.get("confidence", "undeclared"),
                "matrix_relevance": relation.get("matrix_relevance", "undeclared"),
                "evidence_contract": linked.get("evidence_contract", "context_or_relation_only"),
                "notes": relation.get("notes", ""),
                "source_groups": {
                    key: linked.get(key, [])
                    for key in (
                        "rd_pages",
                        "testing_guides",
                        "product_resources",
                        "research_posts",
                        "scientific_sources",
                        "other_sources",
                    )
                },
            })
        groups = source_groups(urls, catalog)
        profiles.append({
            "id": entity_id,
            "display_name": record["display_name"],
            "aliases": record.get("aliases", ""),
            "entity_kind": record["entity_kind"],
            "matrix": record.get("matrix", False),
            "source_status": record.get("source_status", "undeclared"),
            "test_status": record.get("test_status", "not_reviewed"),
            "coverage_state": "connected" if relations else "unconnected_in_current_batch",
            "relation_count": len(relations),
            "relation_types": dict(sorted(relation_types.items())),
            "relation_statuses": dict(sorted(relation_statuses.items())),
            "source_count": len(set(urls)),
            "source_groups": groups,
            "public_contract": public_contract(record.get("test_status", "not_reviewed"), record["display_name"]),
            "relations": sorted(relations, key=lambda item: (item["other_label"], item["relation_id"])),
        })

    result = {
        "schema_version": "rd-entity-profile-index-v0.1",
        "generated_at": "2026-08-11",
        "language": "en",
        "status": "derived_profile_index_pending_public_wording_review",
        "source_registry": REGISTRY_PATH.name,
        "source_graph": GRAPH_PATH.name,
        "source_catalog": CATALOG_PATH.name,
        "source_integration_index": INDEX_PATH.name,
        "principles": [
            "Profiles are derived views, not a second source of truth.",
            "An entity may remain present without a relation or test.",
            "A test signal does not become a complete sample identity.",
            "Source groups preserve the distinction between RD pages, guides, products, research, and scientific sources.",
        ],
        "coverage": {
            "entity_count": len(profiles),
            "connected_count": sum(item["coverage_state"] == "connected" for item in profiles),
            "unconnected_count": sum(item["coverage_state"] != "connected" for item in profiles),
        },
        "profiles": profiles,
    }
    JSON_OUTPUT.write_text(json.dumps(result, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    HTML_OUTPUT.write_text(HTML_TEMPLATE.replace("__DATA__", json.dumps(result, ensure_ascii=True, separators=(",", ":"))), encoding="utf-8")
    print(f"wrote_json={JSON_OUTPUT}")
    print(f"wrote_html={HTML_OUTPUT}")
    print(f"profiles={len(profiles)} connected={result['coverage']['connected_count']} unconnected={result['coverage']['unconnected_count']}")


HTML_TEMPLATE = r'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Fichas de entidades - Reduciendo Daño</title>
<style>
:root{--bg:#08090d;--panel:#11131a;--panel2:#171a23;--line:#2b2e3b;--text:#f0f1f5;--muted:#a8adbc;--acid:#dcff36;--cyan:#58e8f2;--orange:#ffad5c;--red:#ff5f6d;--violet:#b98cff}*{box-sizing:border-box}body{margin:0;min-width:1000px;background:radial-gradient(circle at 90% 0,#12313a55,transparent 34rem),var(--bg);color:var(--text);font:14px Inter,system-ui,sans-serif}.shell{max-width:1600px;margin:auto;padding:30px 32px 60px}.eyebrow{color:var(--acid);font-size:11px;font-weight:800;letter-spacing:.25em;text-transform:uppercase}h1{font-size:clamp(36px,5vw,68px);line-height:.95;letter-spacing:-.06em;margin:12px 0}h1 span{color:var(--muted);font-weight:350}.intro{max-width:900px;color:var(--muted);font-size:16px;line-height:1.55}.contract{max-width:1050px;padding:16px 18px;margin:24px 0;border:1px solid #dcff3655;border-left:4px solid var(--acid);border-radius:12px;background:#dcff360d}.contract strong{color:var(--acid)}.contract p{margin:6px 0;line-height:1.5}.controls{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:9px;margin:22px 0 14px}.control label{display:block;color:var(--muted);font-size:10px;letter-spacing:.12em;text-transform:uppercase;margin-bottom:5px}.control input,.control select{width:100%;padding:10px;color:var(--text);background:var(--panel);border:1px solid var(--line);border-radius:8px}.layout{display:grid;grid-template-columns:minmax(400px,.85fr) minmax(500px,1.2fr);gap:14px;align-items:start}.panel{background:#11131aee;border:1px solid var(--line);border-radius:14px;overflow:hidden}.panel-head{display:flex;justify-content:space-between;padding:16px 18px;border-bottom:1px solid var(--line)}.panel-head h2{font-size:17px;margin:0}.panel-head small{color:var(--muted)}.cards{display:grid;gap:8px;padding:12px;max-height:760px;overflow:auto}.card{display:block;width:100%;text-align:left;color:var(--text);background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:12px}.card:hover,.card.selected{border-color:var(--cyan)}.card .top{display:flex;justify-content:space-between;gap:10px}.card strong{font-size:15px}.card small{display:block;color:var(--muted);line-height:1.4;margin-top:6px}.badge{color:var(--acid);font-size:10px;text-transform:uppercase;letter-spacing:.06em;white-space:nowrap}.detail{min-height:520px}.detail-body{padding:20px}.kicker{color:var(--acid);font-size:10px;letter-spacing:.15em;text-transform:uppercase;font-weight:800}.detail h2{font-size:32px;letter-spacing:-.05em;margin:7px 0}.aliases{color:var(--muted);line-height:1.45}.chips{display:flex;flex-wrap:wrap;gap:6px;margin:14px 0}.chip{padding:5px 8px;border:1px solid var(--line);border-radius:99px;color:var(--cyan);font-size:11px}.safe{border-left:3px solid var(--orange);background:#ffad5c12;padding:11px 13px;line-height:1.5}.detail dl{display:grid;grid-template-columns:130px 1fr;gap:8px;margin:18px 0;font-size:13px}.detail dt{color:var(--muted)}.detail dd{margin:0}.source-group{margin-top:18px}.source-group h4{margin:0 0 7px;color:#e9eaf0;font-size:13px}.source-group ul{margin:0;padding-left:18px;color:var(--muted);font-size:11px;line-height:1.6}.source-group a{color:var(--cyan)}.relations{display:grid;gap:8px;margin-top:18px}.relation{padding:11px;border:1px solid var(--line);border-radius:9px;background:var(--panel2)}.relation .line{display:flex;justify-content:space-between;gap:10px}.relation strong{font-size:13px}.relation small{display:block;color:var(--muted);line-height:1.45;margin-top:5px}.note{color:#dfe2e9;font-size:12px;line-height:1.45;margin-top:8px}.footer{color:#777c8b;font-size:11px;line-height:1.5;margin-top:22px}@media(max-width:1150px){.layout{grid-template-columns:1fr}}
</style></head><body><main class="shell"><div class="eyebrow">Reduciendo Daño · registro universal · fichas derivadas</div><h1>Fichas de entidad <span>una relación a la vez</span></h1><p class="intro">Cada ficha reúne una entidad, sus relaciones, sus fuentes y los límites de interpretación. No reemplaza el grafo: lo vuelve legible para la web, POST y Research.</p><section class="contract"><strong>Regla central</strong><p>Una muestra puede contener una sustancia. Una señal presumible no confirma por sí sola la identidad completa, cantidad, pureza, potencia, seguridad ni ausencia de otras sustancias.</p></section><section class="controls"><div class="control"><label>Buscar</label><input id="search" type="search" placeholder="MDMA, cannabis, reactivo..." autocomplete="off"></div><div class="control"><label>Tipo de entidad</label><select id="kind"><option value="all">Todos</option></select></div><div class="control"><label>Test</label><select id="test"><option value="all">Todos</option></select></div><div class="control"><label>Cobertura</label><select id="coverage"><option value="all">Todas</option><option value="connected">Conectadas</option><option value="unconnected_in_current_batch">Sin relación en esta tanda</option></select></div></section><section class="layout"><section class="panel"><div class="panel-head"><h2>Entidades</h2><small id="count"></small></div><div class="cards" id="cards"></div></section><aside class="panel detail" id="detail"><div class="detail-body" style="color:var(--muted);line-height:1.6">Selecciona una entidad para leer su ficha.</div></aside></section><p class="footer">Artefacto derivado de <code>rd_universo_entidades_2026-08-11.json</code>, <code>rd_grafo_relaciones_2026-08-11.json</code>, <code>rd_fuentes_catalogo_2026-08-11.json</code> y <code>rd_indice_integracion_relaciones_2026-08-11.json</code>.</p></main><script>
const data=__DATA__,profiles=data.profiles,state={search:'',kind:'all',test:'all',coverage:'all',selected:null};const labels={substance:'sustancia',substance_family:'familia',market_name_or_mixture:'nombre de mercado o mezcla',medication:'medicamento',adulterant_or_contaminant:'adulterante o contaminante',metabolite_or_precursor:'metabolito o precursor',contextual_substance:'sustancia contextual'};const tests={colorimetric_reagent:'reactivo colorimétrico',specific_strip:'tira específica',specific_non_colorimetric_test:'test específico no colorimétrico',laboratory_only:'sólo laboratorio',no_known_test_in_scope:'sin test en alcance',not_reviewed:'no revisado'};function match(p){const text=[p.id,p.display_name,p.aliases,p.entity_kind,p.test_status].join(' ').toLowerCase();return(!state.search||text.includes(state.search))&&(state.kind==='all'||p.entity_kind===state.kind)&&(state.test==='all'||p.test_status===state.test)&&(state.coverage==='all'||p.coverage_state===state.coverage)}function esc(s){return String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;')}function urlList(items){return items.length?`<ul>${items.map(u=>`<li><a href="${u}" target="_blank" rel="noreferrer">${u}</a></li>`).join('')}</ul>`:''}function detail(p){const sources=Object.entries(p.source_groups).filter(([,v])=>v.length);const relationHtml=p.relations.length?p.relations.map(r=>`<article class="relation"><div class="line"><strong>${esc(r.direction==='incoming'?'← ':'→ ')}${esc(r.other_label)}</strong><span class="badge">${esc(r.status)}</span></div><small>${esc(r.relation_type)} · ${esc(r.matrix_relevance)} · ${esc(r.confidence)}</small><div class="note">${esc(r.notes)}</div></article>`).join(''):'<p style="color:var(--muted)">Sin relación documentada en esta tanda.</p>';return`<div class="detail-body"><div class="kicker">${esc(p.id)}</div><h2>${esc(p.display_name)}</h2><div class="aliases">${esc(p.aliases||'Sin aliases registrados')}</div><div class="chips"><span class="chip">${esc(labels[p.entity_kind]||p.entity_kind)}</span><span class="chip">${esc(tests[p.test_status]||p.test_status)}</span><span class="chip">${esc(p.coverage_state)}</span><span class="chip">${p.matrix?'matriz actual':'fuera de matriz actual'}</span></div><dl><dt>Estado de fuente</dt><dd>${esc(p.source_status)}</dd><dt>Relaciones</dt><dd>${p.relation_count}</dd><dt>Fuentes</dt><dd>${p.source_count}</dd></dl><div class="safe"><b>Lenguaje permitido:</b><br>${p.public_contract.allowed.map(esc).join('<br>')}<br><br><b>No inferir:</b> ${p.public_contract.not_inferred.join(', ')}</div><div class="relations"><h3>Relaciones</h3>${relationHtml}</div>${sources.map(([k,v])=>`<section class="source-group"><h4>${esc(k.replaceAll('_',' '))} (${v.length})</h4>${urlList(v)}</section>`).join('')}</div>`}function render(){const shown=profiles.filter(match);document.getElementById('count').textContent=`${shown.length} de ${profiles.length}`;document.getElementById('cards').innerHTML=shown.length?shown.map(p=>`<button class="card ${state.selected===p.id?'selected':''}" data-id="${p.id}"><span class="top"><strong>${esc(p.display_name)}</strong><span class="badge">${esc(p.coverage_state)}</span></span><small>${esc(labels[p.entity_kind]||p.entity_kind)} · ${esc(tests[p.test_status]||p.test_status)} · ${p.relation_count} relaciones · ${p.source_count} fuentes</small></button>`).join(''):'<p style="color:var(--muted);padding:10px">No hay entidades con estos filtros.</p>';document.querySelectorAll('.card').forEach(c=>c.onclick=()=>{state.selected=c.dataset.id;const p=profiles.find(x=>x.id===state.selected);document.getElementById('detail').innerHTML=detail(p);render()})}const kinds=[...new Set(profiles.map(p=>p.entity_kind))].sort();kinds.forEach(x=>document.getElementById('kind').insertAdjacentHTML('beforeend',`<option value="${x}">${labels[x]||x}</option>`));const testsList=[...new Set(profiles.map(p=>p.test_status))].sort();testsList.forEach(x=>document.getElementById('test').insertAdjacentHTML('beforeend',`<option value="${x}">${tests[x]||x}</option>`));document.getElementById('search').oninput=e=>{state.search=e.target.value.trim().toLowerCase();render()};document.getElementById('kind').onchange=e=>{state.kind=e.target.value;render()};document.getElementById('test').onchange=e=>{state.test=e.target.value;render()};document.getElementById('coverage').onchange=e=>{state.coverage=e.target.value;render()};render();
</script></body></html>'''


if __name__ == "__main__":
    main()
