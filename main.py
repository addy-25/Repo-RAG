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

from git import Repo as GitRepo
from repo_rag.chunker import chunk_file
from repo_rag.embedder import embed_text

all_chunks = []
for repo in repos:
    repo_path = os.path.join("repos", repo.name)
    commit_sha = GitRepo(repo_path).head.commit.hexsha
    files = find_source_files(repo_path)

    repo_chunks = []
    for fp in files:
        repo_chunks.extend(chunk_file(fp, repo.name, repo_path, commit_sha))

    print(f"{repo.name}: {len(files)} files -> {len(repo_chunks)} chunks")
    all_chunks.extend(repo_chunks)

print(f"\ntotal chunks: {len(all_chunks)}")

sample = all_chunks[0]
print(f"\nsample: {sample.repo}/{sample.file_path}:{sample.start_line}-{sample.end_line} [{sample.chunk_type}] {sample.name}")
print(sample.code[:300])

print("\nembedding a small sample to verify...")
for chunk in all_chunks[:3]:
    vec = embed_text(chunk.code)
    print(f"{chunk.repo}/{chunk.file_path} [{chunk.name}] -> {len(vec)} dims")