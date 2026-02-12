"""MCP Server - Exposes CompText compression as a tool for MCP-compatible clients."""

from __future__ import annotations

from src.core.codex import KVTCStrategy, KVTCResult


def compress_content(
    text: str,
    strategy: str = "kvtc",
    sink_chars: int = 500,
    window_chars: int = 1000,
) -> KVTCResult:
    """Compress clinical text for efficient context-window usage.

    This tool applies the **KVTC (Sink-Middle-Window)** strategy by default,
    which preserves the System Prompt (sink) at the start and the most recent
    interactions (window) at the end while aggressively compressing the
    redundant middle section using the CompText protocol.

    Args:
        text: The full input text to compress.
        strategy: Compression strategy to use.  Currently only ``"kvtc"`` is
            supported.  The KVTC strategy preserves:

            * The first *sink_chars* characters (System Prompt / role context).
            * The last *window_chars* characters (recent interactions).
            * Compresses the middle section via CompText.
        sink_chars: Number of characters to preserve at the start of the text
            (the "attention sink").  Defaults to 500.
        window_chars: Number of characters to preserve at the end of the text
            (the "sliding window").  Defaults to 1000.

    Returns:
        A ``KVTCResult`` with the compressed text and metadata.

    Raises:
        ValueError: If an unsupported strategy is specified.
    """
    if strategy != "kvtc":
        raise ValueError(
            f"Unsupported compression strategy: {strategy!r}. "
            "Currently only 'kvtc' is supported."
        )

    kvtc = KVTCStrategy()
    return kvtc.compress(text, sink_chars=sink_chars, window_chars=window_chars)
