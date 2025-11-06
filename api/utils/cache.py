# api/utils/cache.py
from typing import Any
import threading
import time


class SimpleCache:
    def __init__(self, ttl: int = 5):
        self._data = None
        self._lock = threading.RLock()
        self.ttl = ttl
        self._ts = 0

    def get(self):
        with self._lock:
            if self._data is None:
                return None
            if self.ttl and (time.time() - self._ts) > self.ttl:
                self._data = None
                return None
            return self._data

    def set(self, value: Any):
        with self._lock:
            self._data = value
            self._ts = time.time()

    def invalidate(self):
        with self._lock:
            self._data = None
            self._ts = 0


# global caches
tags_cache = SimpleCache(ttl=2)
people_cache = SimpleCache(ttl=2)
