import time
from vctrl.objects import hash_object

#creates a commit tree, returns encoded object

def create_commit(tree_oid, user_name = "you", user_email = "notknown", parent = None, message = ""):
    if tree_oid is None:
        raise ValueError("Cannot create a commit with no tree")

    commit = f"tree {tree_oid}\n"
    if parent:
        commit += f"parent {parent}\n"
    commit += f"author {user_name} <{user_email}> {int(time.time())} +0000\n"
    commit += f'\n{message}\n'

    return hash_object(commit.encode(), 'commit')

