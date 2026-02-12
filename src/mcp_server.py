"""MCP Server - Exposes CompText tools over a simple interface."""

from __future__ import annotations

from src.core.codex import MedicalKVTCStrategy


def compress_content(text: str, *, mode: str = "medical_safe") -> str:
    """Compress clinical text using the configured strategy.

    Args:
        text: Raw clinical / conversation text.
        mode: Compression mode.  ``"medical_safe"`` (default) uses the
              KVTC Sandwich Strategy that preserves critical header and
              recent-context regions verbatim.

    Returns:
        The compressed text string.
    """
    if mode == "medical_safe":
        strategy = MedicalKVTCStrategy()
    else:
        raise ValueError(
            f"Unsupported compression mode: {mode!r}. "
            "Currently only 'medical_safe' is supported."
        )

    return strategy.compress(text)
