import os
import tempfile

import storage


def test_add_task_assigns_incremental_id():
    tasks = []
    t1 = storage.add_task(tasks, "beli susu")
    t2 = storage.add_task(tasks, "beli roti")
    assert t1["id"] == 1
    assert t2["id"] == 2
    assert t1["title"] == "beli susu"
    assert t1["done"] is False
    assert len(tasks) == 2


def test_complete_task():
    tasks = []
    t = storage.add_task(tasks, "kerjakan laporan")
    assert storage.complete_task(tasks, t["id"]) is True
    assert tasks[0]["done"] is True
    # id yang tidak ada -> False, daftar tak berubah
    assert storage.complete_task(tasks, 9999) is False


def test_remove_task():
    tasks = []
    t1 = storage.add_task(tasks, "satu")
    t2 = storage.add_task(tasks, "dua")
    assert storage.remove_task(tasks, t1["id"]) is True
    assert len(tasks) == 1
    assert tasks[0]["id"] == t2["id"]
    # id yang tidak ada -> False
    assert storage.remove_task(tasks, 9999) is False


def test_load_missing_file_returns_empty():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "tasks.json")
        assert storage.load(path) == []


def test_save_load_round_trip():
    tasks = []
    storage.add_task(tasks, "alpha")
    storage.add_task(tasks, "beta")
    storage.complete_task(tasks, 1)
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "tasks.json")
        storage.save(path, tasks)
        loaded = storage.load(path)
        assert loaded == tasks
        assert len(loaded) == 2
        assert loaded[0]["done"] is True
        assert loaded[1]["done"] is False


if __name__ == "__main__":
    test_add_task_assigns_incremental_id()
    test_complete_task()
    test_remove_task()
    test_load_missing_file_returns_empty()
    test_save_load_round_trip()
    print("semua assert lolos")
