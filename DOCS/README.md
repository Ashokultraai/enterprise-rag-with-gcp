# 📚 Documentation Index

These docs were written alongside the project's evolution. The system was later **migrated off GCP to a local-first, free-to-run stack** (local `sentence-transformers` embeddings, `pypdf` parsing, local file storage, Docker / Hugging Face Spaces deployment). As a result, each doc now carries a **status banner** at the top:

- ✅ **Current** — accurately describes the running system.
- 🚧 **Roadmap** — a designed-but-not-yet-implemented capability; the running system uses something simpler.
- ⚠️ **Superseded** — describes the original **GCP** design that no longer exists; kept for historical/design reference.

For the authoritative description of what actually runs today, see the **[root README](../README.md)**.

---

| # | Doc | Status | Notes |
|---|-----|--------|-------|
| 01 | [System Overview](01_SYSTEM_OVERVIEW.md) | ✅ Current | High-level vision + end-to-end flow |
| 02 | [Ingestion Engine](02_INGESTION_ENGINE.md) | ✅ Current | pypdf/office/html parsing → local embeddings → Qdrant |
| 03 | [Node Intelligence](03_NODE_INTELLIGENCE.md) | ✅ Current | The 5-node LangGraph agent (guardrail·planner·retriever·grader·responder) |
| 04 | [Tracing & Observability](04_TRACING_AND_OBSERVABILITY.md) | ✅ Current (partial) | Logfire spans; LangSmith configured |
| 05 | [GCP Prod Setup](05_GCP_PROD_SETUP.md) | ⚠️ Superseded | GCP infra provisioning |
| 06 | [Deployment Strategy](06_DEPLOYMENT_STRATEGY.md) | ⚠️ Superseded | Cloud Build/Run → now Docker / HF Spaces |
| 07 | [Environment Variables](07_ENVIRONMENT_VARIABLES.md) | ⚠️ Partial | Only Groq + Qdrant vars are still used |
| 08 | [GCP Roles & Services](08_GCP_ROLES_AND_SERVICES.md) | ⚠️ Superseded | IAM / service breakdown |
| 09 | [Infra Architecture](09_INFRA_ARCHITECTURE.md) | ⚠️ Superseded | 3-tier GCP blueprint |
| 10 | [Redis Caching](10_REDIS_CACHING.md) | 🚧 Roadmap | Now in-process `MemorySaver` |
| 11 | [Microservices Transition](11_MICROSERVICES_TRANSITION.md) | 🚧 Roadmap | Now Docker Compose / single container |
| 12 | [Known Gotchas](12_KNOWN_GOTCHAS.md) | ⚠️ Partial | Many gotchas were GCP-specific |
| 13 | [FlashRank Reranking](13_FLASHRANK_RERANKING.md) | ✅ Current | Local cross-encoder reranker |
| 14 | [VPC Networking](14_VPC_NETWORKING.md) | ⚠️ Superseded | GCP VPC connectors |
| 15 | [Guardrails](15_GUARDRAILS.md) | ✅ Partial | NeMo input gate live (self check input); LLM node is fallback. Fuller dialog/PII/output rails still planned |
| 16 | [LLM Gateway](16_LLM_GATEWAY.md) | 🚧 Roadmap | Portkey seam exists; calls go direct to Groq today |
| 17 | [Evals](17_EVALS.md) | 🚧 Roadmap | RAGAS metrics theory |
| 18 | [Evals Pipeline](18_EVALS_PIPELINE.md) | 🚧 Roadmap | Eval pipeline not wired up |
| 19 | [GCP Permissions & Services](19_GCP_PERMISSIONS_AND_SERVICES.md) | ⚠️ Superseded | GCP IAM reference |

---

### What actually runs today (quick reference)

| Concern | Implementation |
|---|---|
| Embeddings | `sentence-transformers/all-mpnet-base-v2` (local, 768-dim) |
| PDF / office parsing | `pypdf`, `python-docx`, `python-pptx`, BeautifulSoup |
| Vector DB | Qdrant Cloud (free tier) |
| Reranking | FlashRank (local ONNX cross-encoder) |
| LLM | Groq `gpt-oss-120b` (answers) + `gpt-oss-20b` (routing) |
| Agent | LangGraph 5-node graph + in-process `MemorySaver` |
| Serving | FastAPI + Streamlit |
| Packaging | Docker Compose / Hugging Face Space |
