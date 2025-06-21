from vctrl.objects import hash_object, get_object

def test_hash_and_retrieve():
    oid = hash_object(b"hello world")
    content = get_object(oid)
    assert content == b"hello world"
