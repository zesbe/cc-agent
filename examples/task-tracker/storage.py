import json
import os


def load(path: str) -> list[dict]:
    """Baca JSON; return [] kalau file tak ada."""
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


def save(path: str, tasks: list) -> None:
    """Tulis JSON (indent=2)."""
    with open(path, "w") as f:
        json.dump(tasks, f, indent=2)


def add_task(tasks: list, title: str) -> dict:
    """id = max(id)+1 (mulai 1); append {"id","title","done":False}; return task baru."""
    new_id = max((t["id"] for t in tasks), default=0) + 1
    task = {"id": new_id, "title": title, "done": False}
    tasks.append(task)
    return task


def complete_task(tasks: list, task_id: int) -> bool:
    """Set done=True; True kalau ketemu, else False."""
    for t in tasks:
        if t["id"] == task_id:
            t["done"] = True
            return True
    return False


def remove_task(tasks: list, task_id: int) -> bool:
    """Hapus; True kalau ketemu, else False."""
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            tasks.pop(i)
            return True
    return False
