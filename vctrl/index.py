import json, os
from vctrl.repo import repo_path


index_file = os.path.join(repo_path(), "index")
def read_index():
    if os.path.exists(index_file):
        return json.load(open(index_file))
    return {}


def write_index(index):
    with open(index_file, 'w') as f:
        json.dump(index, f)

def add_to_index(file_path, oid):
    if not isinstance(file_path, str) or not file_path.strip():
        raise TypeError("Invalid file path")
    if not isinstance(oid, str) or not oid.strip():
        raise TypeError("Invalid object ID")
    
    index = read_index()
    index[file_path] = oid
    write_index(index)

