import os
import requests
import shutil
import zipfile
import platform
import argparse

def get_windows_version():
    version = platform.system()
    if version == "Windows":
        release = platform.release()
        if release == '10':
            return 'win10'
        elif release == '11':
            return 'win11'
    return None

# Determine the correct API URL based on branch
def get_api_url(browser, os, branch):
    if branch == 'prod':
        return f"https://api.lambdatest.com/api/v2/capability?grid=selenium&browser={browser}&os={os}"
    elif branch == 'stage':
        return f"https://stage-api.lambdatestinternal.com/api/v2/capability?grid=selenium&browser={browser}&os={os}"
    else:
        # For any other branch, default to stage URL
        return f"https://stage-api.lambdatestinternal.com/api/v2/capability?grid=selenium&browser={browser}&os={os}"

def fetch_versions(browser, os, branch):
    url = get_api_url(browser, os, branch)
    response = requests.get(url)
    return response.json()

def get_latest_versions(browser, branch):
    detected_os_version = get_windows_version()
    if detected_os_version is None:
        print("Not running on Windows")
        return None

    data = fetch_versions(browser, detected_os_version, branch)
    beta_versions = []
    stable_versions = []
    dev_versions = []

    # Iterate through the versions and extract the latest 5 for each category
    for version in data['versions']:
        if version['channel_type'] == 'beta' and len(beta_versions) < 5:
            beta_versions.append(version['version'])
        elif version['channel_type'] == 'stable' and len(stable_versions) < 5:
            stable_versions.append(version['version'])
        elif version['channel_type'] == 'dev' and len(dev_versions) < 5:
            dev_versions.append(version['version'])

    return {
        'beta_versions': beta_versions,
        'stable_versions': stable_versions,
        'dev_versions' : dev_versions
    }

# Function to create directories if they don't exist
def create_directories(directories):
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
        else:
            print(f"Directory already exists: {directory}")

# Function to download a file
def download_file(url, dest):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        zip_path = os.path.join(dest, os.path.basename(url))
        with open(zip_path, 'wb') as file:
            shutil.copyfileobj(response.raw, file)
        print(f"Downloaded: {zip_path}")
        return zip_path
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}: {e}")
        return None

# Function to unzip a file
def unzip_file(src, dest):
    try:
        with zipfile.ZipFile(src, 'r') as zip_ref:
            zip_ref.extractall(dest)
        print(f"Extracted {src} to {dest}")
    except zipfile.BadZipFile:
        print(f"Error unzipping {src}")

# Function to delete files or directories
def delete_directory(path):
    try:
        shutil.rmtree(path)
        print(f"Deleted: {path}")
    except FileNotFoundError:
        print(f"Directory not found: {path}")
    except Exception as e:
        print(f"Error deleting {path}: {e}")

