import os
from vctrl.repo import repo_path

def update_ref(ref, oid):
    path = os.path.join(repo_path(), ref)
    with open(path, "w") as f:
        f.write(oid)

def get_ref(ref):
    path = os.path.join(repo_path(), ref)
    with open(path) as f:
        return f.read().strip()

