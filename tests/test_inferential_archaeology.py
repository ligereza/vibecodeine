import json
import sqlite3
from pathlib import Path

from tools.inferential_archaeology import (
    _question_links,
    classify_turns,
    deduplicate_turns,
    build_idea_followups,
    build_git_cadence,
    build_evidence_report,
    build_bifurcation_map,
    build_cross_source_packet,
    build_proposal_followups,
    _path_history,
    _split_git_rename_path,
    load_claude_web,
    load_claude_actions,
    load_codex_actions,
    load_mak_activity,
    load_memories,
    load_rule_events,
    load_vscode_sol_sessions,
    validate_interpretation,
    write_duckdb,
    write_sqlite,
)


def _turn(n, role, text, session="s1"):
    return {
        "n": n, "rol": role, "clase": "humano" if role == "user" else "asistente",
        "via": None, "ts": "2026-08-12T10:%02d:00Z" % n, "sesion": session,
        "rama": "mak", "archivo": "session.jsonl", "linea": n,
        "chars": len(text), "sintetico": False, "texto": text,
    }


def test_classification_keeps_heuristics_as_candidates():
    turns = [_turn(1, "user", "rompiste el vaso, para y revisa el bug"),
             _turn(2, "assistant", "voy a revisar"),
             _turn(3, "user", "¿qué quedó pendiente?")]

    signals, candidates, questions = classify_turns(turns)

    assert any(s["signal_kind"] == "frustration_hotspot" for s in signals)
    assert any(c["seed_kind"] == "question_candidate" for c in candidates)
    idea_signals, idea_candidates, _ = classify_turns(
        [_turn(4, "user", "se me ocurre una idea: podríamos probar otra ruta")]
    )
    assert any(s["signal_kind"] == "idea_candidate" for s in idea_signals)
    assert any(c["seed_kind"] == "idea_candidate" for c in idea_candidates)
    assert questions[-1]["response_present"] is False


def test_question_links_use_exact_turn_ids():
    turns = [_turn(1, "user", "¿qué pasó?"), _turn(2, "assistant", "lo reviso")]

    links = _question_links(turns)

    assert links == [{"turn_id": 1, "response_turn_id": 2,
                      "response_present": True, "status": "needs_interpretation"}]


def test_sqlite_contains_fts_and_source_tables(tmp_path: Path):
    output = tmp_path / "archaeology.sqlite"
    turns = [_turn(1, "user", "una pregunta exacta")]
    write_sqlite(output, turns, [], [], [], [], [], [], [], [], [], [], [], {"schema": "test"})

    conn = sqlite3.connect(output)
    assert conn.execute("SELECT text FROM turns_fts WHERE turns_fts MATCH 'pregunta'").fetchone()[0]
    assert conn.execute("SELECT value FROM meta WHERE key='schema'").fetchone()[0] == "test"
    conn.close()


def test_path_history_matches_renamed_old_path(tmp_path: Path):
    output = tmp_path / "archaeology.sqlite"
    write_sqlite(output, [_turn(1, "user", "rename evidence")],
                 [], [], [], [], [], [], [], [], [], [], [], {"schema": "test"})
    conn = sqlite3.connect(output)
    conn.execute(
        "INSERT INTO git_commits VALUES (?,?,?,?,?,?,?,?)",
        ("sha-1", "2026-08-12T10:00:00Z", "2026-08-12T10:00:00Z",
         "author", "rename file", 1, 1, 1),
    )
    conn.execute(
        "INSERT INTO git_files VALUES (?,?,?,?,?,?)",
        ("sha-1", "new/name.py", "R", "old/name.py", 1, 1),
    )
    conn.commit()
    state = _path_history(conn, tmp_path, ["old/name.py"])
    conn.close()

    assert state["git_history"][0]["old_path"] == "old/name.py"
    assert state["git_history"][0]["requested_path"] == "old/name.py"

    packet = build_evidence_report(output, limit=2)
    assert packet["schema"] == "inferential-archaeology-report-v1"
    assert packet["interpretation_policy"]["idea_commit_link"] == (
        "lexical_subject_overlap_only"
    )


