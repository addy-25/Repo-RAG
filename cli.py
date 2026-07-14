import typer
from dotenv import load_dotenv

load_dotenv()

from repo_rag.retriever import HybridRetriever
from repo_rag.generator import ask

app = typer.Typer()
_retriever = None


def get_retriever():
    global _retriever
    if _retriever is None:
        print("loading index...")
        _retriever = HybridRetriever()
    return _retriever


@app.command()
def query(question: str, k: int = 6, show_sources: bool = True):
    retriever = get_retriever()
    answer, chunks = ask(question, retriever, k=k)
    print(f"\n{answer}\n")
    if show_sources:
        print("Sources:")
        for c in chunks:
            m = c["meta"]
            print(f"  {m['repo']}/{m['file_path']}:{m['start_line']}-{m['end_line']}")


if __name__ == "__main__":
    app()