import json
import os
import sys
import threading

sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), "..", "cultura", "mak_research"))

from research_lib import emitir_evento


def test_concurrent_event_emission_preserves_valid_json_records(
        tmp_path, monkeypatch):
    expanduser = os.path.expanduser
    monkeypatch.setattr(
        os.path, "expanduser",
        lambda path: str(tmp_path) if path == "~" else expanduser(path))
    barrier = threading.Barrier(12)

    def write_record(index):
        barrier.wait(timeout=3)
        emitir_evento("research", "job-%d" % index, "node_end",
                       estado="listo")

    threads = [threading.Thread(target=write_record, args=(i,))
               for i in range(12)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=3)

    path = tmp_path / "research" / "eventos.jsonl"
    records = [json.loads(line) for line in
               path.read_text(encoding="utf-8").splitlines()]
    assert len(records) == 12
    assert {record["job_id"] for record in records} == {
        "job-%d" % index for index in range(12)}