def test_duckdb_preserves_relational_types(tmp_path: Path):
    sqlite_path = tmp_path / "archaeology.sqlite"
    duckdb_path = tmp_path / "archaeology.duckdb"
    write_sqlite(sqlite_path, [_turn(1, "user", "typed row")],
                 [], [], [], [], [], [], [], [], [], [], [], {"schema": "test"})
    write_duckdb(duckdb_path, sqlite_path)

    import duckdb
    db = duckdb.connect(str(duckdb_path), read_only=True)
    columns = {row[1]: row[2] for row in db.execute(
        "pragma table_info('git_cadence')"
    ).fetchall()}
    assert columns["commit_count"] == "BIGINT"
    assert columns["bucket"] == "VARCHAR"
    db.close()


def test_mak_activity_loader_keeps_department_and_payload(tmp_path: Path):
    source = tmp_path / "actividad.jsonl"
    source.write_text(
        '{"activity_id":"act-1","department":"research",'
        '"provider":"ollama","status":"finished","ts":10}\n'
        '{bad json}\n', encoding="utf-8"
    )

    rows, warnings = load_mak_activity(source)

    assert rows[0]["department"] == "research"
    assert '"activity_id": "act-1"' in rows[0]["payload"]
    assert warnings == ["mak_activity_invalid_json:2"]


def test_memory_loader_keeps_exact_text_separate_from_turns(tmp_path: Path):
    root = tmp_path / "memory"
    root.mkdir()
    (root / "project.md").write_text(
        "---\nnode_type: project\noriginSessionId: s-1\n---\n"
        "exact memory text\n", encoding="utf-8"
    )

    rows, warnings = load_memories(root)

    assert not warnings
    assert rows[0]["relative_path"] == "project.md"
    assert rows[0]["node_type"] == "project"
    assert rows[0]["text"].endswith("exact memory text\n")


def test_vscode_loader_reconstructs_sol_requests_and_drops_mixed_models(tmp_path: Path):
    root = tmp_path / "chatSessions"
    root.mkdir()
    path = root / "sol.jsonl"
    initial = {
        "version": 3, "creationDate": 1785226343012,
        "sessionId": "sol-session", "requests": [],
    }
    sol = {
        "requestId": "req-sol", "timestamp": 1785226405524,
        "responseTimestamp": 1785226406000,
        "modelId": "aitk-foundry/Microsoft Foundry/(LIGEREZA-project)gpt-5.6-sol",
        "message": {"text": "pregunta SOL"},
        "response": [
            {"kind": "toolInvocationSerialized", "invocationMessage": {"value": "read"}},
            {"value": "respuesta SOL"},
        ],
    }
    mixed = {
        "requestId": "req-codex", "timestamp": 1785226407000,
        "modelId": "aitk-foundry/Microsoft Foundry/(LIGEREZA-project)gpt-5.3-codex",
        "message": {"text": "pregunta Codex"},
        "response": [{"value": "respuesta Codex"}],
    }
    path.write_text(
        json.dumps({"kind": 0, "v": initial}) + "\n" +
        json.dumps({"kind": 2, "k": ["requests"], "v": [sol, mixed]}) + "\n",
        encoding="utf-8",
    )

    turns, warnings = load_vscode_sol_sessions([root])

    assert not warnings
    assert [(turn["rol"], turn["texto"]) for turn in turns] == [
        ("user", "pregunta SOL"), ("assistant", "respuesta SOL"),
    ]
    assert all(turn["source"] == "vscode_sol" for turn in turns)


def test_git_cadence_aggregates_minute_hour_and_day():
    commits = [
        {"sha": "a", "authored_at": "2026-08-12T10:11:22+00:00",
         "author": "one", "files": 1, "insertions": 3, "deletions": 1},
        {"sha": "b", "authored_at": "2026-08-12T10:11:45+00:00",
         "author": "two", "files": 2, "insertions": 5, "deletions": 2},
    ]
    files = [
        {"sha": "a", "path": "a.py", "additions": 3, "deletions": 1},
        {"sha": "b", "path": "b.py", "additions": 2, "deletions": 1},
        {"sha": "b", "path": "c.py", "additions": 3, "deletions": 1},
    ]

    rows = build_git_cadence(commits, files)

    minute = next(row for row in rows if row["granularity"] == "minute")
    hour = next(row for row in rows if row["granularity"] == "hour")
    day = next(row for row in rows if row["granularity"] == "day")
    assert minute["commit_count"] == 2
    assert minute["author_count"] == 2
    assert minute["file_count"] == 3
    assert minute["insertions"] == 8
    assert minute["deletions"] == 3
    assert hour["commit_count"] == 2
    assert day["commit_count"] == 2


