import os
import shutil
import tempfile
import json
import pytest

from vctrl import repo
from vctrl.index import read_index, write_index, add_to_index


def setup_temp_repo():
    temp_dir = tempfile.mkdtemp()
    os.makedirs(os.path.join(temp_dir, ".vctrl"))

    # Patch repo_path
    import vctrl.index
    repo.repo_path = lambda: os.path.join(temp_dir, ".vctrl")
    vctrl.index.repo_path = repo.repo_path
    vctrl.index.index_file = os.path.join(repo.repo_path(), "index")

    return temp_dir


def test_read_empty_index():
    temp_dir = setup_temp_repo()
    try:
        assert read_index() == {}
    finally:
        shutil.rmtree(temp_dir)


def test_write_and_read_index():
    temp_dir = setup_temp_repo()
    try:
        sample_index = {"file1.txt": "abc123", "main.py": "def456"}
        write_index(sample_index)
        assert read_index() == sample_index
    finally:
        shutil.rmtree(temp_dir)


def test_add_to_index_creates_file():
    temp_dir = setup_temp_repo()
    try:
        add_to_index("file.txt", "abc123")
        assert read_index() == {"file.txt": "abc123"}
    finally:
        shutil.rmtree(temp_dir)


def test_add_to_index_overwrites_existing():
    temp_dir = setup_temp_repo()
    try:
        add_to_index("file.txt", "abc123")
        add_to_index("file.txt", "zzz999")
        assert read_index() == {"file.txt": "zzz999"}
    finally:
        shutil.rmtree(temp_dir)


def test_add_multiple_files():
    temp_dir = setup_temp_repo()
    try:
        add_to_index("file1.txt", "a1")
        add_to_index("file2.txt", "b2")
        add_to_index("dir/file3.txt", "c3")
        assert read_index() == {
            "file1.txt": "a1",
            "file2.txt": "b2",
            "dir/file3.txt": "c3"
        }
    finally:
        shutil.rmtree(temp_dir)


def test_index_file_is_valid_json():
    temp_dir = setup_temp_repo()
    try:
        add_to_index("main.py", "xyz789")
        index_path = os.path.join(repo.repo_path(), "index")
        with open(index_path) as f:
            data = json.load(f)
        assert data["main.py"] == "xyz789"
    finally:
        shutil.rmtree(temp_dir)


def test_write_index_overwrites_completely():
    temp_dir = setup_temp_repo()
    try:
        write_index({"file1.txt": "abc123"})
        write_index({"newfile.py": "zzz999"})
        assert read_index() == {"newfile.py": "zzz999"}
    finally:
        shutil.rmtree(temp_dir)


def test_add_to_index_with_empty_path_or_oid():
    temp_dir = setup_temp_repo()
    try:
        with pytest.raises(TypeError):
            add_to_index(None, "abc123")

        with pytest.raises(TypeError):
            add_to_index("file.txt", None)

        with pytest.raises(TypeError):
            add_to_index("", "")
    finally:
        shutil.rmtree(temp_dir)


def test_read_index_with_invalid_json_raises():
    temp_dir = setup_temp_repo()
    try:
        index_path = os.path.join(repo.repo_path(), "index")
        with open(index_path, "w") as f:
            f.write("{invalid json")

        with pytest.raises(json.JSONDecodeError):
            read_index()
    finally:
        shutil.rmtree(temp_dir)


def test_large_index():
    temp_dir = setup_temp_repo()
    try:
        big_index = {f"file_{i}.txt": f"oid_{i}" for i in range(1000)}
        write_index(big_index)
        assert read_index() == big_index
    finally:
        shutil.rmtree(temp_dir)


def test_unicode_paths_and_oids():
    temp_dir = setup_temp_repo()
    try:
        unicode_path = "📁🚀✨file.py"
        unicode_oid = "🌟abc123🌍"
        add_to_index(unicode_path, unicode_oid)
        assert read_index()[unicode_path] == unicode_oid
    finally:
        shutil.rmtree(temp_dir)