# Main execution logic
def main(branch):
    chrome_versions = get_latest_versions('chrome', branch)
    edge_versions = get_latest_versions('edge', branch)
    firefox_versions = get_latest_versions('firefox', branch)

    chrome_versions_list = chrome_versions['stable_versions']
    edge_versions_list = edge_versions['stable_versions']
    firefox_versions_list = firefox_versions['stable_versions']

    # Directories for Chrome, Firefox, and Edge
    chrome_folder = "G:\\chrome\\"
    new_chrome_folder = "G:\\New_chrome_browser\\"
    chrome_drivers_folder = "G:\\drivers\\Chrome\\"

    firefox_folder = "G:\\firefox\\"
    new_firefox_folder = "G:\\New_browser_firefox\\"

    edge_folder = "C:\\Program Files (x86)\\Microsoft\\EdgeCore"
    new_edge_folder = "G:\\New_browser_edge\\"
    edge_drivers_folder = "G:\\drivers\\edge"

    # Deleting old directories
    delete_directory(chrome_folder)
    delete_directory(chrome_drivers_folder)
    delete_directory(firefox_folder)
    delete_directory(edge_folder)
    delete_directory(edge_drivers_folder)

    # Create necessary directories
    create_directories([chrome_folder, new_chrome_folder, firefox_folder, new_firefox_folder, edge_folder, new_edge_folder, edge_drivers_folder])

    # Download and unzip Chrome versions
    #TODO Need to Revert Back
    chrome_versions_list.append('133.0')

    for version in chrome_versions_list:
        if branch == 'prod':
            url = f"https://ltbrowserdeploy.lambdatest.com/windows/chrome/Google+Chrome+{version}.zip"
        else:
            url = f"https://stage-ltbrowserdeploy.lambdatestinternal.com/windows/chrome/Google+Chrome+{version}.zip"
        download_file(url, new_chrome_folder)

        if branch == 'prod':
            url = f"https://ltbrowserdeploy.lambdatest.com/windows/drivers/Chrome/{version}.zip"
        else:
            url = f"https://stage-ltbrowserdeploy.lambdatestinternal.com/windows/drivers/Chrome/{version}.zip"

        download_file(url, new_chrome_folder)

        unzip_file(os.path.join(new_chrome_folder, f"{version}.zip"), chrome_drivers_folder)
        unzip_file(os.path.join(new_chrome_folder, f"Google+Chrome+{version}.zip"), chrome_folder)

    delete_directory(new_chrome_folder)

    # Download and unzip Firefox versions
    for version in firefox_versions_list:
        if branch == 'prod':
            url = f"https://ltbrowserdeploy.lambdatest.com/windows/firefox/{version}.zip"
        else:
            url = f"https://stage-ltbrowserdeploy.lambdatestinternal.com/windows/firefox/{version}.zip"

        download_file(url, new_firefox_folder)
        unzip_file(os.path.join(new_firefox_folder, f"{version}.zip"), firefox_folder)

    delete_directory(new_firefox_folder)

    # Download and unzip Edge versions
    for version in edge_versions_list:
        if branch == 'prod':
            url = f"https://ltbrowserdeploy.lambdatest.com/windows/edge/Edge+{version}.zip"
        else:
            url = f"https://stage-ltbrowserdeploy.lambdatestinternal.com/windows/edge/Edge+{version}.zip"
        download_file(url, new_edge_folder)

        if branch == 'prod':
            url = f"https://ltbrowserdeploy.lambdatest.com/windows/drivers/Edge/{version}.zip"
        else:
            url = f"https://stage-ltbrowserdeploy.lambdatestinternal.com/windows/drivers/Edge/{version}.zip"
        download_file(url, new_edge_folder)

        unzip_file(os.path.join(new_edge_folder, f"{version}.zip"), edge_drivers_folder)
        unzip_file(os.path.join(new_edge_folder, f"Edge+{version}.zip"), edge_folder)

    # Handle Edge beta and dev versions
    handle_edge_versions(edge_versions['beta_versions'][0], 'beta', new_edge_folder, edge_drivers_folder, edge_folder, branch)
    handle_edge_versions(edge_versions['dev_versions'][0], 'dev', new_edge_folder, edge_drivers_folder, edge_folder, branch)

    delete_directory(new_edge_folder)

# Function to handle Edge beta and dev versions
def handle_edge_versions(version, version_type, new_edge_folder, edge_drivers_folder, edge_folder, branch):
    if branch == 'prod':
        url = f"https://ltbrowserdeploy.lambdatest.com/windows/edge/{version_type}/Edge+{version}.zip"
    else:
        url = f"https://stage-ltbrowserdeploy.lambdatestinternal.com/windows/edge/{version_type}/Edge+{version}.zip"
    download_file(url, new_edge_folder)

    if branch == 'prod':
        url = f"https://ltbrowserdeploy.lambdatest.com/windows/drivers/Edge/{version_type}/{version}.zip"
    else:
        url = f"https://stage-ltbrowserdeploy.lambdatestinternal.com/windows/edge/{version_type}/Edge+{version}.zip"

    download_file(url, new_edge_folder)

    unzip_file(os.path.join(new_edge_folder, f"{version}.zip"), edge_drivers_folder)
    unzip_file(os.path.join(new_edge_folder, f"Edge+{version}.zip"), edge_folder)

    if os.path.exists(f'{edge_drivers_folder}\\{version_type}'):
        delete_directory(f'{edge_drivers_folder}\\{version_type}')

    if os.path.exists(f'{edge_folder}\\{version_type}'):
        delete_directory(f'{edge_folder}\\{version_type}')

    os.rename(f'{edge_drivers_folder}\\{version}', f'{edge_drivers_folder}\\{version_type}')
    os.rename(f'{edge_folder}\\Edge {version}', f'{edge_folder}\\{version_type}')

# Entry point
if __name__ == "__main__":
    # Set up argument parser to get branch from command line
    parser = argparse.ArgumentParser(description="Download and configure browser versions.")
    parser.add_argument('--branch', type=str, required=True, help='Branch to use (e.g. prod, stage, or other)')
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Run the main function with the provided branch
    main(args.branch)
