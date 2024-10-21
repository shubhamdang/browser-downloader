import os
import requests
import shutil
import zipfile


import requests
import platform

def get_windows_version():
    version = platform.system()
    if version == "Windows":
        release = platform.release()
        if release == '10':
            return 'win10'
        elif release == '11':
            return 'win11'
    return None

def fetch_versions(browser, os):
    url = f"https://stage-api.lambdatestinternal.com/api/v2/capability?grid=selenium&browser={browser}&os={os}"
    response = requests.get(url)
    return response.json()

def get_latest_versions(browser):
    detected_os_version = get_windows_version()
    if detected_os_version is None:
        print("Not running on Windows")
        return None

    data = fetch_versions(browser, detected_os_version)
    beta_versions = []
    stable_versions = []

    # Iterate through the versions and extract the latest 10 for beta and stable
    for version in data['versions']:
        if version['channel_type'] == 'beta' and len(beta_versions) < 10:
            beta_versions.append(version['version'])
        elif version['channel_type'] == 'stable' and len(stable_versions) < 10:
            stable_versions.append(version['version'])

    return {
        'beta_versions': beta_versions,
        'stable_versions': stable_versions
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

# Chrome and Firefox configuration

chrome_versions = get_latest_versions('chrome')
edge_versions = get_latest_versions('edge')
firefox_versions = get_latest_versions('firefox')

# chrome_versions_list = chrome_versions['beta_versions'] + chrome_versions['stable_versions']
# edge_versions_list = edge_versions['beta_versions'] + edge_versions['stable_versions']
# firefox_versions_list = firefox_versions['beta_versions'] + firefox_versions['stable_versions']

chrome_versions_list =  chrome_versions['stable_versions']
edge_versions_list =  edge_versions['stable_versions']
firefox_versions_list =  firefox_versions['stable_versions']

# Directories for Chrome
chrome_folder = "G:\\chrome\\"
new_chrome_folder = "G:\\New_chrome_browser\\"
chrome_drivers_folder = "G:\\drivers\\Chrome\\"

# Directories for Firefox
firefox_folder = "G:\\firefox\\"
new_firefox_folder = "G:\\New_browser_firefox\\"

# Directories for Edge
edge_folder = "C:\\Program Files (x86)\\Microsoft\\EdgeCore"
new_edge_folder = "G:\\New_browser_edge\\"
edge_drivers_folder = "G:\\drivers\\edge"

# 1. Create directories for Chrome and Firefox
create_directories([chrome_folder, new_chrome_folder, firefox_folder, new_firefox_folder, edge_folder, new_edge_folder, edge_drivers_folder])


for version in chrome_versions_list:
    #Download Chrome browser
    url = f"https://ltbrowserdeploy.lambdatest.com/windows/chrome/Google+Chrome+{version}.zip"
    download_file(url, new_chrome_folder)

    # Download Chrome drivers
    url = f"https://ltbrowserdeploy.lambdatest.com/windows/drivers/Chrome/{version}.zip"
    download_file(url, new_chrome_folder)

    #Unzip Chrome drivers
    zip_path = os.path.join(new_chrome_folder, f"{version}.zip")
    unzip_file(zip_path, chrome_drivers_folder)

    #Unzip Chrome browser
    zip_path = os.path.join(new_chrome_folder, f"Google+Chrome+{version}.zip")
    unzip_file(zip_path, chrome_folder)

delete_directory(new_chrome_folder)


# 6. Download Firefox browser
for version in firefox_versions_list:
    url = f"https://ltbrowserdeploy.lambdatest.com/windows/firefox/{version}.zip"
    download_file(url, new_firefox_folder)

    zip_path = os.path.join(new_firefox_folder, f"{version}.zip")
    unzip_file(zip_path, firefox_folder)

delete_directory(new_firefox_folder)

beta_version = '.'.join(edge_versions['beta_versions'][0].split('.')[:2])
edge_versions_list.append(beta_version)

for version in edge_versions_list:
    #Download Edge browser
    url = f"https://ltbrowserdeploy.lambdatest.com/windows/edge/Edge+{version}.zip"
    download_file(url, new_edge_folder)

    # Download Edge drivers
    url = f"https://ltbrowserdeploy.lambdatest.com/windows/drivers/Edge/{version}.zip"
    download_file(url, new_edge_folder)

    #Unzip Edge drivers
    zip_path = os.path.join(new_edge_folder, f"{version}.zip")
    unzip_file(zip_path, edge_drivers_folder)

    #Unzip Edge browser
    zip_path = os.path.join(new_edge_folder, f"Edge+{version}.zip")
    unzip_file(zip_path, edge_folder)

    # Handling for dev and beta 
    os.rename(f'{edge_drivers_folder}\\{beta_version}', f'{edge_drivers_folder}\\beta)
    os.rename(f"{edge_folder}\\{beta_version}", f"{edge_folder}\\beta")

delete_directory(new_edge_folder)
