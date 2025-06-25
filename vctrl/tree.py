import os
from vctrl.objects import hash_object

# Recursively writes directory trees like Git
def write_tree(directory='.'):
    entries = []

    for entry in sorted(os.listdir(directory)):
        path = os.path.join(directory, entry)

        # Skip the .vctrl directory
        if '.vctrl' in path:
            continue

        if os.path.isfile(path):
            with open(path, 'rb') as f:
                blob_data = f.read()
            oid = hash_object(blob_data)
            entries.append(("blob", oid, entry))

        elif os.path.isdir(path):
            oid = write_tree(path)
            if oid:  # Only add non-empty subtrees
                entries.append(("tree", oid, entry))

    if not entries:
        return None  # Don't store empty trees

    tree = "\n".join(f"{typ} {oid} {name}" for typ, oid, name in entries)
    return hash_object(tree.encode(), "tree")

