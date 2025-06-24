from vctrl.refs import update_ref, get_ref

def test_ref_update():
    update_ref("refs/heads/master", "oid123")
    assert get_ref("refs/heads/master") == "oid123"
