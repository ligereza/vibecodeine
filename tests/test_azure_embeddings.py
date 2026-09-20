import json

from cultura.mak_plataforma import azure_embeddings


class _Response:
    headers = {"x-request-id": "req-test"}

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, _limit):
        return json.dumps({
            "model": "text-embedding-3-small",
            "data": [
                {"index": 1, "embedding": [0.3, 0.4]},
                {"index": 0, "embedding": [0.1, 0.2]},
            ],
            "usage": {"prompt_tokens": 4, "total_tokens": 4},
        }).encode()


def test_credit_guard_is_closed_by_default(monkeypatch):
    monkeypatch.delenv("MAK_AZURE_ALLOW_CREDIT", raising=False)
    result = azure_embeddings.embed(["evidence"])
    assert result["available"] is False
    assert result["error"] == "azure_credit_guard_blocked"


def test_embeddings_preserve_input_order_without_returning_text(monkeypatch):
    monkeypatch.setenv("MAK_AZURE_ALLOW_CREDIT", "1")
    monkeypatch.setattr(azure_embeddings, "token_for", lambda _resource: "token")
    monkeypatch.setattr(azure_embeddings.urllib.request, "urlopen", lambda *_args, **_kwargs: _Response())
    result = azure_embeddings.embed(["first", "second"])
    assert result["available"] is True
    assert result["vectors"] == [[0.1, 0.2], [0.3, 0.4]]
    assert result["dimensions"] == 2
    assert "texts" not in result


def test_embedding_text_excludes_decision_and_decision_reason():
    from tools.iris_azure_embeddings import _embedding_text

    text = _embedding_text({
        "project_rel_root": "svg/example",
        "project_kind": "framework_project",
        "origin_class": "repository_backed",
        "structure_class": "monorepo",
        "decision": "KEEP_CANONICAL",
        "reason": "secret target explanation",
        "evidence": {
            "reasons": [{"message": "observable source evidence"}],
            "package_summary": {"classes": {"monorepo": 1}},
            "cluster_summary": {"cluster_count": 0},
            "history_summary": {"available": True},
        },
    })
    assert "KEEP_CANONICAL" not in text
    assert "secret target explanation" not in text
    assert "observable source evidence" in text
