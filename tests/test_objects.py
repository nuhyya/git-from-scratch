import os
import shutil
import tempfile
from vctrl import repo
from vctrl.objects import hash_object, get_object


def setup_temp_repo():
    temp_dir = tempfile.mkdtemp()
    os.makedirs(os.path.join(temp_dir, ".vctrl", "objects"))

    import vctrl.objects
    repo.repo_path = lambda: os.path.join(temp_dir, ".vctrl")
    vctrl.objects.repo_path = repo.repo_path
    return temp_dir


def test_hash_and_retrieve():
    temp_dir = setup_temp_repo()
    try:
        oid = hash_object(b"hello world")
        assert get_object(oid, "blob") == b"hello world"
    finally:
        shutil.rmtree(temp_dir)

