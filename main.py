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

import time
from repo_rag.store import get_collection, add_chunks

collection = get_collection()

print(f"\nembedding and storing {len(all_chunks)} chunks...")
BATCH_SIZE = 25
for i in range(0, len(all_chunks), BATCH_SIZE):
    batch = all_chunks[i:i + BATCH_SIZE]
    embeddings = []
    valid_chunks = []
    for chunk in batch:
        try:
            vec = embed_text(chunk.code)
            embeddings.append(vec)
            valid_chunks.append(chunk)
        except Exception as e:
            print(f"skipping {chunk.repo}/{chunk.file_path}:{chunk.start_line} ({e})")
        time.sleep(0.3)
    if valid_chunks:
        add_chunks(collection, valid_chunks, embeddings)
    print(f"  indexed {min(i + BATCH_SIZE, len(all_chunks))}/{len(all_chunks)}")

print(f"\ndone. collection now has {collection.count()} chunks.")