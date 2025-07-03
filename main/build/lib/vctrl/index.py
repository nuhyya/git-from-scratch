
import os
import json
from vctrl.repo import repo_path

def index_path():
    return os.path.join(repo_path(), "index")

def read_index():
    try:
        with open(index_path(), 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def write_index(data):
    path = index_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)  # <- 🔧 Ensure directory
    with open(path, 'w') as f:
        json.dump(data, f)

def add_to_index(file_path, oid):
    if not file_path or not isinstance(file_path, str) or not file_path.strip():
        raise TypeError("Invalid file path")
    if not oid or not isinstance(oid, str) or not oid.strip():
        raise TypeError("Invalid object ID")
    index_data = read_index()
    index_data[file_path] = oid
    write_index(index_data)

def clear_index():
    write_index({})
