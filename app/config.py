import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # --- GCP CONFIG ---
    PROJECT_ID = os.getenv("PROJECT_ID", "enterprise-rag-507805")
    LOCATION = os.getenv("LOCATION", "us-central1")
    GCP_DOC_AI_LOCATION = os.getenv("GCP_DOC_AI_LOCATION", "us")
    GCP_DOC_AI_PROCESSOR_ID = os.getenv("GCP_DOC_AI_PROCESSOR_ID")
    RAW_BUCKET = os.getenv("GCP_RAW_BUCKET", "enterprise-rag-ra")
    PROCESSED_BUCKET = os.getenv("GCP_PROCESSED_BUCKET", "enterprise_rag-process")

    # --- VECTOR DB (QDRANT) ---
    QDRANT_URL = os.getenv("QDRANT_CLUSTER_ENDPOINT")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    QDRANT_COLLECTION = "enterprise_rag"

    # --- REASONING ENGINE (GROQ) ---
    # NOTE: Groq retired the Llama 3.x models; these are current as of 2026-09.
    # Check https://console.groq.com/docs/models if a call 404s (model_not_found).
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")       # heavy: answer synthesis
    GROQ_FAST_MODEL = os.getenv("GROQ_FAST_MODEL", "openai/gpt-oss-20b")  # light: planner/guardrail/grader
    GROQ_FALLBACK_API_KEY = os.getenv("GROQ_FALLBACK_API_KEY")

    # --- LLM GATEWAY (PORTKEY) — optional seam, inactive unless PORTKEY_API_KEY is set ---
    PORTKEY_API_KEY = os.getenv("PORTKEY_API_KEY")
    GROQ_SLUG =  "rag"     # primary slug -> @rag/<GROQ_MODEL> (e.g. openai/gpt-oss-120b on Groq)
    GROQ_SLUG_2 = "brag"  # fallback slug -> @brag/<GROQ_FAST_MODEL> (e.g. openai/gpt-oss-20b on Groq)

    
    # --- OBSERVABILITY ---
    LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "true")
    LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
    LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "rag_scale_test")
    LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")

# Enable LangSmith tracing. Set BOTH the modern LANGSMITH_* and the legacy
# LANGCHAIN_* names so any SDK version picks it up (newer SDKs read LANGSMITH_*,
# older ones LANGCHAIN_*). Only turn tracing ON when an API key is actually
# present, to avoid noisy failures when it isn't configured.
#
# Accept the key under EITHER env name — some setups store the secret as
# LANGCHAIN_API_KEY. And NEVER overwrite a real key with an empty string
# (an earlier version of this block wiped LANGCHAIN_API_KEY when only
# LANGSMITH_API_KEY was checked, which silently disabled tracing).
_ls_key = os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY") or ""
_ls_on = "true" if _ls_key else "false"
_ls_project = os.getenv("LANGSMITH_PROJECT") or os.getenv("LANGCHAIN_PROJECT") or "enterprise-rag"
_ls_endpoint = os.getenv("LANGSMITH_ENDPOINT") or os.getenv("LANGCHAIN_ENDPOINT") or "https://api.smith.langchain.com"
for _prefix in ("LANGSMITH", "LANGCHAIN"):
    if _ls_key:  # don't clobber a present key with ""
        os.environ[f"{_prefix}_API_KEY"] = _ls_key
    os.environ[f"{_prefix}_PROJECT"] = _ls_project
    os.environ[f"{_prefix}_ENDPOINT"] = _ls_endpoint
os.environ["LANGSMITH_TRACING"] = _ls_on
os.environ["LANGCHAIN_TRACING_V2"] = _ls_on

settings = Settings()
