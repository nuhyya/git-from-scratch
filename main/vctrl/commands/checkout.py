import os
from vctrl.index import clear_index, write_index
from vctrl.refs import get_ref
from vctrl.objects import GitObject, Blob
from vctrl.repo import repo_path


def checkout(name):
    # Get OID: could be direct commit or symbolic ref
    try:
        oid = get_ref(f"refs/heads/{name}")  # Try as branch
    except FileNotFoundError:
        oid = name  # Fallback to raw OID

    if oid is None or not isinstance(oid, str) or not oid.strip():
        print(f"❌ Branch or commit '{name}' not found.")
        return

    try:
        commit = GitObject.from_file(oid, expected_type="commit")
    except FileNotFoundError:
        print(f"❌ Commit object '{oid}' not found in object store.")
        return

    tree_oid = commit.data.decode().split("\n")[0].split()[1]

    # Replace working directory with tree contents
    checkout_tree(tree_oid)

    # Update HEAD
    with open(os.path.join(repo_path(), "HEAD"), "w") as f:
        f.write(f"ref: refs/heads/{name}")

    clear_index()



def checkout_tree(tree_oid):
    tree = GitObject.from_file(tree_oid, expected_type="tree")
    entries = tree.data.decode().splitlines()
    for entry in entries:
        parts = entry.split()
        if len(parts) != 3:
            raise ValueError(f"Malformed tree entry: {entry}")

        type_, oid, path = parts
        try:
            blob = GitObject.from_file(oid, expected_type="blob")
        except FileNotFoundError:
            print(f"⚠️ Warning: Missing blob object for {path} ({oid})")
        continue

        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "wb") as f:
            f.write(blob.data)
