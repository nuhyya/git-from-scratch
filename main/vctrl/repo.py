import os

#initialises and manages repo structure 

def repo_path():
    return os.path.join(os.getcwd())

def init(path=None):
    if path is None:
        path = repo_path()
    path = os.path.join(path, ".vctrl")
    os.makedirs(os.path.join(path, "refs"), exist_ok = True)
    os.makedirs(os.path.join(path, "objects"), exist_ok = True)

    with open(os.path.join(path, "HEAD"), "w") as f:
        f.write("ref: refs/heads/main")

    print(f"Initialised empty repo with path {path}")
    return path






    
