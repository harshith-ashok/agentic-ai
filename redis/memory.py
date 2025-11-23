import faiss
import numpy as np
from datetime import datetime
from typing import List, Dict
import redis
from sentence_transformers import SentenceTransformer
import uuid


class MemoryManager:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dim = 384  # embedding size for all-MiniLM-L6-v2
        self.index = faiss.IndexFlatL2(self.dim)
        self.messages: List[Dict] = []
        self.embeddings: List[np.ndarray] = []
        self.redis = redis.Redis(host='localhost', port=6379, db=0)

    def add_message(self, content: str, labels: List[str]):
        embedding = self.model.encode([content]).astype('float32')
        self.index.add(embedding)
        self.embeddings.append(embedding[0])
        msg_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        msg_data = {
            "id": msg_id,
            "content": content,
            "labels": labels,
            "timestamp": timestamp,
            "embedding": embedding[0]  # store for reference
        }
        self.messages.append(msg_data)
        self.redis.set(msg_id, str(msg_data))

    def retrieve_contexts(self, query: str, top_k: int = 5) -> List[Dict]:
        if len(self.messages) == 0 or self.index.ntotal == 0:
            return []

        # encode the query
        query_embedding = self.model.encode([query]).astype('float32')
        k = min(top_k, len(self.messages))
        D, I = self.index.search(query_embedding, k)

        results = []
        for score, idx in zip(D[0], I[0]):
            if idx < 0 or idx >= len(self.messages):
                continue
            msg = self.messages[idx]
            results.append({
                "content": msg["content"],
                "labels": msg["labels"],
                "timestamp": msg["timestamp"],
                "score": float(score)
            })
        return results