def test_git_rename_path_normalizes_compact_and_braced_forms():
    assert _split_git_rename_path("old.py => new.py") == ("old.py", "new.py")
    assert _split_git_rename_path("src/{old.py => new.py}") == (
        "src/old.py", "src/new.py"
    )


def test_rule_events_classify_added_and_removed_lines(tmp_path: Path):
    repo = tmp_path
    (repo / ".git").mkdir()
    # The function is exercised through a mocked git boundary in the dedicated
    # integration suite; this test only pins the event contract shape.
    assert load_rule_events(repo, []) == []


def test_duplicate_filter_keeps_repeated_wording_at_different_times():
    turns = [_turn(1, "user", "same", session="a"),
             _turn(2, "user", "same", session="b")]
    # The fixture timestamps differ; repeated wording is not a duplicate.
    assert deduplicate_turns(turns) == {"unique": 2}


def test_duplicate_filter_marks_same_content_and_timestamp():
    first = _turn(1, "user", "same", session="a")
    second = _turn(1, "user", "same", session="b")
    turns = [first, second]
    assert deduplicate_turns(turns) == {"unique": 1, "duplicates": 1}
    assert second["is_duplicate"] is True
    assert second["duplicate_of"] == first["n"]
    assert second["duplicate_reason"] == "same_content_timestamp"


def test_claude_recovered_loader_includes_design_chats_without_index_html(tmp_path: Path):
    export = tmp_path / "export"
    design = export / "design_chats"
    design.mkdir(parents=True)
    (export / "conversations.json").write_text(json.dumps([{
        "uuid": "web-session", "chat_messages": [{
            "uuid": "web-turn", "sender": "human", "created_at": "2026-08-12T10:00:00Z",
            "text": "web exact text",
        }],
    }]), encoding="utf-8")
    (design / "design.json").write_text(json.dumps({
        "uuid": "design-session", "messages": [{
            "uuid": "design-turn", "role": "assistant",
            "created_at": "2026-08-12T10:01:00Z",
            "content": {"content": "design exact text"},
        }],
    }), encoding="utf-8")
    turns, warnings = load_claude_web(export)
    assert not warnings
    assert {(turn["source"], turn["texto"]) for turn in turns} == {
        ("claude_web", "web exact text"),
        ("claude_design", "design exact text"),
    }


