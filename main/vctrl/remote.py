import os
import requests

def push(remote_url, repo_path):
    """Push all refs and objects to the remote."""
    for root, _, files in os.walk(os.path.join(repo_path, ".vctrl", "refs", "heads")):
        for f in files:
            local_ref = os.path.join(root, f)
            with open(local_ref, 'r') as fr:
                oid = fr.read().strip()
            ref_name = os.path.relpath(local_ref, os.path.join(repo_path, ".vctrl"))
            requests.post(f"{remote_url}/upload_ref", json={"ref": ref_name, "oid": oid})

    for root, _, files in os.walk(os.path.join(repo_path, ".vctrl", "objects")):
        for f in files:
            obj_path = os.path.join(root, f)
            with open(obj_path, 'rb') as fo:
                data = fo.read()
            rel_path = os.path.relpath(obj_path, os.path.join(repo_path, ".vctrl"))
            requests.post(f"{remote_url}/upload_object", files={"file": (rel_path, data)})

def pull(remote_url, repo_path):
    """Pull refs and objects from the remote."""
    resp = requests.get(f"{remote_url}/refs")
    refs = resp.json()
    for ref, oid in refs.items():
        ref_path = os.path.join(repo_path, ".vctrl", ref)
        os.makedirs(os.path.dirname(ref_path), exist_ok=True)
        with open(ref_path, 'w') as f:
            f.write(oid)

    resp = requests.get(f"{remote_url}/objects")
    for obj_name, obj_data in resp.json().items():
        obj_path = os.path.join(repo_path, ".vctrl", "objects", obj_name)
        os.makedirs(os.path.dirname(obj_path), exist_ok=True)
        with open(obj_path, 'wb') as f:
            f.write(bytes.fromhex(obj_data))

def clone(remote_url, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    pull(remote_url, dest_dir)
    print(f"Cloned into {dest_dir}")
