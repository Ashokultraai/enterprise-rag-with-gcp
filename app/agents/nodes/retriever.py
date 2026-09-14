"""Retriever node: Qdrant vector search (top-15) + FlashRank rerank (top-5)."""
import logfire

from app.agents.state import AgentState
from app.services.retrieval.qdrant_service import search_enterprise_knowledge
from app.services.retrieval.reranking_service import rerank_documents


def retriever_node(state: AgentState) -> dict:
    search_query = state.get("search_query") or state.get("query", "")
    thoughts = list(state.get("thought_process", []))

    with logfire.span("🔍 Retriever", query=search_query):
        # Stage 1 — fast bi-encoder search in Qdrant (top 15 candidates)
        hits = search_enterprise_knowledge(search_query, limit=15)

        if not hits:
            thoughts.append("Context Retrieved: 0 documents")
            return {"documents": [], "sources": [], "thought_process": thoughts}

        # Stage 2 — cross-encoder rerank locally, keep the strongest 5
        texts = [h["content"] for h in hits]
        top_texts = rerank_documents(state.get("query", ""), texts, top_n=5)

        # map reranked text back to its full hit (preserve source + score)
        by_text = {h["content"]: h for h in hits}
        documents = [by_text[t] for t in top_texts if t in by_text]
        sources = list(dict.fromkeys(d["source"] for d in documents))  # unique, ordered

        thoughts.append(f"Context Retrieved: {len(documents)} documents")
        logfire.info(f"📚 Retrieved {len(documents)} reranked docs from {len(sources)} sources")
        return {"documents": documents, "sources": sources, "thought_process": thoughts}
