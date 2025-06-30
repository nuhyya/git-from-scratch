from vctrl.index import read_index
from vctrl.objects import GitObject


def diff_index_vs_workdir():
    index_data = read_index()
    for path, oid in index_data.items():
        try:
            with open(path, 'rb') as f:
                data = f.read()
            current_oid = GitObject(data=data, type_="blob").save()
            if current_oid != oid:
                print(f"Modified: {path}")
        except FileNotFoundError:
            print(f"Deleted: {path}")
