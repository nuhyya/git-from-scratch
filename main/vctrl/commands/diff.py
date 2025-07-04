from vctrl.index import read_index
from vctrl.objects import GitObject


import os


IGNORED_DIRS = {'.vctrl', '__pycache__', '.git', '.DS_Store', 'venv', 'build', 'dist'}


def is_ignored(path):
    parts = path.split(os.sep)
    return any(part in IGNORED_DIRS for part in parts)


def diff_index_vs_workdir():
    index_data = read_index()
    seen_paths = set()

    # 1. Check for modified & deleted files
    for path, oid in index_data.items():
        seen_paths.add(path)
        try:
            with open(path, 'rb') as f:
                data = f.read()
            current_oid = GitObject(data=data, type_="blob").save()
            if current_oid != oid:
                print(f"Modified: {path}")
        except FileNotFoundError:
            print(f"Deleted: {path}")

    # 2. Check for added files
    for root, _, files in os.walk("."):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, start=".")
            if is_ignored(rel_path):
                continue
            if rel_path not in seen_paths:
                print(f"Added: {rel_path}")
