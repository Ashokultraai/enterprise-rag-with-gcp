"""
Quick end-to-end retrieval test on the local (no-GCP) stack.

Flow: local embed query -> Qdrant vector search -> FlashRank rerank -> print.
Usage:
    python test_query.py "your question here"
    python test_query.py            # uses a default question
"""
import sys

# Force UTF-8 so any emoji log lines don't crash on Windows consoles.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from app.services.retrieval.qdrant_service import search_enterprise_knowledge
from app.services.retrieval.reranking_service import rerank_documents


def main():
    query = sys.argv[1] if len(sys.argv) > 1 else "How do C++ exceptions unwind the stack on Windows?"
    print(f"\n🔎 QUERY: {query}\n" + "=" * 70)

    # 1. Vector search (local embedding + Qdrant)
    hits = search_enterprise_knowledge(query, limit=8)
    print(f"\n[1] Vector search returned {len(hits)} hits:\n")
    for i, h in enumerate(hits, 1):
        print(f"  {i}. score={h['score']:.4f}  source={h['source']}")
        print(f"     {h['content'][:110].strip()!r}...")

    if not hits:
        print("\n⚠️  No hits — is the collection populated?")
        return

    # 2. Rerank with FlashRank cross-encoder (local)
    docs = [h["content"] for h in hits]
    reranked = rerank_documents(query, docs, top_n=3)

    print("\n" + "=" * 70)
    print(f"[2] Top {len(reranked)} after FlashRank rerank:\n")
    for i, doc in enumerate(reranked, 1):
        # find which source this reranked chunk came from
        src = next((h["source"] for h in hits if h["content"] == doc), "Unknown")
        print(f"  #{i}  source={src}")
        print(f"      {doc[:220].strip()}\n")


if __name__ == "__main__":
    main()
