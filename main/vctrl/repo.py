import os

#initialises and manages repo structure 

def repo_path():
    return os.path.join(os.getcwd(), ".vctrl")

def init():
    path = repo_path()

    os.makedirs(os.path.join(path, "refs"), exist_ok = True)
    os.makedirs(os.path.join(path, "objects"), exist_ok = True)

    with open(os.path.join(path, "HEAD"), "w") as f:
        f.write("ref: refs/heads/main")

    print("Initialised empty repo with path {path}")
    return path






    
