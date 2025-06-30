#!/usr/bin/env python3
"""
Auto-installer for vctrl
Downloads only the 'main/' folder from GitHub, installs, and runs vctrl
"""

import sys
import os
import tempfile
import subprocess
import urllib.request
import zipfile
import shutil

# ✅ Correct GitHub ZIP URL for full repo
ZIP_URL = "https://github.com/nuhyya/git-from-scratch/archive/refs/heads/main.zip"

def download_and_extract():
    print("📦 Downloading vctrl...")
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, "vctrl.zip")

        try:
            urllib.request.urlretrieve(ZIP_URL, zip_path)
        except Exception as e:
            print(f"❌ Failed to download: {e}")
            return None

        extract_dir = os.path.join(temp_dir, "extracted")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        # GitHub zip root folder is like: git-from-scratch-main/
        root_dirs = [d for d in os.listdir(extract_dir) if os.path.isdir(os.path.join(extract_dir, d))]
        if not root_dirs:
            print("❌ No root project directory found")
            return None

        root_path = os.path.join(extract_dir, root_dirs[0])
        main_path = os.path.join(root_path, "main")

        if not os.path.exists(main_path):
            print("❌ main/ folder not found in extracted archive")
            return None

        install_dir = os.path.expanduser("~/.vctrl")
        if os.path.exists(install_dir):
            shutil.rmtree(install_dir)
        shutil.copytree(main_path, install_dir)

        return install_dir

def install_vctrl(project_path):
    print("🔧 Installing vctrl...")

    requirements_path = os.path.join(project_path, "requirements.txt")
    if os.path.exists(requirements_path):
        print("📋 Installing dependencies...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_path, '--user'])
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False

    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-e', project_path, '--user'])
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install vctrl: {e}")
        return False

def run_vctrl():
    try:
        from vctrl.cli import main as vctrl_main
        vctrl_main()
    except ImportError as e:
        print(f"❌ Failed to import vctrl: {e}")
        sys.exit(1)

def main():
    try:
        import vctrl
        print("✅ vctrl already installed, running...")
        run_vctrl()
        return
    except ImportError:
        pass

    print("🚀 vctrl not found, installing...")

    project_path = download_and_extract()
    if not project_path:
        print("❌ Installation failed")
        sys.exit(1)

    if not install_vctrl(project_path):
        print("❌ Installation failed during setup")
        sys.exit(1)

    print("✅ Installation complete!")
    print("🏃 Running vctrl...")
    run_vctrl()

if __name__ == "__main__":
    main()

