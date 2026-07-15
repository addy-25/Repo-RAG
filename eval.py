from dotenv import load_dotenv
load_dotenv()
from repo_rag.retriever import HybridRetriever

# repo/file_path must match exactly what's stored in chunk metadata
EVAL_SET = [
    # GrowEasy
    {"question": "how are lead fields mapped from a CSV into the CRM schema?",
     "expected_file": "GrowEasy/backend/src/services/prompt.ts"},
    {"question": "what happens when a CSV row has multiple phone numbers or emails?",
     "expected_file": "GrowEasy/backend/src/services/sanitize.ts"},
    {"question": "how is an uploaded CSV file parsed?",
     "expected_file": "GrowEasy/backend/src/services/csv.ts"},
    {"question": "how does the batch extraction process work?",
     "expected_file": "GrowEasy/backend/src/services/extractor.ts"},

    # FeedFlow
    {"question": "how does Instagram feed ranking work?",
     "expected_file": "FeedFlow/backend/app/worker.py"},
    {"question": "how does user authentication work in FeedFlow?",
     "expected_file": "FeedFlow/backend/app/auth.py"},
    {"question": "how does the app send emails?",
     "expected_file": "FeedFlow/backend/app/email_service.py"},
    {"question": "how does the Instagram integration fetch posts?",
     "expected_file": "FeedFlow/backend/app/routers/instagram.py"},
    {"question": "how are user content preferences managed?",
     "expected_file": "FeedFlow/backend/app/routers/preferences.py"},

    # QuantHFT
    {"question": "how does the order matching engine handle partial fills?",
     "expected_file": "QuantHFT/services/matching-engine/internal/engine/orderbook.go"},
    {"question": "how does the system connect to Alpaca for paper trading?",
     "expected_file": "QuantHFT/services/order-service/app/core/alpaca.py"},
    {"question": "how is market data fetched from an external feed?",
     "expected_file": "QuantHFT/services/market-data-service/app/feed/yahoo_feed.py"},
    {"question": "how are trade notifications consumed and processed?",
     "expected_file": "QuantHFT/services/notification-service/app/consumer.py"},
    {"question": "how is risk checked before an order is placed?",
     "expected_file": "QuantHFT/services/order-service/app/services/risk.py"},

    # Gravitas
    # task creation is exposed via multiple paths (route, MCP tool, agent) - any counts
    {"question": "how are tasks created in Gravitas?",
     "expected_files": ["Gravitas/backend/main.py", "Gravitas/backend/mcp_server.py", "Gravitas/backend/agent.py"]},
    {"question": "how does authentication work in Gravitas?",
     "expected_files": ["Gravitas/backend/auth.py"]},
    {"question": "how does the AI agent process requests?",
     "expected_files": ["Gravitas/backend/agent.py", "Gravitas/backend/main.py"]},
    {"question": "what does the MCP server expose?",
     "expected_files": ["Gravitas/backend/mcp_server.py"]},
]


def retrieval_at_k(retriever, eval_set, k=5):
    hits = 0
    for item in eval_set:
        expected = item.get("expected_files") or [item["expected_file"]]
        results = retriever.search(item["question"], k=k)
        found = any(
            f"{r['meta']['repo']}/{r['meta']['file_path']}" in expected
            for r in results
        )
        print(f"[{'HIT' if found else 'MISS'}] {item['question']}")
        hits += found

    pct = hits / len(eval_set)
    print(f"\nretrieval@{k}: {hits}/{len(eval_set)} ({pct:.0%})")


if __name__ == "__main__":
    r = HybridRetriever()
    retrieval_at_k(r, EVAL_SET, k=5)
