# KONTRAK API (wajib dipatuhi semua agent)
File data: tasks.json (list of dict). Tiap task: {"id": int, "title": str, "done": bool}

## storage.py harus expose persis fungsi ini:
- load(path: str) -> list[dict]        # baca JSON; return [] kalau file tak ada
- save(path: str, tasks: list) -> None # tulis JSON (indent=2)
- add_task(tasks: list, title: str) -> dict   # id = max(id)+1 (mulai 1); append {"id","title","done":False}; return task baru
- complete_task(tasks: list, task_id: int) -> bool  # set done=True; True kalau ketemu, else False
- remove_task(tasks: list, task_id: int) -> bool    # hapus; True kalau ketemu, else False

## cli.py: argparse subcommands pakai file tasks.json di CWD, import dari storage:
- add "<title>"  -> tambah & print "Added #<id>: <title>"
- list           -> print tiap task: "[x] #1 judul" (done) / "[ ] #2 judul"
- done <id>      -> print "Done #<id>" atau "Not found #<id>"
- rm <id>        -> print "Removed #<id>" atau "Not found #<id>"
