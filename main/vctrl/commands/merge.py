from vctrl.objects import GitObject, Blob
from vctrl.index import write_index
from vctrl.commands.checkout import checkout_tree

def get_tree_entries(tree_oid):
    tree = GitObject.from_file(tree_oid, expected_type="tree")
    entries = {}
    for entry in tree.data.decode().splitlines():
        parts = entry.split()
        if len(parts) == 3:
            _, path, oid = parts
            entries[path] = oid
    return entries

def merge(base_oid, other_oid):
    base = GitObject.from_file(base_oid, expected_type="commit")
    other = GitObject.from_file(other_oid, expected_type="commit")

    base_tree_oid = base.data.decode().splitlines()[0].split()[1]
    other_tree_oid = other.data.decode().splitlines()[0].split()[1]

    base_tree = get_tree_entries(base_tree_oid)
    other_tree = get_tree_entries(other_tree_oid)

    merged_index = {}
    conflicts = []

    for path in set(base_tree) | set(other_tree):
        base_oid = base_tree.get(path)
        other_oid = other_tree.get(path)

        if base_oid == other_oid:
            merged_index[path] = other_oid
        elif base_oid is None:
            merged_index[path] = other_oid
        elif other_oid is None:
            merged_index[path] = base_oid
        else:
            base_data = GitObject.from_file(base_oid).data
            other_data = GitObject.from_file(other_oid).data

            if base_data != other_data:
                merged_blob = b"<<<<<<< HEAD\n" + base_data + b"\n=======\n" + other_data + b"\n>>>>>>> MERGE\n"
                conflict_blob = Blob(merged_blob)
                oid = conflict_blob.save()
                merged_index[path] = oid
                conflicts.append(path)
            else:
                merged_index[path] = base_oid

    checkout_tree(other_tree_oid)  # naive; consider using merged tree
    write_index(merged_index)

    if conflicts:
        print("Merge completed with conflicts in:")
        for path in conflicts:
            print(f"  - {path}")
    else:
        print("Merge successful with no conflicts.")
