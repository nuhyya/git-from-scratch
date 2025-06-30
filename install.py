#!/usr/bin/env python3
"""
Auto-installer and updater for vctrl
Downloads, installs, and runs vctrl in one command
"""

import sys
import os
import tempfile
import subprocess
import urllib.request
import zipfile
import shutil
import hashlib

# Config
GITHUB_ZIP_URL = "https://github.com/nuhyya/git-from-scratch/archive/refs/heads/main.zip"
INSTALL_DIR = os.path.expanduser("~/.vctrl")


def hash_dir(path):
    """Generate a quick hash of directory content"""
    hash_obj = hashlib.sha256()
    for root, _, files in os.walk(path):
        for file in sorted(files):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "rb") as f:
                    hash_obj.update(f.read())
            except Exception:
                continue
    return hash_obj.hexdigest()


def download_and_extract():
    """Download ZIP from GitHub and extract full project (including setup.py)"""
    print("📦 Downloading vctrl...")

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "vctrl.zip")
    extract_dir = os.path.join(temp_dir, "extracted")

    try:
        urllib.request.urlretrieve(GITHUB_ZIP_URL, zip_path)
    except Exception as e:
        print(f"❌ Failed to download: {e}")
        return None

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    # Look for the actual root that contains setup.py (i.e. main/)
    for root, dirs, files in os.walk(extract_dir):
        if "setup.py" in files:
            return root

    print("❌ No valid setup.py found in extracted ZIP")
    return None




def install_vctrl(source_path):
    """Install in editable mode"""
    print("🔧 Installing vctrl in editable mode...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", source_path])
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install: {e}")
        return False


def run_vctrl():
    """Run the vctrl CLI"""
    try:
        from vctrl.cli import main as vctrl_main
        vctrl_main()
    except ImportError as e:
        print(f"❌ Failed to import vctrl CLI: {e}")
        sys.exit(1)


def main():
    print("🚀 Checking vctrl installation...")

    extracted_path = download_and_extract()
    if not extracted_path:
        sys.exit(1)

    if os.path.exists(INSTALL_DIR):
        print("🔍 Checking for updates...")
        old_hash = hash_dir(INSTALL_DIR)
        new_hash = hash_dir(extracted_path)

        if old_hash != new_hash:
            print("⬆️  Update detected! Installing latest version...")
            shutil.rmtree(INSTALL_DIR)
            shutil.copytree(extracted_path, INSTALL_DIR)
            if not install_vctrl(INSTALL_DIR):
                sys.exit(1)
        else:
            print("✅ Already up to date.")
    else:
        print("📂 First-time install...")
        shutil.copytree(extracted_path, INSTALL_DIR)
        if not install_vctrl(INSTALL_DIR):
            sys.exit(1)

    print("🏃 Running vctrl...")
    run_vctrl()


if __name__ == "__main__":
    main()
