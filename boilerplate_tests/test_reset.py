def test_reset():
    from vctrl.reset import reset
    reset(repo, '<commit_hash>')
    # check HEAD
