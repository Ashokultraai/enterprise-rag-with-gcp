"""Streamlit chat frontend for the Enterprise RAG agent."""
import os
import uuid

import requests
import streamlit as st

# On Streamlit Community Cloud, config comes from st.secrets. Copy those into the
# environment so app.config (which reads os.getenv) and the agent pick them up.
try:
    for _k, _v in st.secrets.items():
        os.environ.setdefault(_k, str(_v))
except Exception:
    pass

API_URL = os.getenv("API_URL", "http://localhost:8000")
# Run the agent INSIDE Streamlit by default (no separate API server needed) — this
# is what makes a single-container / Streamlit Cloud deploy work. Set USE_LOCAL_GRAPH=0
# only when you deliberately want the UI to call a separate FastAPI backend.
USE_LOCAL_GRAPH = os.getenv("USE_LOCAL_GRAPH", "1").lower() in ("1", "true", "yes")


@st.cache_resource(show_spinner="Warming up the model (first load only)…")
def _get_runner():
    """Import + build the agent once, shared across reruns and sessions."""
    from app.agents.graph import run_turn
    return run_turn


def get_answer(query: str, thread_id: str):
    """Return (answer, sources, plan) either in-process or via the HTTP API."""
    if USE_LOCAL_GRAPH:
        run_turn = _get_runner()
        result = run_turn(query, thread_id)
        return (result.get("answer", ""),
                result.get("sources", []),
                result.get("thought_process", []))
    resp = requests.post(
        f"{API_URL}/query",
        json={"query": query, "thread_id": thread_id},
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("answer", ""), data.get("sources", []), data.get("thought_process", [])

st.set_page_config(page_title="Enterprise RAG", page_icon="🧠", layout="centered")
st.title("🧠 Enterprise RAG Assistant")
st.caption("Ask a technical question, or just say hi. Powered by LangGraph + Qdrant + Groq.")

# --- session state ---
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.subheader("Session")
    st.code(st.session_state.thread_id, language=None)
    if st.button("🔄 New conversation", key="new_conversation"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
    st.caption("Mode: in-process agent" if USE_LOCAL_GRAPH else f"API: {API_URL}")

# --- replay history ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m.get("sources"):
            with st.expander("📚 Sources"):
                for s in m["sources"]:
                    st.markdown(f"- {s}")
        if m.get("plan"):
            with st.expander("🧭 Agent plan"):
                for step in m["plan"]:
                    st.markdown(f"- {step}")

# --- new turn: compute, store, then rerun so the history loop renders it once ---
if prompt := st.chat_input("Ask something..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.spinner("Thinking..."):
        try:
            answer, sources, plan = get_answer(prompt, st.session_state.thread_id)
        except Exception as e:
            answer, sources, plan = f"⚠️ Error: {e}", [], []
    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": sources, "plan": plan}
    )
    st.rerun()
