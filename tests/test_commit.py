from vctrl.commit import create_commit

def test_create_commit():
    user = 'user'
    email = 'email@gmail.com'
    commit_oid = create_commit("treeoid123", user, email, message="Init commit")
    assert len(commit_oid) == 40
