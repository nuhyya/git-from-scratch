import shutil
import os
from vctrl.repo import repo_path


def fetch(local_path):
    """Copy refs and objects from another .vctrl repo"""
    for sub in ["refs", "objects"]:
        src = os.path.join(local_path, ".vctrl", sub)
        dst = os.path.join(repo_path(), sub)
        for root, _, files in os.walk(src):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), src)
                os.makedirs(os.path.dirname(os.path.join(dst, rel_path)), exist_ok=True)
                shutil.copy2(os.path.join(root, file), os.path.join(dst, rel_path))
    print("Fetch complete.")
