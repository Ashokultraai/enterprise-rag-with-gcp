"""Shared state object that flows through every node of the agent graph."""
import operator
from typing import TypedDict, List, Dict, Literal, Annotated


class AgentState(TypedDict, total=False):
    # --- conversation ---
    # operator.add makes returned message lists APPEND to the persisted history
    # (per thread_id via MemorySaver) instead of overwriting it.
    messages: Annotated[List[Dict[str, str]], operator.add]
    query: str                       # the raw user message for this turn

    # --- planner output ---
    route: Literal["conversational", "technical", "blocked"]
    search_query: str                # optimized query used for retrieval

    # --- retriever output ---
    documents: List[Dict]            # [{content, source, score}, ...] after rerank
    sources: List[str]               # unique source filenames

    # --- grader output / self-correction ---
    grade: Literal["relevant", "irrelevant"]
    retries: int                     # how many times we've re-searched

    # --- responder output ---
    answer: str

    # --- observability (shown as the "plan" in the UI) ---
    thought_process: List[str]
