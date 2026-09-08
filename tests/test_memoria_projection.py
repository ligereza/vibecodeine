import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cultura" / "mak_research"))

import memoria


def test_limited_graph_keeps_connected_core_and_edges():
    graph = {
        "nodes": [
            {"id": "a", "sustancia": 0.1},
            {"id": "b", "sustancia": 0.8},
            {"id": "c", "sustancia": 0.2},
        ],
        "edges": [
            {"a": "a", "b": "b", "w": 0.9},
            {"a": "b", "b": "c", "w": 0.7},
        ],
    }

    limited = memoria.limitar_grafo(graph, 2)

    assert len(limited["nodes"]) == 2
    assert {node["id"] for node in limited["nodes"]} == {"b", "c"}
    assert limited["edges"] == [{"a": "b", "b": "c", "w": 0.7}]
    assert limited["projection"] == {"limit": 2, "source_nodes": 3}
