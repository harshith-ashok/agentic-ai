import ast
import redis
from pymongo import MongoClient
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from datetime import datetime
import uuid


class MemoryManager:
    def __init__(self, redis_url, mongo_url, mongo_db="ai_memory"):
        self.redis = redis.Redis.from_url(redis_url, decode_responses=True)
        self.mongo = MongoClient(mongo_url)
        self.db = self.mongo[mongo_db]
        self.long_term = self.db["long_term_memory"]
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.dimension = 384
        self.index = faiss.IndexFlatL2(self.dimension)
        self._load_faiss()

    def save_short(self, session_id, message):
        key = f"session:{session_id}"
        entry = {
            "id": str(uuid.uuid4()),
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.redis.rpush(key, str(entry))

    def get_short(self, session_id):
        key = f"session:{session_id}"
        raw = self.redis.lrange(key, 0, -1)
        messages = []
        for item in raw:
            try:
                entry = ast.literal_eval(item)
                messages.append(entry["message"])
            except:
                continue
        return messages

    def clear_short(self, session_id):
        key = f"session:{session_id}"
        self.redis.delete(key)

    def save_long(self, text):
        embedding = self.embedder.encode([text])[0].astype("float32")
        doc_id = str(uuid.uuid4())
        self.long_term.insert_one({
            "_id": doc_id,
            "text": text,
            "embedding": embedding.tolist(),
            "timestamp": datetime.utcnow()
        })
        self.index.add(np.array([embedding]))
        return doc_id

    def get_long(self, query, top_k=5):
        query_emb = self.embedder.encode([query])[0].astype("float32")
        if self.index.ntotal == 0:
            return []
        distances, indices = self.index.search(np.array([query_emb]), top_k)
        results = []
        for idx in indices[0]:
            if idx == -1:
                continue
            py_idx = int(idx)
            doc = self.long_term.find().skip(py_idx).limit(1)
            for d in doc:
                results.append(d["text"])
        return results

    def clear_long(self):
        self.long_term.delete_many({})
        self.index.reset()

    def _load_faiss(self):
        all_docs = list(self.long_term.find())
        if not all_docs:
            return
        embeddings = [np.array(d["embedding"], dtype="float32")
                      for d in all_docs]
        self.index.add(np.array(embeddings))
