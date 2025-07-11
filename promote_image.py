import subprocess
import sys
import os

# Ensure that the correct number of arguments are provided
if len(sys.argv) < 5:
    print("Usage: python promote_image.py <GITHUB_USERNAME> <GITHUB_TOKEN> <REPO_URL> <NEW_IMAGE> <GITHUB_REPO>")
    sys.exit(1)

# Get the command-line arguments
GITHUB_USERNAME = sys.argv[1]  # GitHub username
GITHUB_TOKEN = sys.argv[2]     # GitHub token
REPO_URL = sys.argv[3]         # Repo URL (e.g., "chasecadet/wiz-test-helm.git")
NEW_IMAGE = sys.argv[4]        # New image tag
GITHUB_REPO = sys.argv[5]      # GitHub repo name
BASE_BRANCH = "main"           # Default branch

# Clone the repository
clone_command = f"git clone https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{REPO_URL}"
print(f"Cloning repository from https://github.com/{REPO_URL}...")

# Run the clone command and check for errors
try:
    subprocess.run(clone_command, shell=True, check=True)
    print(f"Successfully cloned {REPO_URL}")
except subprocess.CalledProcessError as e:
    print(f"Error occurred while cloning the repository: {e}")
    sys.exit(1)

# Use the name of the repository as the directory
# The directory name is the same as the repository name (e.g., "wiz-test-helm")
CLONE_DIR = REPO_URL.split("/")[-1].replace(".git", "")

# Change working directory to the cloned repository
try:
    os.chdir(CLONE_DIR)
    print(f"Changed working directory to {CLONE_DIR}")
except FileNotFoundError:
    print(f"Failed to change directory to {CLONE_DIR}")
    sys.exit(1)

# Create a new branch
NEW_BRANCH = f"promote/{NEW_IMAGE.split(':')[-1]}"
subprocess.run(["git", "checkout", "-b", NEW_BRANCH], check=True)

# Define the correct path to values.yaml (update based on repo structure)
VALUES_FILE = "helm/values/values-kestra.yaml"  # Adjust this to match your repo

# Update the image tag in values.yaml
import yaml
with open(VALUES_FILE, "r") as f:
    values = yaml.safe_load(f)

values["image"]["tag"] = NEW_IMAGE.split(":")[-1]

with open(VALUES_FILE, "w") as f:
    yaml.dump(values, f)

# Commit and push changes
subprocess.run(["git", "config", "user.name", "AutoBot"], check=True)
subprocess.run(["git", "config", "user.email", "bot@example.com"], check=True)
subprocess.run(["git", "add", VALUES_FILE], check=True)
subprocess.run(["git", "commit", "-m", f"Update image to {NEW_IMAGE}"], check=True)
subprocess.run(["git", "push", "--set-upstream", "origin", NEW_BRANCH], check=True)

# Create pull request
from github import Github

g = Github(GITHUB_TOKEN)
repo = g.get_repo(GITHUB_REPO)
pr = repo.create_pull(title=f"Promote image {NEW_IMAGE}", body="This PR promotes {NEW_IMAGE} to the Helm chart for the Kestra Standalone Server", head=NEW_BRANCH, base=BASE_BRANCH)

print(f"✅ PR created: {pr.html_url}")
