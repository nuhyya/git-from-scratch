import os
from vctrl.repo import repo_path

def update_ref(ref, oid):
    path = os.path.join(repo_path(), ref)
    with open(path, "w") as f:
        f.write(oid)

def get_ref(name):
    path = os.path.join(repo_path(), name)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        value = f.read().strip()
    if value.startswith("ref:"):
        # resolve the referenced ref recursively
        return get_ref(value[5:].strip())
    return value

def get_branch_name():
    head_path = os.path.join(repo_path(), "HEAD")
    with open(head_path) as f:
        data = f.read().strip()
    if data.startswith("ref:"):
        return data.split("/")[-1]  # return just the branch name
    return None  # detached HEAD

def get_ref_path(ref):
    return os.path.join(repo_path(), ref)

