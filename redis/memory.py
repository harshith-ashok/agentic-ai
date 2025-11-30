import faiss
import numpy as np
from datetime import datetime
from typing import List, Dict
import redis
from sentence_transformers import SentenceTransformer
import uuid
import json


class MemoryManager:
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dim = 384
        self.index = faiss.IndexFlatL2(self.dim)
        self.messages: List[Dict] = []
        self.embeddings: List[np.ndarray] = []

        # connect to Redis
        self.redis = redis.Redis(host=redis_host, port=redis_port, db=redis_db)

        # load existing messages
        self._load_from_redis()

    def _load_from_redis(self):
        keys = self.redis.keys()
        for key in keys:
            raw = self.redis.get(key)
            if not raw:
                continue
            try:
                msg_data = json.loads(raw.decode())
                self.messages.append(msg_data)
                self.index.add(
                    np.array([msg_data["embedding"]], dtype="float32"))
                self.embeddings.append(msg_data["embedding"])
            except Exception as e:
                print(f"Failed to load key {key}: {e}")

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
            "embedding": embedding[0].tolist()
        }
        self.messages.append(msg_data)
        self.redis.set(msg_id, json.dumps(msg_data))

    def retrieve_contexts(self, query: str, top_k: int = 5, threshold: float = 1.2):
        if len(self.messages) == 0 or self.index.ntotal == 0:
            return []

        query_embedding = self.model.encode([query]).astype('float32')
        k = min(top_k, len(self.messages))
        D, I = self.index.search(query_embedding, k)

        results = []
        for score, idx in zip(D[0], I[0]):
            if idx < 0 or idx >= len(self.messages):
                continue
            # ignore irrelevant memory
            if score > threshold:
                continue
            msg = self.messages[idx]
            results.append({
                "content": msg["content"],
                "labels": msg["labels"],
                "timestamp": msg["timestamp"],
                "score": float(score)
            })

        return results
