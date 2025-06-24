import os
from vctrl.objects import hash_object

#recursively handles directory trees


def write_tree(directory = '.'):
    entries = []
    for entry in sorted(os.listdir(directory)):
        path = os.path.join(directory, entry)

        if path in '.vctrl':
            continue

        if os.path.isfile(path):
            with open(path, 'rb') as f:
                blob_data = f.read()    
            oid = hash_object(blob_data)
            entries.append(("blob", oid, entry))

        elif os.path.isdir(path):
            oid = write_tree(path)
            entries.append(("tree", oid, entry))

    tree = "\n".join(f"{typ} {oid} {name}" for typ, oid, name in entries)
    return hash_object(tree.encode(), "tree")

