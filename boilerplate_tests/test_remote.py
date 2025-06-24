def test_push_pull():
    from vctrl.remote import push, pull
    assert push('http://localhost:5000', 'path/to/repo.zip') == 200
    assert isinstance(pull('http://localhost:5000'), bytes)
