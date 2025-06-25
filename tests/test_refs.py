import os
import tempfile
import shutil
import pytest

from vctrl import repo
from vctrl.refs import update_ref, get_ref


def setup_temp_repo():
    temp_dir = tempfile.mkdtemp()
    os.makedirs(os.path.join(temp_dir, ".vctrl", "refs", "heads"))

    # Patch repo_path globally
    import vctrl.refs
    repo.repo_path = lambda: os.path.join(temp_dir, ".vctrl")
    vctrl.refs.repo_path = repo.repo_path

    return temp_dir


def test_update_and_get_head_ref():
    temp_dir = setup_temp_repo()
    try:
        update_ref("HEAD", "abc123")
        assert get_ref("HEAD") == "abc123"
    finally:
        shutil.rmtree(temp_dir)


def test_update_and_get_named_ref():
    temp_dir = setup_temp_repo()
    try:
        ref_name = os.path.join("refs", "heads", "main")
        oid = "def4567890abcdef"
        update_ref(ref_name, oid)
        assert get_ref(ref_name) == oid
    finally:
        shutil.rmtree(temp_dir)


def test_overwrite_ref():
    temp_dir = setup_temp_repo()
    try:
        update_ref("HEAD", "abc123")
        update_ref("HEAD", "zzz999")
        assert get_ref("HEAD") == "zzz999"
    finally:
        shutil.rmtree(temp_dir)


def test_nonexistent_ref_raises():
    temp_dir = setup_temp_repo()
    try:
        with pytest.raises(FileNotFoundError):
            get_ref("refs/heads/does-not-exist")
    finally:
        shutil.rmtree(temp_dir)


def test_invalid_oid_format():
    temp_dir = setup_temp_repo()
    try:
        ref_path = os.path.join(repo.repo_path(), "HEAD")
        with open(ref_path, "w") as f:
            f.write("INVALID-OID!\n")

        # We allow any string for now; real validation would go here
        assert get_ref("HEAD") == "INVALID-OID!"
    finally:
        shutil.rmtree(temp_dir)

