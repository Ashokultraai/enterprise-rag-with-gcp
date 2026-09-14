"""Streamlit chat frontend for the Enterprise RAG agent."""
import os
import uuid

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")
# In-process mode: run the LangGraph agent inside Streamlit (no separate API).
# Used on Hugging Face Spaces (set USE_LOCAL_GRAPH=1) so a single container serves everything.
USE_LOCAL_GRAPH = os.getenv("USE_LOCAL_GRAPH", "").lower() in ("1", "true", "yes")


def get_answer(query: str, thread_id: str):
    """Return (answer, sources, plan) either in-process or via the HTTP API."""
    if USE_LOCAL_GRAPH:
        from app.agents.graph import run_turn
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
    if st.button("🔄 New conversation"):
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

# --- new turn ---
if prompt := st.chat_input("Ask something..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                answer, sources, plan = get_answer(prompt, st.session_state.thread_id)
            except Exception as e:
                answer, sources, plan = f"⚠️ Error: {e}", [], []

        st.markdown(answer)
        if sources:
            with st.expander("📚 Sources"):
                for s in sources:
                    st.markdown(f"- {s}")
        if plan:
            with st.expander("🧭 Agent plan"):
                for step in plan:
                    st.markdown(f"- {step}")

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": sources, "plan": plan}
    )
