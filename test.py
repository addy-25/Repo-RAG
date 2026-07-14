from dotenv import load_dotenv
load_dotenv()

from repo_rag.retriever import HybridRetriever
from repo_rag.generator import ask

r = HybridRetriever()

question = "How does the CSV importer map lead fields into the CRM schema?"
answer, chunks = ask(question, r)

print("ANSWER:\n")
print(answer)
print("\nSOURCES USED:")
for c in chunks:
    m = c["meta"]
    print(f"  {m['repo']}/{m['file_path']}:{m['start_line']}-{m['end_line']}")