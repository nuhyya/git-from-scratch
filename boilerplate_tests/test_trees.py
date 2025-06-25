import os
import shutil
import tempfile

from vctrl.tree import write_tree
from vctrl.objects import get_object
from vctrl.objects import repo_path as original_repo_path

def test_write_tree_creates_nested_tree():
    # --- Setup ---
    temp_dir = tempfile.mkdtemp()
    vctrl_dir = os.path.join(temp_dir, ".vctrl", "objects")
    os.makedirs(vctrl_dir)

    # Patch repo_path() temporarily
    import vctrl.objects
    vctrl.objects.repo_path = lambda: os.path.join(temp_dir, ".vctrl")

    # Move into temp directory
    original_cwd = os.getcwd()
    os.chdir(temp_dir)

    try:
        # Create files and directories
        os.makedirs("src")
        with open("a.txt", "w") as f:
            f.write("hello world")
        with open("src/main.py", "w") as f:
            f.write("print('hi')")
        with open("src/util.py", "w") as f:
            f.write("def util(): pass")

        # --- Run ---
        tree_oid = write_tree()
        tree_data = get_object(tree_oid, "tree").decode()
        lines = tree_data.strip().split("\n")

        # --- Check root tree entries ---
        assert any("blob" in line and "a.txt" in line for line in lines)
        assert any("tree" in line and "src" in line for line in lines)

        # --- Check nested src/ tree entries ---
        src_tree_oid = next(oid for typ, oid, name in 
                            (line.split() for line in lines) 
                            if typ == "tree" and name == "src")
        src_tree_data = get_object(src_tree_oid, "tree").decode()
        assert "main.py" in src_tree_data
        assert "util.py" in src_tree_data

    finally:
        # --- Cleanup ---
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)
        vctrl.objects.repo_path = original_repo_path  # restore original


