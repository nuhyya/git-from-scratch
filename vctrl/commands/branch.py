import os
from vctrl.refs import update_ref, get_ref
from vctrl.repo import repo_path


def create_branch(name, start_oid=None):
    if not name:
        raise ValueError("Branch name cannot be empty")
    if not start_oid:
        head = get_ref("HEAD")
        if head.startswith("ref:"):
            head_ref = head.split(": ")[1]
            start_oid = get_ref(head_ref)
        else:
            start_oid = head
    update_ref(f"refs/heads/{name}", start_oid)
    print(f"Branch '{name}' created at {start_oid}")


def list_branches():
    refs_dir = os.path.join(repo_path(), "refs/heads")
    branches = os.listdir(refs_dir)
    for branch in branches:
        print(branch)