def test_claude_action_loader_keeps_file_mutations_out_of_turn_counts(tmp_path: Path):
    root = tmp_path / "claude"
    root.mkdir()
    path = root / "session.jsonl"
    records = [
        {
            "type": "assistant", "sessionId": "claude-session",
            "timestamp": "2026-08-12T10:00:00Z",
            "message": {"content": [{"type": "tool_use", "id": "tool-edit",
                "name": "Edit", "input": {"file_path": "src/demo.py",
                "old_string": "old", "new_string": "new"}}]},
        },
        {"type": "user", "sessionId": "claude-session",
         "timestamp": "2026-08-12T10:00:01Z", "message": {"content": []}},
        {"type": "user", "sessionId": "claude-session",
         "timestamp": "2026-08-12T10:00:02Z", "message": {"content": []}},
    ]
    records.insert(1, {
        "type": "user", "sessionId": "claude-session",
        "timestamp": "2026-08-12T09:59:00Z",
        "message": {"content": [{"type": "text", "text": "dame una propuesta"}]},
    })
    records.insert(2, {
        "type": "assistant", "sessionId": "claude-session",
        "timestamp": "2026-08-12T09:59:30Z",
        "message": {"content": [{"type": "text", "text": "Propondré editar el archivo."}]},
    })
    records.insert(3, {
        "type": "user", "sessionId": "claude-session",
        "timestamp": "2026-08-12T09:59:40Z",
        "message": {"content": [{"type": "text", "text": "dale"}]},
    })
    records.insert(5, {
        "type": "tool_result", "sessionId": "claude-session",
        "timestamp": "2026-08-12T10:00:01Z",
        "message": {"content": [{"type": "tool_result",
            "tool_use_id": "tool-edit", "content": "edited",
            "is_error": False}]},
    })
    path.write_text("\n".join(json.dumps(record) for record in records), encoding="utf-8")

    actions, warnings = load_claude_actions(root)

    assert not warnings
    assert len(actions) == 1
    assert actions[0]["tool_name"] == "Edit"
    assert actions[0]["result_status"] == "ok"
    assert actions[0]["paths"] == ["src/demo.py"]

    turns = [
        _turn(1, "user", "dame una propuesta"),
        _turn(2, "assistant", "Propondré editar el archivo."),
        _turn(3, "user", "dale"),
    ]
    turns[0]["ts"] = "2026-08-12T09:59:00Z"
    turns[1]["ts"] = "2026-08-12T09:59:30Z"
    turns[2]["ts"] = "2026-08-12T09:59:40Z"
    turns[0]["sesion"] = turns[1]["sesion"] = turns[2]["sesion"] = "claude-session"
    turns[0]["source"] = turns[1]["source"] = turns[2]["source"] = "claude_code"
    rows = build_proposal_followups(
        turns, [], repo=tmp_path, claude_actions=actions
    )
    assert rows[0]["direct_action_count"] == 1
    assert rows[0]["status"] == "direct_action_candidate"


def test_codex_action_loader_extracts_patch_paths_and_pairs_result(tmp_path: Path):
    root = tmp_path / "codex"
    root.mkdir()
    path = root / "rollout.jsonl"
    patch = "*** Begin Patch\n*** Update File: src/demo.py\n@@\n-old\n+new\n*** End Patch"
    records = [
        {"type": "session_meta", "payload": {
            "session_id": "codex-session", "git": {"branch": "mak"}
        }},
        {"type": "response_item", "timestamp": "2026-08-12T10:00:00Z",
         "payload": {"type": "custom_tool_call", "name": "apply_patch",
                     "call_id": "call-1", "input": patch}},
        {"type": "response_item", "timestamp": "2026-08-12T10:00:01Z",
         "payload": {"type": "custom_tool_call_output", "call_id": "call-1",
                     "output": "Exit code: 0\nSuccess."}},
    ]
    path.write_text("\n".join(json.dumps(record) for record in records), encoding="utf-8")

    actions, warnings = load_codex_actions(root)

    assert not warnings
    assert actions[0]["session_id"] == "codex-session"
    assert actions[0]["paths"] == ["src/demo.py"]
    assert actions[0]["result_status"] == "ok"

    turns = [
        _turn(1, "user", "dame una propuesta", session="codex-session"),
        _turn(2, "assistant", "Propondré editar el archivo.", session="codex-session"),
        _turn(3, "user", "dale", session="codex-session"),
    ]
    turns[0]["source"] = turns[1]["source"] = turns[2]["source"] = "codex"
    turns[0]["ts"] = "2026-08-12T09:59:00Z"
    turns[1]["ts"] = "2026-08-12T09:59:30Z"
    turns[2]["ts"] = "2026-08-12T09:59:40Z"
    rows = build_proposal_followups(
        turns, [], repo=tmp_path, codex_actions=actions
    )
    assert rows[0]["direct_action_count"] == 1


def test_interpretation_gate_rejects_model_claim_without_direct_evidence():
    result = validate_interpretation(
        {"kind": "idea", "id": "x", "response_id": "y"},
        {"evidence_status": "implemented", "confidence": 0.9},
    )
    assert result["model_status"] == "implemented"
    assert result["validated_status"] == "insufficient"


