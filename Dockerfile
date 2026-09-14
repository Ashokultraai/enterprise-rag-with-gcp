# --- Hugging Face Space: single Streamlit container running the agent in-process ---
# HF Docker Spaces serve the app on port 7860.
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Non-root user (HF Spaces best practice)
RUN useradd -m -u 1000 user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1 \
    USE_LOCAL_GRAPH=1 \
    LOGFIRE_IGNORE_NO_CONFIG=1 \
    HF_HOME=/home/user/.cache/huggingface

WORKDIR /app
COPY requirements-app.txt .
RUN pip install --no-cache-dir -r requirements-app.txt

COPY --chown=user app ./app
COPY --chown=user ui ./ui

USER user

# Bake the embedding model into the image (first query then needs no download).
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-mpnet-base-v2')"

EXPOSE 7860
CMD ["streamlit", "run", "ui/app.py", \
     "--server.port=7860", "--server.address=0.0.0.0", "--server.headless=true"]
