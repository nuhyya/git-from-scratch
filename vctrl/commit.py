import time
from vctrl.objects import hash_object

def create_commit(tree_oid, user_name, user_email, parent = None, message = ""):
    commit = f"tree {tree_oid}\n"
    if parent:
        commit += f"parent {parent}\n"
    commit += f'author {user_name} {user_email} {int(time.time())} +000\n'
    commit += f'\n{message}\n'

    return hash_object(commit.encode(), 'commit')

