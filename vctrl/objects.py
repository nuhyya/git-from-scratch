import os, hashlib, zlib
from vctrl.repo import repo_path

def hash_object(data, type_ = "blob"):
    header = f"{type_} {len(data)}\0".encode()
    full_data = header + data
    oid = hashlib.sha1(full_data).hexdigest()

    path = os.path.join(repo_path()+"objects"+oid)

    with open(path, "wb") as f:
        f.write(zlib.compress(full_data))

    return oid 

def get_object(oid, expected_type = None):
    path = os.path.join(repo_path() + "objects" + oid)

    with open(path, "rb") as file:
        data = zlib.decompress(file.read())
    
    null_sep = data.index(b'\0')

    header = data[:null_sep].decode()
    type_, size = header.split()
    size = int(size)

    content = data[null_sep+1:]
    assert len(content) == size
    if expected_type: assert expected_type == type_
    
    return content 



