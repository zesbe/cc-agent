import argparse

import storage

PATH = "tasks.json"


def cmd_add(args):
    tasks = storage.load(PATH)
    task = storage.add_task(tasks, args.title)
    storage.save(PATH, tasks)
    print(f"Added #{task['id']}: {task['title']}")


def cmd_list(args):
    tasks = storage.load(PATH)
    for t in tasks:
        mark = "[x]" if t["done"] else "[ ]"
        print(f"{mark} #{t['id']} {t['title']}")


def cmd_done(args):
    tasks = storage.load(PATH)
    if storage.complete_task(tasks, args.id):
        storage.save(PATH, tasks)
        print(f"Done #{args.id}")
    else:
        print(f"Not found #{args.id}")


def cmd_rm(args):
    tasks = storage.load(PATH)
    if storage.remove_task(tasks, args.id):
        storage.save(PATH, tasks)
        print(f"Removed #{args.id}")
    else:
        print(f"Not found #{args.id}")


def main():
    parser = argparse.ArgumentParser(description="Todo CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Tambah task baru")
    p_add.add_argument("title", help="Judul task")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="Tampilkan semua task")
    p_list.set_defaults(func=cmd_list)

    p_done = sub.add_parser("done", help="Tandai task selesai")
    p_done.add_argument("id", type=int, help="ID task")
    p_done.set_defaults(func=cmd_done)

    p_rm = sub.add_parser("rm", help="Hapus task")
    p_rm.add_argument("id", type=int, help="ID task")
    p_rm.set_defaults(func=cmd_rm)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
