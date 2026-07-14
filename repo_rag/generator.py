import os
from google import genai
from google.genai import types

GEN_MODEL = "gemini-flash-lite-latest"

SYSTEM_PROMPT = """You are a code assistant answering questions about a specific set of repositories.
Answer ONLY using the provided context chunks below. Each chunk is labeled with its repo, file path, and line range.
When you reference something, cite it inline like (repo/path/to/file.py:12-30).
If the context doesn't contain enough information to answer, say so explicitly instead of guessing."""


def build_context(chunks):
    parts = []
    for c in chunks:
        m = c["meta"]
        label = f"{m['repo']}/{m['file_path']}:{m['start_line']}-{m['end_line']}"
        parts.append(f"--- {label} ---\n{c['code']}")
    return "\n\n".join(parts)


def ask(question, retriever, k=6):
    chunks = retriever.search(question, k=k)
    context = build_context(chunks)

    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    prompt = f"{SYSTEM_PROMPT}\n\nContext:\n{context}\n\nQuestion: {question}\n\nAnswer:"

    response = client.models.generate_content(
        model=GEN_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.2),
    )
    return response.text, chunks