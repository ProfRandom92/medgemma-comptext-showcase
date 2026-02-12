"""Future EHR - AI-Native Patient Record simulation module.

Demonstrates the 'Universal AI Record' concept where any facility can
instantly load a pre-compressed patient context, eliminating redundant
intake processing.
"""

from __future__ import annotations

import json
from typing import Any

from src.core.comptext import CompTextProtocol


class AINativeRecord:
    """Simulates an AI-Native Electronic Health Record.

    Records are compressed via CompText and stored as JSON in an in-memory
    dictionary (simulating a shared database).
    """

    def __init__(self) -> None:
        self._db: dict[str, str] = {}
        self._protocol = CompTextProtocol()

    def save_record(self, patient_id: str, raw_text: str) -> dict[str, Any]:
        """Compress *raw_text* and persist it under *patient_id*.

        Args:
            patient_id: Unique patient identifier.
            raw_text: Free-form clinical text.

        Returns:
            A dict with ``patient_id``, ``compressed_json``, and size
            metrics (``raw_chars``, ``compressed_chars``).
        """
        state = self._protocol.compress(raw_text)
        compressed_json = state.to_compressed_json()
        self._db[patient_id] = compressed_json

        return {
            "patient_id": patient_id,
            "compressed_json": compressed_json,
            "raw_chars": len(raw_text),
            "compressed_chars": len(compressed_json),
        }

    def load_record(self, patient_id: str) -> dict[str, Any] | None:
        """Retrieve the compressed record for *patient_id*.

        Returns:
            Parsed JSON dict, or ``None`` if the patient is not found.
        """
        stored = self._db.get(patient_id)
        if stored is None:
            return None
        return json.loads(stored)

    def get_stats(self, patient_id: str, raw_text: str) -> dict[str, Any]:
        """Return comparison metrics for *patient_id*.

        Args:
            patient_id: Unique patient identifier (must already be saved).
            raw_text: The original uncompressed text for comparison.

        Returns:
            A dict with storage and token savings metrics.
        """
        stored = self._db.get(patient_id)
        if stored is None:
            return {"error": "Patient not found"}

        raw_chars = len(raw_text)
        compressed_chars = len(stored)
        raw_tokens = max(1, raw_chars // 4)
        compressed_tokens = max(1, compressed_chars // 4)

        return {
            "patient_id": patient_id,
            "raw_chars": raw_chars,
            "compressed_chars": compressed_chars,
            "storage_saved_pct": round(
                (1 - compressed_chars / raw_chars) * 100, 1
            ) if raw_chars > 0 else 0.0,
            "raw_tokens": raw_tokens,
            "compressed_tokens": compressed_tokens,
            "tokens_saved_pct": round(
                (1 - compressed_tokens / raw_tokens) * 100, 1
            ) if raw_tokens > 0 else 0.0,
        }
