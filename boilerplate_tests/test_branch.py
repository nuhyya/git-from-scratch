def test_branch_creation():
    from vctrl.branch import create_branch
    create_branch(repo, 'feature', '<hash>')
    # assert file exists with hash
