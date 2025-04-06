import requests
import json
import argparse
import os

# GitHub API endpoint for listing organizations
ORG_API_URL = "https://api.github.com/user/orgs"

# GitHub API endpoint for listing repositories
REPO_API_URL = "https://api.github.com/orgs/{org}/repos"

# Headers for authorization
def get_headers(pat):
    """Return headers for authentication"""
    return {'Authorization': f'token {pat}'}

def fetch_organizations(pat):
    """Fetch organizations that the authenticated user belongs to"""
    url = ORG_API_URL
    orgs = []
    page = 1
    
    while True:
        response = requests.get(url, headers=get_headers(pat), params={'page': page, 'per_page': 100})
        if response.status_code != 200:
            print(f"Error fetching organizations: {response.status_code}")
            return []
        
        data = response.json()
        if not data:
            break
        
        orgs.extend([org['login'] for org in data])
        page += 1
    
    return orgs

def fetch_repositories(org_name, pat):
    """Fetch repositories from a given GitHub organization"""
    url = REPO_API_URL.format(org=org_name)
    repos = []
    page = 1
    
    while True:
        response = requests.get(url, headers=get_headers(pat), params={'page': page, 'per_page': 100})
        if response.status_code != 200:
            print(f"Error fetching repositories for {org_name}: {response.status_code}")
            return []
        
        data = response.json()
        if not data:
            break
        
        repos.extend(data)
        page += 1
    
    return repos

def format_output(all_repositories):
    """Format the output to the required structure"""
    output = []
    for org, repos in all_repositories.items():
        output.append(f"{org}:")
        for repo in repos:
            output.append(f"    {repo['name']} {repo['url']}")
        output.append("")  # Blank line between organizations
    return "\n".join(output)

def write_to_readme(formatted_output):
    """Write the formatted output to the README.md file"""
    with open('README.md', 'w') as readme_file:
        readme_file.write("# GitHub Organization Repository Index\n\n")
        readme_file.write(formatted_output)
        print("README.md file updated successfully.")

def index_repositories(pat):
    """Index repositories from all organizations, format output, and write to README.md"""
    # Fetch organizations dynamically
    print("Fetching organizations...")
    organizations = fetch_organizations(pat)

    all_repositories = {}

    for org in organizations:
        print(f"Fetching repositories for {org}...")
        repos = fetch_repositories(org, pat)
        all_repositories[org] = [{"name": repo['name'], "url": repo['html_url']} for repo in repos]

    # Format the output as required
    formatted_output = format_output(all_repositories)

    # Write the formatted output to README.md
    write_to_readme(formatted_output)

if __name__ == "__main__":
    # Setup command-line argument parsing
    parser = argparse.ArgumentParser(description="GitHub Repository Indexer")
    parser.add_argument('--pat', type=str, required=True, help="GitHub Personal Access Token (PAT)")
    args = parser.parse_args()

    # Run indexing process with the provided PAT
    index_repositories(args.pat)
