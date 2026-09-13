# pyrefly: ignore [missing-import]
from sentence_transformers import SentenceTransformer

# Local, free embedding model. 768-dim output to match the Qdrant collection
# (VectorParams(size=768)). Runs fully offline after the first download.
EMBEDDING_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
BATCH_SIZE = 50

model = None


def get_embedding_model():
    global model
    if model is None:
        # First call downloads the weights (~420MB) to the HuggingFace cache,
        # then loads from disk on every subsequent run.
        model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return model


def embed_query(query: str):
    """Embeds a single query string locally. Returns a plain list of floats."""
    model = get_embedding_model()
    vector = model.encode(query, normalize_embeddings=True)
    return vector.tolist()


def embed_texts(texts: list[str]):
    """Embeds a list of text strings in batches. Returns a list of float lists."""
    model = get_embedding_model()
    vectors = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return [v.tolist() for v in vectors]
