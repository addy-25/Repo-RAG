from dotenv import load_dotenv
load_dotenv()

from repo_rag.retriever import HybridRetriever

r = HybridRetriever()
print("retriever ready\n")

for q in [
    "how are CRM lead fields mapped from a CSV?",
    "order matching engine",
    "how does Instagram feed ranking work?",
]:
    print(f"Q: {q}")
    for hit in r.search(q, k=3):
        m = hit["meta"]
        print(f"  {m['repo']}/{m['file_path']}:{m['start_line']}-{m['end_line']} [{m['name']}]")
    print()