from vctrl.objects import GitObject
from vctrl.index import write_index
from vctrl.commands.checkout import checkout_tree


def merge(base_oid, other_oid):
    base = GitObject.from_file(base_oid, expected_type="commit")
    other = GitObject.from_file(other_oid, expected_type="commit")

    base_tree_oid = base.data.decode().splitlines()[0]
    other_tree_oid = other.data.decode().splitlines()[0]

    # For now, simply replace with other
    print("Merging by replacing working tree with other")
    checkout_tree(other_tree_oid)
    write_index({}) 
