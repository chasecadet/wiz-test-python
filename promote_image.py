import subprocess
import sys
import os
import yaml
from github import Github

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

# Create a new branch name based on the image tag
NEW_BRANCH = f"promote/{NEW_IMAGE.split(':')[-1]}"

# Check if the branch already exists
try:
    subprocess.run(["git", "checkout", "origin/main"], check=True)  # Ensure we're on main before checking for branch
    subprocess.run(["git", "fetch", "--all"], check=True)  # Fetch all remote branches

    # Check if the branch exists
    subprocess.run(["git", "rev-parse", "--verify", f"origin/{NEW_BRANCH}"], check=True)
    print(f"Branch {NEW_BRANCH} already exists. Switching to that branch.")
    subprocess.run(["git", "checkout", f"origin/{NEW_BRANCH}"], check=True)
except subprocess.CalledProcessError:
    print(f"Branch {NEW_BRANCH} does not exist. Creating new branch.")
    subprocess.run(["git", "checkout", "-b", NEW_BRANCH], check=True)

# Pull the latest changes from the remote branch to avoid the 'non-fast-forward' error
try:
    subprocess.run(["git", "pull", "origin", NEW_BRANCH], check=True)
    print(f"Successfully pulled the latest changes for {NEW_BRANCH}.")
except subprocess.CalledProcessError as e:
    print(f"Error occurred while pulling changes: {e}")
    print("Merge conflicts detected! Exiting...")
    sys.exit(1)  # Stop the script if there are conflicts

# Ensure you're on the correct branch before committing (ensure you're not in detached HEAD)
subprocess.run(["git", "checkout", NEW_BRANCH], check=True)
print(f"Switched to the branch {NEW_BRANCH}.")

# Define the correct path to values.yaml (update based on repo structure)
VALUES_FILE = "helm/values/values-kestra.yaml"  # Adjust this to match your repo

# Update the image tag in values.yaml
with open(VALUES_FILE, "r") as f:
    values = yaml.safe_load(f)

# Ensure that the 'image' key exists before modifying it
if "image" not in values:
    print(f"Error: 'image' key not found in {VALUES_FILE}.")
    sys.exit(1)

values["image"]["tag"] = NEW_IMAGE.split(":")[-1]

# Write the updated values back to the file
with open(VALUES_FILE, "w") as f:
    yaml.dump(values, f)

# Commit and push changes
subprocess.run(["git", "config", "user.name", "AutoBot"], check=True)
subprocess.run(["git", "config", "user.email", "bot@example.com"], check=True)
subprocess.run(["git", "add", VALUES_FILE], check=True)
subprocess.run(["git", "commit", "-m", f"Update image to {NEW_IMAGE}"], check=True)

# Push the changes
try:
    subprocess.run(["git", "push", "--set-upstream", "origin", NEW_BRANCH], check=True)
    print(f"Successfully pushed changes to {NEW_BRANCH}.")
except subprocess.CalledProcessError as e:
    print(f"Error occurred while pushing changes: {e}")
    sys.exit(1)

# Create pull request
g = Github(GITHUB_TOKEN)
repo = g.get_repo(GITHUB_REPO)
pr = repo.create_pull(title=f"Promote image {NEW_IMAGE}", body="This PR promotes a new image to the Helm chart for the Kestra Standalone Server", head=NEW_BRANCH, base=BASE_BRANCH)

print(f"✅ PR created: {pr.html_url}")
