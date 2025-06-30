import os
import shutil
from vctrl import repo

def test_init():
    shutil.rmtree(".vctrl", ignore_errors=True)
    path = repo.init()
    assert os.path.exists(path + "/objects")
    assert os.path.exists(path + "/HEAD")
