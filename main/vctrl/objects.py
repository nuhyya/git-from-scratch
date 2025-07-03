import os, hashlib, zlib
from vctrl.repo import repo_path


class GitObject:
    
    def __init__(self, oid=None, type_=None, data=None):
        self.oid = oid
        self.type = type_
        self.data = data
    
    @classmethod
    def from_file(cls, oid, expected_type=None):
        content = read_object(oid, expected_type)
        obj = cls(oid=oid, type_=expected_type, data=content)
        return obj
    
    def save(self):
        if self.data is None:
            raise ValueError("Cannot save object with no data")
        self.oid = hash_object(self.data, self.type)
        return self.oid


class Blob(GitObject):
    
    def __init__(self, data=None, oid=None):
        super().__init__(oid=oid, type_="blob", data=data)
    
    @classmethod
    def from_file_path(cls, file_path):
        with open(file_path, 'rb') as f:
            data = f.read()
        return cls(data=data)


class Tree(GitObject):
    
    def __init__(self, entries=None, oid=None):
        self.entries = entries or []
        data = self._serialize_entries() if entries else None
        super().__init__(oid=oid, type_="tree", data=data)
    
    def _serialize_entries(self):
        if not self.entries:
            return b""
        tree_content = "\n".join(f"{typ} {oid} {name}" for typ, oid, name in self.entries)
        return tree_content.encode()
    
    def add_entry(self, type_, oid, name):
        self.entries.append((type_, oid, name))
        self.data = self._serialize_entries()
    
    @classmethod
    def from_directory(cls, directory='.'):
        entries = []

        for entry in sorted(os.listdir(directory)):
            if entry.startswith('.') or entry in {'__pycache__', 'build', 'dist', 'venv'}:
                continue  # Skip hidden and system files like .DS_Store

            path = os.path.join(directory, entry)

            if os.path.isfile(path):
                blob = Blob.from_file_path(path)
                oid = blob.save()
                entries.append(("blob", oid, entry))

            elif os.path.isdir(path):
                subtree = cls.from_directory(path)
                if subtree.entries:  # Only add non-empty subtrees
                    oid = subtree.save()
                    entries.append(("tree", oid, entry))
    
        return cls(entries=entries)


class Commit(GitObject):
    
    def __init__(self, tree_oid, parent=None, message="", author_name="you", 
                 author_email="notknown", oid=None):
        self.tree_oid = tree_oid
        self.parent = parent
        self.message = message
        self.author_name = author_name
        self.author_email = author_email
        
        data = self._serialize_commit()
        super().__init__(oid=oid, type_="commit", data=data)
    
    def _serialize_commit(self):
        import time
        
        if self.tree_oid is None:
            raise ValueError("Cannot create a commit with no tree")
        
        commit = f"tree {self.tree_oid}\n"
        if self.parent:
            commit += f"parent {self.parent}\n"
        commit += f"author {self.author_name} <{self.author_email}> {int(time.time())} +0000\n"
        commit += f'\n{self.message}\n'
        
        return commit.encode()


def hash_object(data, type_="blob"):
    header = f"{type_} {len(data)}\0".encode()
    full_data = header + data
    oid = hashlib.sha1(full_data).hexdigest()
   
    object_dir = os.path.join(repo_path(), "objects")

    if not os.path.isdir(object_dir):
        raise FileNotFoundError(f"Object directory not found: {object_dir}")
    
    path = os.path.join(object_dir, oid)
    
    with open(path, "wb") as f:
        f.write(zlib.compress(full_data))

    return oid 


def get_object(oid, expected_type=None):
    path = os.path.join(repo_path(), "objects", oid)

    with open(path, "rb") as file:
        data = zlib.decompress(file.read())
    
    null_sep = data.index(b'\0')

    header = data[:null_sep].decode()
    type_, size = header.split()
    size = int(size)

    content = data[null_sep+1:]
    assert len(content) == size
    if expected_type: 
        assert expected_type == type_
    
    return content 


def read_object(oid, expected_type=None):
    return get_object(oid, expected_type)

from vctrl.index import read_index

def write_tree():
    entries = []
    index = read_index()
    for path, oid in index.items():
        entries.append(("blob", oid, path))
    tree = Tree(entries=entries)
    return tree.save()
