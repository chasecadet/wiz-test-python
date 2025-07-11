import os
import subprocess
import yaml
import sys
from github import Github

# Get inputs from env or fallback to defaults
REPO_URL = os.environ.get("REPO_URL", sys.argv[1])
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", sys.argv[2])
NEW_IMAGE = os.environ.get("NEW_IMAGE", sys.argv[3])
GITHUB_REPO = os.environ.get("GITHUB_REPO", sys.argv[4])
VALUES_FILE = os.environ.get("VALUES_FILE", "charts/mychart/values.yaml")
BASE_BRANCH = os.environ.get("BASE_BRANCH", "main")

CLONE_DIR = "/tmp/repo"
NEW_BRANCH = f"promote/{NEW_IMAGE.split(':')[-1]}"
PR_TITLE = f"Promote image {NEW_IMAGE}"
PR_BODY = "This PR promotes a new image to the Helm chart."

# Clone the repo
subprocess.run(["rm", "-rf", CLONE_DIR])
subprocess.run(["git", "clone", REPO_URL, CLONE_DIR], check=True)
os.chdir(CLONE_DIR)

# Create a new branch
subprocess.run(["git", "checkout", "-b", NEW_BRANCH], check=True)

# Update the image tag
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
g = Github(GITHUB_TOKEN)
repo = g.get_repo(GITHUB_REPO)
pr = repo.create_pull(title=PR_TITLE, body=PR_BODY, head=NEW_BRANCH, base=BASE_BRANCH)

print(f"✅ PR created: {pr.html_url}")
