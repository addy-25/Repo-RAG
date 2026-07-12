import chromadb

DB_DIR = "chroma_db"
COLLECTION_NAME = "repo_chunks"

def get_collection():
    client = chromadb.PersistentClient(path=DB_DIR)
    return client.get_or_create_collection(name=COLLECTION_NAME)

def chunk_id(chunk):
    return f"{chunk.repo}/{chunk.file_path}:{chunk.start_line}-{chunk.end_line}"

def add_chunks(collection, chunks, embeddings):
    collection.add(
        ids=[chunk_id(c) for c in chunks],
        embeddings=embeddings,
        documents=[c.code for c in chunks],
        metadatas=[{
            "repo": c.repo,
            "file_path": c.file_path,
            "language": c.language,
            "chunk_type": c.chunk_type,
            "name": c.name,
            "start_line": c.start_line,
            "end_line": c.end_line,
            "commit_sha": c.commit_sha,
        } for c in chunks],
    )