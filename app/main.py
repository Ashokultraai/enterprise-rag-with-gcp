"""FastAPI backend exposing the agentic RAG graph."""
import sys
import uuid

# Force UTF-8 so emoji log lines don't crash on Windows / redirected stdout.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import logfire
# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from pydantic import BaseModel

from app.agents.graph import run_turn

logfire.configure(service_name="enterprise-rag-api")

app = FastAPI(title="Enterprise RAG API", version="1.0.0")
logfire.instrument_fastapi(app)


class QueryRequest(BaseModel):
    query: str
    thread_id: str | None = None


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
    thought_process: list[str]
    thread_id: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    thread_id = req.thread_id or str(uuid.uuid4())

    with logfire.span("POST /query", thread_id=thread_id, query=req.query):
        result = run_turn(req.query, thread_id)

    return QueryResponse(
        answer=result.get("answer", ""),
        sources=result.get("sources", []),
        thought_process=result.get("thought_process", []),
        thread_id=thread_id,
    )
