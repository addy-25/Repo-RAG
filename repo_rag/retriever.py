import re
from rank_bm25 import BM25Okapi
from repo_rag.store import get_collection
from repo_rag.embedder import embed_text


def tokenize(text):
    # split on non-alphanumerics; keeps identifiers like getUserById whole
    return [t for t in re.split(r"\W+", text.lower()) if t]


class HybridRetriever:
    def __init__(self):
        self.collection = get_collection()
        # pull everything once to build the BM25 keyword index in memory
        data = self.collection.get(include=["documents", "metadatas"])
        self.ids = data["ids"]
        self.documents = data["documents"]
        self.metadatas = data["metadatas"]
        tokenized_corpus = [tokenize(doc) for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized_corpus)
        self.id_to_idx = {cid: i for i, cid in enumerate(self.ids)}

    def dense_search(self, query, k=10):
        qvec = embed_text(query, task_type="RETRIEVAL_QUERY")
        res = self.collection.query(query_embeddings=[qvec], n_results=k)
        return res["ids"][0]  # list of chunk ids, best first

    def sparse_search(self, query, k=10):
        scores = self.bm25.get_scores(tokenize(query))
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        return [self.ids[i] for i in ranked[:k]]

    def rrf_merge(self, dense_ids, sparse_ids, rrf_k=60):
        scores = {}
        for rank, cid in enumerate(dense_ids):
            scores[cid] = scores.get(cid, 0) + 1 / (rrf_k + rank)
        for rank, cid in enumerate(sparse_ids):
            scores[cid] = scores.get(cid, 0) + 1 / (rrf_k + rank)
        return sorted(scores, key=scores.get, reverse=True)

    def search(self, query, k=5):
        dense_ids = self.dense_search(query, k=10)
        sparse_ids = self.sparse_search(query, k=10)
        merged = self.rrf_merge(dense_ids, sparse_ids)[:k]
        results = []
        for cid in merged:
            idx = self.id_to_idx[cid]
            results.append({
                "id": cid,
                "code": self.documents[idx],
                "meta": self.metadatas[idx],
            })
        return results