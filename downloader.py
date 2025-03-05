import os
import requests
import shutil
import zipfile
import platform
import argparse

# Function to determine the Windows version
def get_windows_version():
    version = platform.system()
    if version == "Windows":
        release = platform.release()
        if release == '10':
            return 'win10'
        elif release == '11':
            return 'win11'
    return None

# Function to determine the correct API URL based on branch
def get_api_url(browser, os, branch):
    if branch == 'prod':
        return f"https://api.lambdatest.com/api/v2/capability?grid=selenium&browser={browser}&os={os}"
    elif branch == 'stage':
        return f"https://stage-api.lambdatestinternal.com/api/v2/capability?grid=selenium&browser={browser}&os={os}"
    else:
        # For any other branch, default to stage URL
        return f"https://stage-api.lambdatestinternal.com/api/v2/capability?grid=selenium&browser={browser}&os={os}"

# Fetch versions from the LambdaTest API
def fetch_versions(browser, os, branch):
    url = get_api_url(browser, os, branch)
    response = requests.get(url)
    return response.json()

# Get latest versions from the API
def get_latest_versions(browser, branch):
    detected_os_version = get_windows_version()
    if detected_os_version is None:
        print("Not running on Windows")
        return None
    data = fetch_versions(browser, detected_os_version, branch)
    beta_versions = []
    stable_versions = []
    dev_versions = []
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
        'dev_versions': dev_versions
    }

# Check if a specific version exists in the deployment URL
def check_version_exists(base_url, browser, version):
    if browser == 'chrome':
        file_name = f"Google Chrome {version}.zip"
    elif browser == 'edge':
        file_name = f"Edge {version}.zip"
    elif browser == 'firefox':
        file_name = f"{version}.zip"
    else:
        return False

    url = f"{base_url}{file_name}"
    try:
        response = requests.head(url)  # Use HEAD request to check existence
        return response.status_code == 200  # 200 means the file exists
    except requests.exceptions.RequestException:
        return False

# Generate future versions (+1 to +5)
def generate_future_versions(latest_version):
    try:
        major, minor = map(int, latest_version.split('.'))
        return [f"{major+i}.0" for i in range(1, 6)]  # Append ".0" to each version
    except ValueError:
        print(f"Invalid version format: {latest_version}")
        return []

# Main execution logic
def main(branch):
    # Base URLs for deployment
    if branch == 'prod':
        chrome_base_url = "https://ltbrowserdeploy.lambdatest.com/windows/chrome/"
        firefox_base_url = "https://ltbrowserdeploy.lambdatest.com/windows/firefox/"
        edge_base_url = "https://ltbrowserdeploy.lambdatest.com/windows/edge/"
        chrome_driver_base_url = "https://ltbrowserdeploy.lambdatest.com/windows/drivers/Chrome/"
        edge_driver_base_url = "https://ltbrowserdeploy.lambdatest.com/windows/drivers/Edge/"
    else:  # stage
        chrome_base_url = "https://stage-ltbrowserdeploy.lambdatestinternal.com/windows/chrome/"
        firefox_base_url = "https://stage-ltbrowserdeploy.lambdatestinternal.com/windows/firefox/"
        edge_base_url = "https://stage-ltbrowserdeploy.lambdatestinternal.com/windows/edge/"
        chrome_driver_base_url = "https://stage-ltbrowserdeploy.lambdatestinternal.com/windows/drivers/Chrome/"
        edge_driver_base_url = "https://stage-ltbrowserdeploy.lambdatestinternal.com/windows/drivers/Edge/"

    # Fetch latest stable versions from API
    chrome_versions_api = get_latest_versions('chrome', branch)['stable_versions']
    firefox_versions_api = get_latest_versions('firefox', branch)['stable_versions']
    edge_versions_api = get_latest_versions('edge', branch)['stable_versions']

    # Get the latest stable version for each browser
    chrome_latest = chrome_versions_api[0]
    firefox_latest = firefox_versions_api[0]
    edge_latest = edge_versions_api[0]

    # Generate future versions (+1 to +5) for each browser
    chrome_future_versions = generate_future_versions(chrome_latest)
    firefox_future_versions = generate_future_versions(firefox_latest)
    edge_future_versions = generate_future_versions(edge_latest)

    # Filter future versions to include only those that exist in the deployment URLs
    chrome_future_filtered = [v for v in chrome_future_versions if check_version_exists(chrome_base_url, 'chrome', v)]
    firefox_future_filtered = [v for v in firefox_future_versions if check_version_exists(firefox_base_url, 'firefox', v)]
    edge_future_filtered = [v for v in edge_future_versions if check_version_exists(edge_base_url, 'edge', v)]

    # Combine future versions with API versions and sort to get the top 5
    chrome_versions_list = sorted(set(chrome_future_filtered + chrome_versions_api), reverse=True)[:5]
    firefox_versions_list = sorted(set(firefox_future_filtered + firefox_versions_api), reverse=True)[:5]
    edge_versions_list = sorted(set(edge_future_filtered + edge_versions_api), reverse=True)[:5]

    print(f"Filtered Chrome Versions: {chrome_versions_list}")
    print(f"Filtered Firefox Versions: {firefox_versions_list}")
    print(f"Filtered Edge Versions: {edge_versions_list}")

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
    for version in chrome_versions_list:
        download_and_unzip(chrome_base_url, 'chrome', version, new_chrome_folder, chrome_drivers_folder, chrome_folder, branch, chrome_driver_base_url)
    delete_directory(new_chrome_folder)

    # Download and unzip Firefox versions
    for version in firefox_versions_list:
        download_and_unzip(firefox_base_url, 'firefox', version, new_firefox_folder, None, firefox_folder, branch, None)
    delete_directory(new_firefox_folder)

    # Download and unzip Edge versions
    for version in edge_versions_list:
        download_and_unzip(edge_base_url, 'edge', version, new_edge_folder, edge_drivers_folder, edge_folder, branch, edge_driver_base_url)
    delete_directory(new_edge_folder)

# Helper function to download and unzip files
def download_and_unzip(base_url, browser, version, temp_folder, drivers_folder, browser_folder, branch, driver_base_url=None):
    if browser == 'chrome':
        browser_file_name = f"Google Chrome {version}.zip"
        driver_file_name = f"{version}.zip"
    elif browser == 'edge':
        browser_file_name = f"Edge {version}.zip"
        driver_file_name = f"{version}.zip"
    elif browser == 'firefox':
        browser_file_name = f"{version}.zip"
        driver_file_name = None
    else:
        return

    browser_url = f"{base_url}{browser_file_name}"
    driver_url = f"{driver_base_url}{driver_file_name}" if driver_base_url and driver_file_name else None

    # Download browser zip
    browser_zip_path = download_file(browser_url, temp_folder)
    if browser_zip_path:
        unzip_file(browser_zip_path, browser_folder)

    # Download driver zip (if applicable)
    if drivers_folder and driver_url:
        driver_zip_path = download_file(driver_url, temp_folder)
        if driver_zip_path:
            unzip_file(driver_zip_path, drivers_folder)

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

# Entry point
if __name__ == "__main__":
    # Set up argument parser to get branch from command line
    parser = argparse.ArgumentParser(description="Download and configure browser versions.")
    parser.add_argument('--branch', type=str, required=True, help='Branch to use (e.g. prod, stage, or other)')
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Run the main function with the provided branch
    main(args.branch)
