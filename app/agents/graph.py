"""
Assemble the agentic RAG graph.

    guardrail ─(blocked)────────────────────────► responder ─► END
        │(safe)
     planner ─(conversational)───────────────────► responder
        │(technical)
     retriever ─► grader ─(relevant)─────────────► responder
                    │(weak, budget left) ─► retriever   [self-correction loop]
                    │(weak, budget spent) ─────────────► responder
"""
# pyrefly: ignore [missing-import]
from langgraph.graph import StateGraph, START, END
# pyrefly: ignore [missing-import]
from langgraph.checkpoint.memory import MemorySaver

from app.agents.state import AgentState
from app.agents.nodes.guardrail import guardrail_node
from app.agents.nodes.planner import planner_node
from app.agents.nodes.retriever import retriever_node
from app.agents.nodes.grader import grader_node, MAX_RETRIES
from app.agents.nodes.responder import responder_node


def _after_guardrail(state: AgentState) -> str:
    return "responder" if state.get("route") == "blocked" else "planner"


def _after_planner(state: AgentState) -> str:
    return "retriever" if state.get("route") == "technical" else "responder"


def _after_grader(state: AgentState) -> str:
    if state.get("grade") == "relevant":
        return "responder"
    # irrelevant: retry while we still have budget, otherwise give up
    if state.get("retries", 0) <= MAX_RETRIES:
        return "retriever"
    return "responder"


def build_graph():
    g = StateGraph(AgentState)

    g.add_node("guardrail", guardrail_node)
    g.add_node("planner", planner_node)
    g.add_node("retriever", retriever_node)
    g.add_node("grader", grader_node)
    g.add_node("responder", responder_node)

    g.add_edge(START, "guardrail")
    g.add_conditional_edges("guardrail", _after_guardrail,
                            {"planner": "planner", "responder": "responder"})
    g.add_conditional_edges("planner", _after_planner,
                            {"retriever": "retriever", "responder": "responder"})
    g.add_edge("retriever", "grader")
    g.add_conditional_edges("grader", _after_grader,
                            {"retriever": "retriever", "responder": "responder"})
    g.add_edge("responder", END)

    # MemorySaver keeps conversation state per thread_id (in-process for v1).
    return g.compile(checkpointer=MemorySaver())


# Module-level compiled agent, imported by the API and the in-process UI.
agent = build_graph()


def run_turn(query: str, thread_id: str) -> dict:
    """
    Run one conversation turn. Resets per-turn state (only `messages` accumulates
    via the reducer, keyed by thread_id) and returns the final AgentState.
    Shared by the FastAPI endpoint and the in-process Streamlit UI.
    """
    state_in = {
        "query": query,
        "messages": [{"role": "user", "content": query}],
        "route": "pending",
        "grade": None,
        "retries": 0,
        "documents": [],
        "sources": [],
        "thought_process": [],
    }
    return agent.invoke(state_in, config={"configurable": {"thread_id": thread_id}})
