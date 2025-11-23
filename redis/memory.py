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
        self.messages = []
        self.redis = redis.Redis(host='localhost', port=6379, db=0)

    def add_message(self, content: str, labels: List[str]):
        embedding = self.model.encode([content]).astype('float32')
        self.index.add(embedding)
        msg_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        msg_data = {
            "id": msg_id,
            "content": content,
            "labels": labels,
            "timestamp": timestamp
        }
        self.messages.append(msg_data)
        self.redis.set(msg_id, str(msg_data))

    def retrieve_contexts(self, query_labels: List[str], k: int = 5) -> List[Dict]:
        # collect all messages that match any label
        candidates = [m for m in self.messages if any(
            label in m['labels'] for label in query_labels)]
        # limit results
        return candidates[-k:]
