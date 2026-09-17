"""NeMo Guardrails input gate — the PRIMARY guardrail.

Wraps NeMo Guardrails' "self check input" rail (see app/agents/nemo_rails/) and
exposes a single boolean check used by guardrail_node. The rails engine is built
once (lazily) and reused. Our existing Groq LLM is injected as NeMo's main model,
so there's no separate model config and no extra provider wiring.

If anything here raises, guardrail_node falls back to the lightweight LLM gate.
"""
import os

# pyrefly: ignore [missing-import]
from nemoguardrails import RailsConfig, LLMRails
# pyrefly: ignore [missing-import]
from nemoguardrails.rails.llm.options import GenerationOptions

from app.llm import get_llm

# Colang/prompt config lives one directory up from nodes/, in nemo_rails/.
_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "nemo_rails")

_rails = None


def _get_rails() -> LLMRails:
    """Build the NeMo rails engine once, injecting our Groq (fast) model."""
    global _rails
    if _rails is None:
        config = RailsConfig.from_path(_CONFIG_PATH)
        # Reuse the same cheap classifier model the LLM guardrail used.
        llm = get_llm(temperature=0.0, fast=True)
        _rails = LLMRails(config, llm=llm)
    return _rails


def nemo_check_input(query: str) -> tuple[bool, str]:
    """
    Run the NeMo input rails on `query`.

    Returns (allow, reason):
      allow = False when an input rail stops the message (a BLOCK decision).
    Raises on any NeMo error so the caller can fall back to the LLM gate.
    """
    rails = _get_rails()
    options = GenerationOptions(
        rails=["input"],                     # input rails only — our agent does the answering
        log={"activated_rails": True},       # we read the block decision from the rail log
    )
    res = rails.generate(
        messages=[{"role": "user", "content": query}],
        options=options,
    )

    log = getattr(res, "log", None)
    activated = getattr(log, "activated_rails", None) or []
    stopped = [ar for ar in activated if getattr(ar, "stop", False)]

    if stopped:
        names = ", ".join(getattr(ar, "name", "input rail") for ar in stopped)
        return False, f"nemo: blocked by [{names}]"
    return True, "nemo: allowed"
