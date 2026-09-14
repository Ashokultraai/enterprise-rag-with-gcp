"""Responder: final answer synthesis for all four outcomes."""
import logfire

from app.llm import get_llm
from app.agents.state import AgentState
from app.agents.nodes._util import llm_text

# Keep the responder request well under Groq's free-tier 8k tokens/minute limit.
MAX_DOC_CHARS = 900     # per-chunk cap in the context
MAX_HIST_CHARS = 600    # per-message cap in conversational history

_BLOCKED_MSG = (
    "I can't help with that request. I'm an enterprise technical assistant — "
    "feel free to ask me about the topics in the knowledge base."
)

_CONVO_SYSTEM = """You are a friendly enterprise technical assistant. Reply naturally and
concisely to greetings and small talk. Do not invent technical facts."""

_TECH_SYSTEM = """You are an enterprise technical assistant. Answer the user's question using
ONLY the provided context. Cite the source filenames you used inline like [source: <name>].
If the context is insufficient, say so plainly — do not invent facts."""


def _history(messages, limit: int = 6):
    return [{"role": m["role"], "content": m["content"][:MAX_HIST_CHARS]}
            for m in (messages or [])[-limit:]]


def responder_node(state: AgentState) -> dict:
    query = state.get("query", "")
    route = state.get("route")
    grade = state.get("grade")
    docs = state.get("documents", [])
    sources = state.get("sources", [])
    thoughts = list(state.get("thought_process", []))

    with logfire.span("✍️ Responder", route=route, grade=grade):
        # 1. Guardrail block → canned refusal, no LLM call.
        if route == "blocked":
            return _reply(_BLOCKED_MSG, [], thoughts)

        # 2. Technical query that found nothing usable → honest "not found".
        if route == "technical" and (grade == "irrelevant" or not docs):
            answer = (
                f"I couldn't find anything about that in the knowledge base, so I don't "
                f"have a grounded answer for: \"{query}\". It may not be covered by the "
                f"ingested documents."
            )
            thoughts.append("Response: Not in knowledge base")
            return _reply(answer, [], thoughts)

        llm = get_llm(temperature=0.2, fast=False)

        # 3. Conversational → chit-chat, no retrieval context.
        if route == "conversational":
            msgs = [{"role": "system", "content": _CONVO_SYSTEM}] + _history(state.get("messages", []))
            answer = llm_text(llm.invoke(msgs))
            thoughts.append("Response: Conversational")
            return _reply(answer, [], thoughts)

        # 4. Technical with relevant context → grounded, cited answer.
        context = "\n\n".join(
            f"[source: {d['source']}]\n{d['content'][:MAX_DOC_CHARS]}" for d in docs
        )
        msgs = [
            {"role": "system", "content": _TECH_SYSTEM},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
        ]
        answer = llm_text(llm.invoke(msgs))
        thoughts.append("Response: Grounded answer")
        logfire.info("✅ Response synthesised via LLM")
        return _reply(answer, sources, thoughts)


def _reply(answer: str, sources: list, thoughts: list) -> dict:
    """Standard responder return: also append the assistant turn to history."""
    return {
        "answer": answer,
        "sources": sources,
        "thought_process": thoughts,
        "messages": [{"role": "assistant", "content": answer}],
    }
