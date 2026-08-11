import json
import threading

from cultura.mak_plataforma import mutaciones


def test_concurrent_records_preserve_two_valid_json_lines(tmp_path):
    path = str(tmp_path / "mutaciones.log")
    results = []
    barrier = threading.Barrier(2)

    def write_record(index):
        barrier.wait(timeout=3)
        results.append(mutaciones.registrar(
            "prueba", "detalle-%d" % index, ruta=path))

    threads = [threading.Thread(target=write_record, args=(i,)) for i in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=3)

    assert results == [True, True]
    lines = open(path, encoding="utf-8").read().splitlines()
    records = [json.loads(line) for line in lines]
    assert len(records) == 2
    assert {record["detalle"] for record in records} == {
        "detalle-0", "detalle-1"}


def test_recording_creates_file_lock_next_to_target(tmp_path):
    path = str(tmp_path / "nested" / "mutaciones.log")
    assert mutaciones.registrar("prueba", ruta=path)
    assert (tmp_path / "nested" / "mutaciones.log.lock").exists()
