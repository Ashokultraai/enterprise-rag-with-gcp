"""Grader: judge whether retrieved context actually answers the query.

Drives the self-correction loop — on weak context it rewrites the search query and
signals a retry; once the retry budget is spent it gives up so the responder can
honestly say the answer isn't in the knowledge base (instead of hallucinating).
"""
import logfire

from app.llm import get_llm
from app.agents.state import AgentState
from app.agents.nodes._util import parse_json, llm_text

MAX_RETRIES = 1          # one rewrite+retry before giving up
MIN_SCORE = 0.35         # best cosine below this ⇒ almost certainly off-topic
HIGH_SCORE = 0.55        # best cosine at/above this ⇒ trust retrieval, skip the LLM grader

_SYSTEM = """You grade whether a set of retrieved document snippets contains enough
information to answer the user's question.

Return ONLY JSON:
{"relevant": true|false, "rewrite": "<an improved search query if not relevant, else empty>"}"""


def grader_node(state: AgentState) -> dict:
    query = state.get("query", "")
    docs = state.get("documents", [])
    retries = state.get("retries", 0)
    thoughts = list(state.get("thought_process", []))

    with logfire.span("⚖️ Grader", query=query, retries=retries):
        best_score = max((d.get("score", 0.0) for d in docs), default=0.0)

        # No docs, or vector scores far too low → don't even ask the LLM.
        if not docs or best_score < MIN_SCORE:
            relevant, rewrite = False, ""
        # Strong retrieval signal → trust it; the fast LLM grader is unreliable here.
        elif best_score >= HIGH_SCORE:
            relevant, rewrite = True, ""
        else:
            snippets = "\n---\n".join(d["content"][:400] for d in docs[:3])
            try:
                llm = get_llm(temperature=0.0, fast=True)
                resp = llm.invoke(
                    [{"role": "system", "content": _SYSTEM},
                     {"role": "user", "content": f"Question: {query}\n\nSnippets:\n{snippets}"}]
                )
                data = parse_json(llm_text(resp))
                relevant = bool(data.get("relevant", True))
                rewrite = data.get("rewrite", "")
            except Exception as e:
                logfire.error(f"Grader error, treating as relevant: {e}")
                relevant, rewrite = True, ""

        if relevant:
            thoughts.append(f"Grade: Relevant (score={best_score:.2f})")
            logfire.info(f"✅ Context relevant (best={best_score:.2f})")
            return {"grade": "relevant", "thought_process": thoughts}

        # Not relevant → decide retry vs give up (routing reads retries).
        new_retries = retries + 1
        if new_retries <= MAX_RETRIES:
            new_query = rewrite or f"{query} definition overview"
            thoughts.append(f"Grade: Weak — rewriting & retrying (best={best_score:.2f})")
            logfire.warn(f"🔁 Weak context — retry {new_retries} with: {new_query}")
            return {"grade": "irrelevant", "retries": new_retries,
                    "search_query": new_query, "thought_process": thoughts}

        thoughts.append("Grade: Not in knowledge base")
        logfire.warn("🛑 Giving up — answer not in knowledge base")
        return {"grade": "irrelevant", "retries": new_retries, "thought_process": thoughts}
