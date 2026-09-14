"""Small helpers shared by the LLM nodes."""
import json
import re


def parse_json(text: str) -> dict:
    """
    Best-effort extraction of a JSON object from an LLM response.
    Handles ```json fences and leading/trailing prose. Returns {} on failure.
    """
    if not text:
        return {}
    # strip code fences
    text = re.sub(r"```(?:json)?", "", text).strip()
    # grab the first {...} block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    candidate = match.group(0) if match else text
    try:
        return json.loads(candidate)
    except Exception:
        return {}


def llm_text(response) -> str:
    """Extract plain text from a LangChain chat response (.content) or a raw string."""
    return getattr(response, "content", response) or ""
