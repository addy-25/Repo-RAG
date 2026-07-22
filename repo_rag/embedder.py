import os
import time
from google import genai
from google.genai import types

_client = None

def get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    return _client

def embed_text(text, task_type="RETRIEVAL_DOCUMENT", retries=3):
    client = get_client()
    for attempt in range(retries):
        try:
            result = client.models.embed_content(
                model="gemini-embedding-001",
                contents=text,
                config=types.EmbedContentConfig(task_type=task_type),
            )
            return result.embeddings[0].values # type: ignore
        except Exception as e:
            wait = 5 * (attempt + 1)
            print(f"embed failed ({e}), retrying in {wait}s...")
            time.sleep(wait)
    raise RuntimeError(f"failed to embed after {retries} attempts")