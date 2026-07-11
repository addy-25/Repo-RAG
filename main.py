import os
from dotenv import load_dotenv
from repo_rag.github_source import list_repos, clone_repo

load_dotenv()

REPO_ALLOWLIST = {"Gravitas", "QuantHFT", "GrowEasy", "FeedFlow"}

repos = list_repos(allowed_names=REPO_ALLOWLIST)
print(f"found {len(repos)} repos")

for repo in repos:
    path = clone_repo(repo)
    print(f"cloned {repo.full_name} -> {path}")


from repo_rag.source_files import find_source_files

all_files = []
for repo in repos:
    repo_path = os.path.join("repos", repo.name)
    files = find_source_files(repo_path)
    print(f"{repo.name}: {len(files)} files")
    all_files.extend(files)

print(f"\ntotal: {len(all_files)} files across {len(repos)} repos")