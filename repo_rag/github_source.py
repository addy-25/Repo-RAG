import os
from github import Github, Auth
from git import Repo

def get_client():
    token = os.getenv("GITHUB_TOKEN")
    auth = Auth.Token(token)
    return Github(auth=auth)

def list_repos(include_forks=False, include_archived=False):
    gh = get_client()
    user = gh.get_user()
    repos = []
    for repo in user.get_repos():
        if repo.fork and not include_forks:
            continue
        if repo.archived and not include_archived:
            continue
        repos.append(repo)
    return repos

def clone_repo(repo, dest_dir="repos"):
    os.makedirs(dest_dir, exist_ok=True)
    local_path = os.path.join(dest_dir, repo.name)
    token = os.getenv("GITHUB_TOKEN")
    clone_url = repo.clone_url.replace("https://", f"https://{token}@")

    if os.path.exists(local_path):
        Repo(local_path).remotes.origin.pull()
    else:
        Repo.clone_from(clone_url, local_path, depth=1)
    return local_path