import os
import faiss
import numpy as np
import sqlite3
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
from datetime import datetime

# environment / persistence paths
DATA_DIR = os.getenv("MCP_DATA_DIR", "./data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
FAISS_INDEX_PATH = os.path.join(DATA_DIR, "faiss.index")
SQLITE_DB_PATH = os.path.join(DATA_DIR, "meta.db")

# embedding model (sentence-transformers)
EMBED_MODEL_NAME = os.getenv(
    "EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


class FaissMemory:
    def __init__(self, dim: int = 384):

        self.model = SentenceTransformer(EMBED_MODEL_NAME)

        emb_sample = self.model.encode("hello")
        self.dim = emb_sample.shape[-1]

        self.index = faiss.IndexFlatIP(self.dim)

        self.id_index = faiss.IndexIDMap(self.index)

        if os.path.exists(FAISS_INDEX_PATH):
            try:
                self.id_index = faiss.read_index(FAISS_INDEX_PATH)
            except Exception:

                pass

        self.conn = sqlite3.connect(SQLITE_DB_PATH, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id TEXT PRIMARY KEY,
                numeric_id INTEGER UNIQUE,
                conversation_id TEXT,
                role TEXT,
                content TEXT,
                timestamp TEXT,
                tags TEXT
            )
        """)
        # store a simple counter for numeric ids if needed
        cur.execute("""
            CREATE TABLE IF NOT EXISTS kv (
                k TEXT PRIMARY KEY,
                v TEXT
            )
        """)
        # initialize counter if not set
        cur.execute("INSERT OR IGNORE INTO kv (k, v) VALUES ('counter', '1')")
        self.conn.commit()

    def _next_numeric_id(self) -> int:
        cur = self.conn.cursor()
        cur.execute("SELECT v FROM kv WHERE k='counter'")
        v = int(cur.fetchone()[0])
        cur.execute("UPDATE kv SET v = ? WHERE k='counter'", (str(v+1),))
        self.conn.commit()
        return v

    def _serialize_tags(self, tags: List[str]) -> str:
        return ",".join(tags or [])

    def _deserialize_tags(self, s: str) -> List[str]:
        if not s:
            return []
        return [t for t in s.split(",") if t]

    def embed(self, texts: List[str]) -> np.ndarray:
        embs = self.model.encode(texts, show_progress_bar=False)
        embs = np.array(embs, dtype="float32")
        # normalize for cosine via inner product
        faiss.normalize_L2(embs)
        return embs

    def add_message(self, message_id: str, conversation_id: str, role: str, content: str,
                    timestamp: Optional[str], tags: List[str], replace: bool = False) -> Dict[str, Any]:
        cur = self.conn.cursor()
        # check if exists
        cur.execute(
            "SELECT numeric_id FROM messages WHERE message_id = ?", (message_id,))
        row = cur.fetchone()
        if row:
            numeric_id = row[0]
            if not replace:
                # don't re-add duplicate message
                return {"status": "exists", "numeric_id": numeric_id}
            else:
                # remove existing vector for numeric_id if possible:
                # faiss doesn't have direct delete for IndexFlat, but IndexIDMap supports remove_ids
                try:
                    self.id_index.remove_ids(
                        np.array([numeric_id], dtype=np.int64))
                except Exception:
                    pass
        else:
            numeric_id = self._next_numeric_id()

        # embed content
        vec = self.embed([content])
        # add with id
        try:
            self.id_index.add_with_ids(
                vec, np.array([numeric_id], dtype=np.int64))
        except Exception as e:
            # fallback: if index types mismatch, recreate id_index and add
            self.index = faiss.IndexFlatIP(self.dim)
            self.id_index = faiss.IndexIDMap(self.index)
            self.id_index.add_with_ids(
                vec, np.array([numeric_id], dtype=np.int64))

        # upsert metadata
        cur.execute("""
            INSERT OR REPLACE INTO messages (message_id, numeric_id, conversation_id, role, content, timestamp, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (message_id, numeric_id, conversation_id, role, content, timestamp or datetime.utcnow().isoformat(), self._serialize_tags(tags)))
        self.conn.commit()
        # persist index
        self.save_index()
        return {"status": "added", "numeric_id": numeric_id}

    def save_index(self):
        try:
            faiss.write_index(self.id_index, FAISS_INDEX_PATH)
        except Exception:
            pass

    def _get_metadata_for_numeric_ids(self, numeric_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        cur = self.conn.cursor()
        placeholders = ",".join("?" for _ in numeric_ids)
        q = f"SELECT numeric_id, message_id, conversation_id, role, content, timestamp, tags FROM messages WHERE numeric_id IN ({placeholders})"
        cur.execute(q, tuple(numeric_ids))
        res = {}
        for row in cur.fetchall():
            nid = row[0]
            res[nid] = {
                "message_id": row[1],
                "conversation_id": row[2],
                "role": row[3],
                "content": row[4],
                "timestamp": row[5],
                "tags": self._deserialize_tags(row[6])
            }
        return res

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        vec = self.embed([query])
        # Search returns (distances, indices)
        if self.id_index.ntotal == 0:
            return []
        D, I = self.id_index.search(vec, k)
        distances = D[0].tolist()
        indices = I[0].tolist()
        # filter out -1 indices
        pairs = [(int(idx), float(score))
                 for idx, score in zip(indices, distances) if idx != -1]
        # dedupe by message_id (in case multiple numeric IDs map to same message_id - unlikely here)
        numeric_ids = [p[0] for p in pairs]
        meta = self._get_metadata_for_numeric_ids(numeric_ids)
        results = []
        seen_message_ids = set()
        for nid, score in pairs:
            m = meta.get(nid)
            if not m:
                continue
            mid = m["message_id"]
            if mid in seen_message_ids:
                continue
            seen_message_ids.add(mid)
            results.append({
                "message_id": mid,
                "conversation_id": m["conversation_id"],
                "role": m["role"],
                "content": m["content"],
                "timestamp": m["timestamp"],
                "tags": m["tags"],
                "score": float(score)
            })
        return results

    def search_by_tag(self, tag: str, limit: int = 50) -> List[Dict[str, Any]]:
        cur = self.conn.cursor()
        q = "SELECT message_id, conversation_id, role, content, timestamp, tags FROM messages WHERE tags LIKE ? LIMIT ?"
        pattern = f"%{tag}%"
        cur.execute(q, (pattern, limit))
        results = []
        for row in cur.fetchall():
            results.append({
                "message_id": row[0],
                "conversation_id": row[1],
                "role": row[2],
                "content": row[3],
                "timestamp": row[4],
                "tags": row[5].split(",") if row[5] else [],
                "score": None
            })
        return results

    def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT message_id, numeric_id, conversation_id, role, content, timestamp, tags FROM messages WHERE message_id=?", (message_id,))
        row = cur.fetchone()
        if not row:
            return None
        return {
            "message_id": row[0],
            "numeric_id": row[1],
            "conversation_id": row[2],
            "role": row[3],
            "content": row[4],
            "timestamp": row[5],
            "tags": row[6].split(",") if row[6] else []
        }
