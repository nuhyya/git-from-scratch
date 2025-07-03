import os

def repo_path():
    current = os.getcwd()
    while current != "/":
        candidate = os.path.join(current, ".vctrl")
        if os.path.isdir(candidate):
            return candidate
        current = os.path.dirname(current)
    raise Exception("❌ Not inside a vctrl repository")

def init(path=None):
    if path is None:
        path = repo_path()
    path = os.path.join(path, ".vctrl")
    os.makedirs(os.path.join(path, "refs", "heads"), exist_ok=True)
    os.makedirs(os.path.join(path, "objects"), exist_ok=True)

    with open(os.path.join(path, "HEAD"), "w") as f:
        f.write("ref: refs/heads/main")

    # ✅ Create empty main ref
    open(os.path.join(path, "refs", "heads", "main"), "w").close()

    print(f"Initialised empty repo with path {path}")
    return path

