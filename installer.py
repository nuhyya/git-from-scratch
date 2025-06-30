#!/usr/bin/env python3
"""
Complete auto-installer for vctrl
Downloads, installs, and runs vctrl in one command
"""

import sys
import os
import tempfile
import subprocess
import urllib.request
import zipfile
import shutil

# Configuration
GITHUB_REPO = "yourusername/vctrl"  # Replace with your actual repo
BRANCH = "main"
ZIP_URL = f"https://github.com/{GITHUB_REPO}/archive/{BRANCH}.zip"

def download_and_extract():
    """Download and extract the vctrl package"""
    print("📦 Downloading vctrl...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, "vctrl.zip")
        
        # Download
        try:
            urllib.request.urlretrieve(ZIP_URL, zip_path)
        except Exception as e:
            print(f"❌ Failed to download: {e}")
            return None
        
        # Extract
        extract_dir = os.path.join(temp_dir, "extracted")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Find the actual project directory (usually has the branch name)
        project_dirs = [d for d in os.listdir(extract_dir) 
                       if os.path.isdir(os.path.join(extract_dir, d))]
        
        if not project_dirs:
            print("❌ No project directory found in zip")
            return None
            
        project_path = os.path.join(extract_dir, project_dirs[0])
        
        # Copy to a permanent location
        install_dir = os.path.expanduser("~/.vctrl")
        if os.path.exists(install_dir):
            shutil.rmtree(install_dir)
        shutil.copytree(project_path, install_dir)
        
        return install_dir

def install_vctrl(project_path):
    """Install vctrl and its dependencies"""
    print("🔧 Installing vctrl...")
    
    # Install requirements if they exist
    requirements_path = os.path.join(project_path, "requirements.txt")
    if os.path.exists(requirements_path):
        print("📋 Installing dependencies...")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', 
                '-r', requirements_path, '--user'
            ])
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    # Install the package
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', 
            '-e', project_path, '--user'
        ])
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install vctrl: {e}")
        return False

def run_vctrl():
    """Run vctrl with the provided arguments"""
    try:
        from vctrl.cli import main as vctrl_main
        vctrl_main()
    except ImportError as e:
        print(f"❌ Failed to import vctrl: {e}")
        sys.exit(1)

def main():
    """Main entry point"""
    # Check if vctrl is already installed
    try:
        import vctrl
        print("✅ vctrl already installed, running...")
        run_vctrl()
        return
    except ImportError:
        pass
    
    print("🚀 vctrl not found, installing...")
    
    # Download and extract
    project_path = download_and_extract()
    if not project_path:
        print("❌ Installation failed")
        sys.exit(1)
    
    # Install
    if not install_vctrl(project_path):
        print("❌ Installation failed")
        sys.exit(1)
    
    print("✅ Installation complete!")
    
    # Run vctrl
    print("🏃 Running vctrl...")
    run_vctrl()

if __name__ == '__main__':
    main()
