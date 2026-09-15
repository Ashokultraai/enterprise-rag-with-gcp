# 🔑 Environment Variables & Configuration

> ⚠️ **Partially superseded.** The GCP variables below are no longer used. The running system needs only `GROQ_API_KEY`, `QDRANT_API_KEY`, `QDRANT_CLUSTER_ENDPOINT` (plus optional `GROQ_MODEL`, `GROQ_FAST_MODEL`, `LOGFIRE_TOKEN`). Last updated 2026-09-14.

The project uses a `.env` file for local development and **GCP Secrets/Env Vars** for production. All configuration is managed via **Pydantic Settings** for strict type safety.

---

## 🏛️ Core Settings
| Variable | Description | Example |
| :--- | :--- | :--- |
| `PROJECT_ID` | Your GCP Project ID | `dmtxpress` |
| `LOCATION` | Primary GCP Region | `us-central1` |

## 🧠 AI & LLM (The Brain)
| Variable | Description | Example |
| :--- | :--- | :--- |
| `GROQ_API_KEY` | Groq API key — powers the reasoning engine (NOT an OpenAI key) | `gsk_...` |
| `GROQ_MODEL` | Heavy model for answer synthesis (Groq) | `openai/gpt-oss-120b` |
| `GROQ_FAST_MODEL` | Light model for planner / guardrail / grader (Groq) | `openai/gpt-oss-20b` |

> **The reasoning engine is Groq — no OpenAI key is needed.** The `openai/` in the model IDs is just Groq's naming for OpenAI's *open-weight* `gpt-oss` models, which run **on Groq's servers** via `GROQ_API_KEY`. (Groq retired the older `llama-3.3-70b-versatile` / `llama-3.1-8b-instant` models; `gpt-oss-120b` / `gpt-oss-20b` replaced them.)

## 📥 Ingestion & Storage
| Variable | Description | Example |
| :--- | :--- | :--- |
| `RAW_BUCKET` | Destination for raw PDFs | `dmtxpress-rag-raw` |
| `PROCESSED_BUCKET` | Destination for JSON metadata | `dmtxpress-rag-processed` |

## 🗄️ Persistence (The Memory)
| Variable | Description | Example |
| :--- | :--- | :--- |
| `QDRANT_URL` | Cloud Qdrant Endpoint | `https://...` |
| `QDRANT_API_KEY` | Qdrant Access Token | `xyz...` |
| `DATABASE_URL` | Cloud SQL Postgres URI | `postgresql+pg8000://...` |

## 🕵️ Observability (The Vision)
| Variable | Description | Example |
| :--- | :--- | :--- |
| `LOGFIRE_TOKEN` | Token for system tracing | `logfire_...` |
| `LANGSMITH_API_KEY` | Token for agent logic tracing | `lsv2_...` |

---

## 🔒 Security Best Practices
1.  **Never** commit your `.env` file to Git.
2.  In **Cloud Run**, use the "Variables & Secrets" tab to inject these values at runtime.
3.  Use the `commands_example.md` as a template when setting up a new developer environment.
