from pathlib import Path

import numpy as np

from rag.embed import EmbeddingModel, load_knowledge_chunks


class RAGRetriever:
    """Local FAISS retriever over a compact JEE mentoring knowledge base."""

    def __init__(self, kb_dir: str | Path = "rag/knowledge_base") -> None:
        self.chunks = load_knowledge_chunks(kb_dir)
        self.embedding_model = EmbeddingModel()
        self.embeddings = self.embedding_model.encode([chunk["text"] for chunk in self.chunks])
        self.index = None
        try:
            import faiss

            self.index = faiss.IndexFlatIP(self.embeddings.shape[1])
            self.index.add(self.embeddings)
        except Exception:
            self.index = None

    def retrieve(self, profile: dict, top_k: int = 5) -> list[dict]:
        query = " ".join([
            "weak topics",
            " ".join(profile["weak_topics"]),
            "topic assessment",
            " ".join(profile.get("topic_assessment_summary", {}).get("weak_topics", [])),
            "revision priority",
            " ".join(profile.get("topic_assessment_summary", {}).get("revision_priority", [])),
            "patterns",
            " ".join(profile["behavioral_patterns"]),
            "stress",
            profile["stress_level"],
            profile["short_answer_blocker"],
        ])
        query_vec = self.embedding_model.encode([query])
        if self.index:
            scores, ids = self.index.search(query_vec, top_k)
            pairs = [(int(idx), float(score)) for idx, score in zip(ids[0], scores[0]) if idx >= 0]
        else:
            scores = np.dot(self.embeddings, query_vec[0])
            pairs = [(int(idx), float(scores[idx])) for idx in np.argsort(scores)[::-1][:top_k]]
        return [{**self.chunks[idx], "score": round(score, 4)} for idx, score in pairs]
