from vctrl.commit import create_commit
from vctrl import repo
import os
import shutil
import tempfile


def setup_temp_repo():
    temp_dir = tempfile.mkdtemp()
    os.makedirs(os.path.join(temp_dir, ".vctrl", "objects"))

    import vctrl.objects
    import vctrl.tree
    import vctrl.commit

    repo.repo_path = lambda: os.path.join(temp_dir, ".vctrl")
    vctrl.objects.repo_path = repo.repo_path
    vctrl.tree.repo_path = repo.repo_path
    vctrl.commit.repo_path = repo.repo_path

    return temp_dir


def test_create_commit():
    temp_dir = setup_temp_repo()
    try:
        user = 'user'
        email = 'email@gmail.com'
        commit_oid = create_commit("treeoid123", user, email, message="Init commit")
        assert commit_oid is not None
    finally:
        shutil.rmtree(temp_dir)

