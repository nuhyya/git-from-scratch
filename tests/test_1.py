import os
import shutil
import tempfile

import pytest

from vctrl import repo
from vctrl.objects import hash_object, get_object
from vctrl.tree import write_tree
from vctrl.commit import create_commit


def setup_temp_repo():
    temp_dir = tempfile.mkdtemp()
    os.makedirs(os.path.join(temp_dir, ".vctrl", "objects"))

    # Patch all repo_path imports
    import vctrl.objects
    import vctrl.tree
    import vctrl.commit

    repo.repo_path = lambda: os.path.join(temp_dir, ".vctrl")
    vctrl.objects.repo_path = repo.repo_path
    vctrl.tree.repo_path = repo.repo_path
    vctrl.commit.repo_path = repo.repo_path

    return temp_dir


def test_hash_and_get_regular_blob():
    temp_dir = setup_temp_repo()
    try:
        content = b"hello world"
        oid = hash_object(content)
        retrieved = get_object(oid, "blob")
        assert retrieved == content
    finally:
        shutil.rmtree(temp_dir)


def test_hash_and_get_empty_blob():
    temp_dir = setup_temp_repo()
    try:
        content = b""
        oid = hash_object(content)
        retrieved = get_object(oid, "blob")
        assert retrieved == content
    finally:
        shutil.rmtree(temp_dir)


def test_hash_and_get_binary_blob():
    temp_dir = setup_temp_repo()
    try:
        content = b"\x00\x01\xff"
        oid = hash_object(content)
        retrieved = get_object(oid, "blob")
        assert retrieved == content
    finally:
        shutil.rmtree(temp_dir)


def test_hash_and_get_unicode_blob():
    temp_dir = setup_temp_repo()
    try:
        content = "🌍🚀".encode("utf-8")
        oid = hash_object(content)
        retrieved = get_object(oid, "blob")
        assert retrieved == content
    finally:
        shutil.rmtree(temp_dir)


def test_tree_and_commit_end_to_end():
    temp_dir = setup_temp_repo()
    original_cwd = os.getcwd()
    os.chdir(temp_dir)
    try:
        os.makedirs("src")
        os.makedirs("emptydir")
        with open("file.txt", "w") as f:
            f.write("This is root")
        with open("src/code.py", "w") as f:
            f.write("print('hi')")
        with open("src/unicode.txt", "w", encoding="utf-8") as f:
            f.write("你好，世界")
        with open("binary.bin", "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00")

        tree_oid = write_tree()
        assert tree_oid is not None

        root_tree = get_object(tree_oid, "tree").decode()
        assert "file.txt" in root_tree
        assert "src" in root_tree
        assert "binary.bin" in root_tree
        assert "emptydir" not in root_tree  # empty directory ignored

        src_oid = next(oid for typ, oid, name in 
                       (line.split() for line in root_tree.strip().split("\n"))
                       if typ == "tree" and name == "src")
        src_tree = get_object(src_oid, "tree").decode()
        assert "code.py" in src_tree
        assert "unicode.txt" in src_tree

        commit_oid = create_commit(
            tree_oid, user_name="Alice", user_email="alice@example.com", message="init"
        )
        commit_data = get_object(commit_oid, "commit").decode()
        assert f"tree {tree_oid}" in commit_data
        assert "author Alice <alice@example.com>" in commit_data
        assert "init" in commit_data

    finally:
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)


def test_write_tree_returns_none_for_empty_repo():
    temp_dir = setup_temp_repo()
    original_cwd = os.getcwd()
    os.chdir(temp_dir)
    try:
        os.makedirs("emptydir")
        tree_oid = write_tree()
        assert tree_oid is None  # ✅ empty directories skipped entirely
    finally:
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)


def test_create_commit_raises_on_empty_tree():
    temp_dir = setup_temp_repo()
    original_cwd = os.getcwd()
    os.chdir(temp_dir)
    try:
        os.makedirs("emptydir")
        tree_oid = write_tree()
        assert tree_oid is None

        with pytest.raises(ValueError):
            create_commit(tree_oid, message="this should fail")

    finally:
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)


def test_unicode_filename_handling():
    temp_dir = setup_temp_repo()
    original_cwd = os.getcwd()
    os.chdir(temp_dir)
    try:
        filename = "你好🌟.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("Unicode filename content")

        tree_oid = write_tree()
        tree_data = get_object(tree_oid, "tree").decode()
        assert filename in tree_data

    finally:
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)


def test_missing_vctrl_raises_error():
    temp_dir = tempfile.mkdtemp()
    original_repo_path = repo.repo_path
    repo.repo_path = lambda: os.path.join(temp_dir, ".vctrl")  # .vctrl is missing

    with pytest.raises(FileNotFoundError):
        hash_object(b"should fail")

    repo.repo_path = original_repo_path
    shutil.rmtree(temp_dir)

