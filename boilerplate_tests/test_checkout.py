def test_checkout():
    from vctrl.checkout import checkout
    # setup, create commit, switch files
    checkout('<valid_commit_hash>')
    # validate HEAD and working tree state
