import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class VectorStore:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.dimension = 384
        self.index = faiss.IndexFlatL2(self.dimension)
        self.count = 0  # how many vectors stored

    def embed(self, text: str):
        v = self.model.encode([text], convert_to_numpy=True)
        return v.astype('float32')

    def add(self, text: str):
        vector = self.embed(text)
        self.index.add(vector)
        self.count += 1
        return self.count - 1

    def search(self, query: str, k=5):
        vector = self.embed(query)
        distances, indices = self.index.search(vector, k)
        return indices[0], distances[0]
