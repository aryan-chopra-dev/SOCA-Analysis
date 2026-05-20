from pathlib import Path

import numpy as np


class EmbeddingModel:
    """SentenceTransformers wrapper with a deterministic fallback for offline demos."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        self.model = None
        try:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(model_name)
        except Exception:
            self.model = None

    def encode(self, texts: list[str]) -> np.ndarray:
        if self.model:
            return np.asarray(self.model.encode(texts, normalize_embeddings=True), dtype="float32")
        vectors = []
        for text in texts:
            bucket = np.zeros(384, dtype="float32")
            for token in text.lower().split():
                bucket[hash(token) % 384] += 1.0
            norm = np.linalg.norm(bucket) or 1.0
            vectors.append(bucket / norm)
        return np.vstack(vectors).astype("float32")


def load_knowledge_chunks(kb_dir: str | Path) -> list[dict]:
    chunks: list[dict] = []
    for path in sorted(Path(kb_dir).glob("*.txt")):
        raw = path.read_text(encoding="utf-8")
        for idx, block in enumerate([part.strip() for part in raw.split("\n\n") if part.strip()]):
            chunks.append({"id": f"{path.stem}-{idx}", "text": block, "source": path.name})
    return chunks
