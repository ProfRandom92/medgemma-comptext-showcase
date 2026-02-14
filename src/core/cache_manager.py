"""Cache Manager - Hash-based caching for CompText middle-section compression."""

from __future__ import annotations

import hashlib


class CompTextCache:
    """Simple hash-based cache for compressed text segments.

    Stores compressed results keyed by the SHA-256 hash of the input text,
    avoiding redundant compression of unchanged content (e.g. the stable
    "middle" history section of a patient record).
    """

    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    @staticmethod
    def _key(text: str) -> str:
        """Return a deterministic cache key for *text*."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def get(self, text: str) -> str | None:
        """Return the cached result for *text*, or ``None`` on a miss."""
        return self._store.get(self._key(text))

    def put(self, text: str, compressed: str) -> None:
        """Store the *compressed* result for *text*."""
        self._store[self._key(text)] = compressed

    @property
    def size(self) -> int:
        """Number of entries currently in the cache."""
        return len(self._store)

    def clear(self) -> None:
        """Remove all cached entries."""
        self._store.clear()