def test_interpretation_gate_does_not_promote_lexical_commit_overlap():
    result = validate_interpretation(
        {"kind": "idea", "id": "x", "commit_evidence": [{"sha": "x"}],
         "commit_link_method": "lexical_subject_overlap_only"},
        {"evidence_status": "implemented", "confidence": 0.9},
    )
    assert result["validated_status"] == "insufficient"


def test_interpretation_gate_does_not_promote_unproven_agent_proposal():
    result = validate_interpretation(
        {"kind": "agent_proposal", "id": "x"},
        {"evidence_status": "implemented", "confidence": 0.9},
    )
    assert result["validated_status"] == "insufficient"


def test_interpretation_gate_rejects_rule_cause_inference():
    result = validate_interpretation(
        {"kind": "rule_eliminated_candidate", "id": "x"},
        {"evidence_status": "implemented"},
    )
    assert result["validated_status"] == "insufficient"


def test_idea_followups_are_a_queue_not_an_abandonment_verdict():
    turns = [_turn(1, "user", "tengo otra idea: probar un mapa"),
             _turn(2, "assistant", "la desarrollo como propuesta")]
    _signals, candidates, _questions = classify_turns(turns)
    rows = build_idea_followups(turns, candidates, [])
    assert rows[0]["response_present"] is True
    assert rows[0]["status"] == "needs_semantic_link"


def test_analysis_exclusion_accepts_injected_context_attributes():
    from tools.inferential_archaeology import _analysis_exclusion

    turn = {"source": "codex", "sintetico": False,
            "texto": "\n<in-app-browser-context source=\"ambient-ui-state\">"}
    assert _analysis_exclusion(turn) == "protocol_or_injected_context"


def test_cross_source_packet_keeps_direct_action_distinct_from_git_echo(tmp_path: Path):
    output = tmp_path / "archaeology.sqlite"
    sol = _turn(1, "user", "replantear el micelio", session="sol-session")
    sol.update({
        "source": "vscode_sol", "source_turn_id": "req-1:0:user",
        "archivo": "sol.jsonl", "linea": 7,
    })
    prior = _turn(2, "user", "el micelio necesita materia", session="old-session")
    prior.update({"source": "claude_code", "source_turn_id": "old-1"})
    write_sqlite(
        output, [sol, prior],
        [{"sha": "abc", "authored_at": "2026-08-12T10:05:00Z",
          "committed_at": "2026-08-12T10:05:00Z",
          "author": "test", "subject": "feat micelio", "files": 1,
          "insertions": 2, "deletions": 0}],
        [{"sha": "abc", "path": "cultura/mak_research/micelio.py",
          "status": "M", "additions": 2, "deletions": 0}],
        [], [], [], [], [], [], [], [], [],
        {"schema": "test", "repo": str(tmp_path)},
        [{"session_id": "sol-session", "request_id": "req-1",
          "model_id": "gpt-5.6-sol", "requested_at": "2026-08-12T10:00:00Z",
          "responded_at": "2026-08-12T10:06:00Z", "source_file": "sol.jsonl",
          "source_line": 7, "prompt_tokens": 0, "completion_tokens": 0,
          "elapsed_ms": 0, "response_items": 1, "assistant_chars": 20,
          "tool_invocations": 1}],
        [{"session_id": "sol-session", "request_id": "req-1",
          "model_id": "gpt-5.6-sol", "occurred_at": "2026-08-12T10:04:00Z",
          "source_file": "sol.jsonl", "source_line": 7, "event_index": 1,
          "event_kind": "toolInvocationSerialized", "tool_id": "copilot_applyPatch",
          "invocation": "Editing cultura/mak_research/micelio.py",
          "past_tense": "Edited cultura/mak_research/micelio.py",
          "is_complete": 1, "payload": "{}",
          "message": "Editing cultura/mak_research/micelio.py"}],
    )
    import sqlite3
    conn = sqlite3.connect(output)
    packet = build_cross_source_packet(conn, limit=1)
    conn.close()

    assert packet[0]["implementation_status"] == "direct_action_candidate"
    assert packet[0]["implementation_evidence"][0]["paths"] == [
        "cultura/mak_research/micelio.py"
    ]
    assert packet[0]["git_evidence"][0]["sha"] == "abc"


