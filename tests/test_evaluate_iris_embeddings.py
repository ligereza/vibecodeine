from tools.evaluate_iris_embeddings import evaluate


def test_evaluation_never_uses_a_neighbor_from_the_same_group():
    rows = [
        {"project_id": 1, "group_key": "a", "decision": "KEEP_CANONICAL", "embedding": [1.0, 0.0]},
        {"project_id": 2, "group_key": "a", "decision": "KEEP_CANONICAL", "embedding": [1.0, 0.0]},
        {"project_id": 3, "group_key": "b", "decision": "KEEP_DERIVATIVE", "embedding": [0.9, 0.1]},
        {"project_id": 4, "group_key": "c", "decision": "KEEP_DERIVATIVE", "embedding": [0.0, 1.0]},
    ]
    report = evaluate(rows)
    assert all(
        row["group_key"] != row["neighbor_group_key"]
        for row in report["predictions"]
    )
    assert report["training_ready"] is False
    assert report["unsupported_labels"] == ["KEEP_CANONICAL"]
