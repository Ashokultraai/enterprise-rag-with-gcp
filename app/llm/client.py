"""
Single place every LangGraph node gets its LLM from.

Today: direct Groq via ChatGroq (works with the existing GROQ_API_KEY).
Later: if PORTKEY_API_KEY is set, the same factory returns a Portkey-backed
ChatOpenAI client (gateway: retries, fallback, cache) — no node code changes.
See DOCS/16_LLM_GATEWAY.md.
"""
# pyrefly: ignore [missing-import]
from langchain_groq import ChatGroq

from app.config import settings


def get_llm(temperature: float = 0.1, fast: bool = False):
    """
    Return a chat LLM.

    fast=False -> heavy model (settings.GROQ_MODEL, e.g. openai/gpt-oss-120b on
                  Groq) for final answer synthesis.
    fast=True  -> light model (settings.GROQ_FAST_MODEL, e.g. openai/gpt-oss-20b
                  on Groq) for planner / guardrail / grader, which only need
                  cheap classification / short JSON.
    """
    model = settings.GROQ_FAST_MODEL if fast else settings.GROQ_MODEL

    # --- Portkey gateway seam (activates automatically once the key exists) ---
    if settings.PORTKEY_API_KEY:
        # pyrefly: ignore [missing-import]
        from langchain_openai import ChatOpenAI
        # pyrefly: ignore [missing-import]
        from portkey_ai import createHeaders, PORTKEY_GATEWAY_URL

        slug = settings.GROQ_SLUG  # "rag" -> @rag/<model>
        return ChatOpenAI(
            api_key=settings.PORTKEY_API_KEY,
            base_url=PORTKEY_GATEWAY_URL,
            model=f"@{slug}/{model}",
            temperature=temperature,
            default_headers=createHeaders(
                api_key=settings.PORTKEY_API_KEY,
                metadata={"feature": "enterprise-rag", "_user": "system"},
            ),
        )

    # --- Default: direct Groq ---
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=model,
        temperature=temperature,
    )
