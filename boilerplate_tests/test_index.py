from vctrl.index import add_to_index, read_index

def test_add():
    add_to_index("file.txt", "abc123")
    assert read_index()["file.txt"] == "abc123"
