import os
from dotenv import load_dotenv
from repo_rag.github_source import list_repos, clone_repo

load_dotenv()

repos = list_repos()
print(f"found {len(repos)} repos")

for repo in repos:
    path = clone_repo(repo)
    print(f"cloned {repo.full_name} -> {path}")