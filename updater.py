import os
import sys
import shutil
import tarfile
import urllib.request
import json
import subprocess

TEMP_DIR_BASE = "/mnt/hdd/update_tmp"
GITHUB_API_URL = "https://api.github.com/repos/{repo}/releases/latest"

def get_app_info():
    """Returns the app directory and executable path."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    current = base_dir
    # Heuristic: Walk up until we find the app root containing 'data' and the executable
    while current != '/':
        if os.path.isdir(os.path.join(current, 'data')):
            for f in os.listdir(current):
                p = os.path.join(current, f)
                if os.path.isfile(p) and os.access(p, os.X_OK) and not p.endswith('.so'):
                    return current, p
        current = os.path.dirname(current)
    return base_dir, sys.executable

def check_for_updates(current_version, repo_name):
    """Checks GitHub for a newer release."""
    url = GITHUB_API_URL.format(repo=repo_name)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Flet-Updater'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            latest_version = data.get("tag_name")
            
            if latest_version and latest_version != current_version:
                assets = data.get("assets", [])
                for asset in assets:
                    if asset.get("name", "").endswith(".tar.gz"):
                        return latest_version, asset.get("browser_download_url")
    except Exception as e:
        print(f"Error checking for updates: {e}")
    return None, None

def perform_update(download_url):
    """Downloads, extracts, and replaces the app."""
    try:
        os.makedirs(TEMP_DIR_BASE, exist_ok=True)
        tar_path = os.path.join(TEMP_DIR_BASE, "update.tar.gz")
        extract_path = os.path.join(TEMP_DIR_BASE, "extracted")
        
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)
        os.makedirs(extract_path)

        print(f"Downloading update from {download_url}...")
        urllib.request.urlretrieve(download_url, tar_path)
        
        print("Extracting update...")
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=extract_path)
            
        app_dir, current_exe = get_app_info()
        
        # In a development environment we don't want to replace ourselves
        if "python" in os.path.basename(current_exe).lower() and app_dir == os.path.dirname(os.path.abspath(__file__)):
            print("Running from source. Update replacement skipped.")
            return True

        script_path = os.path.join(TEMP_DIR_BASE, "update.sh")
        script_content = f"""#!/bin/bash
echo "Waiting for app to close..."
sleep 2

echo "Replacing files in {app_dir}..."
# Remove old files except the script
rm -rf "{app_dir}"/*

echo "Copying new files from {extract_path}..."
# The tarball might extract into a subdirectory (like build/linux/)
# Find the first directory that looks like the app root (has 'data' folder)
NEW_APP_DIR="{extract_path}"
for d in $(find "{extract_path}" -type d -name "data"); do
    NEW_APP_DIR=$(dirname "$d")
    break
done

cp -r "$NEW_APP_DIR"/* "{app_dir}"/

echo "Setting executable permissions..."
chmod +x "{app_dir}"/*

echo "Restarting application..."
"{current_exe}" &

echo "Update finished."
"""
        with open(script_path, "w") as f:
            f.write(script_content)
            
        os.chmod(script_path, 0o755)
        
        print("Starting update script and exiting...")
        subprocess.Popen([script_path], start_new_session=True)
        sys.exit(0)

    except Exception as e:
        print(f"Failed to update: {e}")
        return False
