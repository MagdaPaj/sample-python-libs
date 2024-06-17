import requests
import sys

github_token = "YOUR_GITHUB_TOKEN"
version = "YOUR_VERSION"

headers = {
    'Accept': 'application/vnd.github.v3+json',
    'Authorization': f'token {github_token}',
}

# First, get the release information
url = f"https://api.github.com/repos/MagdaPaj/sample-python-libs/releases/tags/v{version}"
response = requests.get(url, headers=headers)

if response.status_code != 200:
    print("Failed to get release information")
    sys.exit(1)

release_data = response.json()

# Get the URL and name of the first asset
asset_url = release_data['assets'][0]['url']
asset_name = release_data['assets'][0]['name']

if 'custom_exceptions_lib' not in asset_name:
    print("No asset with 'custom_exceptions_lib' in the name found")
    sys.exit(1)

# Update the headers for the asset download
headers['Accept'] = 'application/octet-stream'

response = requests.get(asset_url, headers=headers, stream=True)
if response.status_code != 200:
    print("Failed to download asset")
    sys.exit(1)

with open(asset_name, 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)