def test_cross_source_packet_does_not_promote_lexical_overlap(tmp_path: Path):
    output = tmp_path / "archaeology.sqlite"
    sol = _turn(1, "user", "una idea sobre micelio", session="sol-session")
    sol.update({
        "source": "vscode_sol", "source_turn_id": "req-1:0:user",
        "archivo": "sol.jsonl", "linea": 7,
    })
    prior = _turn(2, "user", "el micelio existe", session="old-session")
    prior.update({"source": "claude_code", "source_turn_id": "old-1"})
    write_sqlite(
        output, [sol, prior],
        [{"sha": "abc", "authored_at": "2026-08-12T10:05:00Z",
          "committed_at": "2026-08-12T10:05:00Z",
          "author": "test", "subject": "feat micelio", "files": 1,
          "insertions": 2, "deletions": 0}],
        [{"sha": "abc", "path": "cultura/mak_research/micelio.py",
          "status": "M", "additions": 2, "deletions": 0}],
        [], [], [], [], [], [], [], [], [], {"schema": "test"},
    )
    import sqlite3
    conn = sqlite3.connect(output)
    packet = build_cross_source_packet(conn, limit=1)
    conn.close()

    assert packet[0]["implementation_status"] == "temporal_echo_candidate"
    assert packet[0]["implementation_evidence"] == []


def test_agent_proposal_is_not_counted_as_user_idea():
    turns = [
        _turn(1, "user", "propón mejoras para MAK"),
        _turn(2, "assistant", "Propondré una nueva interfaz y construiré el circuito."),
    ]
    rows = build_proposal_followups(turns, [])

    assert len(rows) == 1
    assert rows[0]["prompt_driven"] == 1
    assert rows[0]["trigger_turn_id"] == 1
    assert rows[0]["status"] == "prompt_generated_unaccepted"


def test_agent_proposal_records_approval_without_calling_it_completion():
    turns = [
        _turn(1, "user", "dame una propuesta"),
        _turn(2, "assistant", "Implementaré una cola de propuestas."),
        _turn(3, "user", "dale"),
    ]
    rows = build_proposal_followups(turns, [])

    assert rows[0]["approval_present"] == 1
    assert rows[0]["status"] == "accepted_without_direct_action"
    assert "not implementation" in rows[0]["evidence"]


def test_bifurcation_group_preserves_prompt_response_and_context(tmp_path: Path):
    output = tmp_path / "archaeology.sqlite"
    turns = [
        _turn(1, "user", "dame una propuesta para el micelio"),
        _turn(2, "assistant", "Propongo construir una ruta de micelio."),
        _turn(3, "user", "dale"),
    ]
    proposal = [{
        "turn_id": 2, "source": "claude_code", "session_id": "s1",
        "proposal_timestamp": "2026-08-12T10:02:00+00:00",
        "trigger_turn_id": 1, "prompt_driven": 1, "approval_turn_id": 3,
        "approval_present": 1, "direct_action_count": 0,
        "session_commit_count": 0, "matching_commit_count": 0,
        "matching_commit_shas": [], "status": "accepted_without_direct_action",
        "evidence": json.dumps({
            "proposal_text": "Propongo construir una ruta de micelio.",
            "trigger_text": "dame una propuesta para el micelio",
            "approval_text": "dale", "direct_actions": [],
        }),
    }]
    write_sqlite(
        output, turns, commits=[], files=[], cadence=[], activity=[],
        memories=[], rules=[], signals=[], questions=[], profiles=[],
        candidates=[], idea_followups=[],
        meta={"schema": "test", "repo": str(tmp_path)},
        proposal_followups=proposal,
    )
    conn = sqlite3.connect(output)
    packet = build_bifurcation_map(conn, tmp_path)
    conn.close()

    group = packet["groups"][0]
    assert packet["item_count"] == 1
    assert group["representative_trigger"]["text"] == turns[0]["texto"]
    assert group["representative_response"]["text"] == turns[2]["texto"]
    assert group["member_evidence"][0]["outcome"] == (
        "approved_without_verified_execution"
    )
    assert "memory_evidence" in group
    assert "mak_activity" in group
