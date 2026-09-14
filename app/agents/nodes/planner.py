"""Planner / router: decide whether the query needs a knowledge-base search."""
import logfire

from app.llm import get_llm
from app.agents.state import AgentState
from app.agents.nodes._util import parse_json, llm_text

_SYSTEM = """You are the planner for an enterprise technical RAG assistant.
Classify the user's message given the conversation so far.

- "CONVERSATIONAL": greetings, small talk, thanks, or a question that can be answered
  purely from the conversation history — NO document search needed.
- "TECHNICAL": a question that likely needs the technical knowledge base (topics like
  operating systems, networking, C++, compilers, algorithms, Kubernetes, hardware, etc.).

If TECHNICAL, also write an optimized, self-contained search query (resolve pronouns using
the history, strip chit-chat, keep key technical terms).

Respond with ONLY JSON:
{"intent": "CONVERSATIONAL"|"TECHNICAL", "search_query": "<optimized query or empty>"}"""


def _history_text(messages, limit: int = 6) -> str:
    recent = messages[-limit:] if messages else []
    return "\n".join(f"{m.get('role')}: {m.get('content')}" for m in recent)


def planner_node(state: AgentState) -> dict:
    query = state.get("query", "")
    thoughts = list(state.get("thought_process", []))

    with logfire.span("🧭 Planner", query=query):
        user_block = f"Conversation so far:\n{_history_text(state.get('messages', []))}\n\nNew message: {query}"
        try:
            llm = get_llm(temperature=0.0, fast=True)
            resp = llm.invoke(
                [{"role": "system", "content": _SYSTEM},
                 {"role": "user", "content": user_block}]
            )
            data = parse_json(llm_text(resp))
            intent = str(data.get("intent", "TECHNICAL")).upper()
            search_query = data.get("search_query") or query
        except Exception as e:
            logfire.error(f"Planner error, defaulting to TECHNICAL: {e}")
            intent, search_query = "TECHNICAL", query

        if intent == "CONVERSATIONAL":
            thoughts.append("Intent: Conversational/Memory")
            logfire.info("💬 Conversational — skipping retrieval")
            return {"route": "conversational", "thought_process": thoughts}

        thoughts.append(f"Intent: Technical | Search: {search_query}")
        logfire.info(f"🔧 Technical — search query: {search_query}")
        return {
            "route": "technical",
            "search_query": search_query,
            "thought_process": thoughts,
        }
