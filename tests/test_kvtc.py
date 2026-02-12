"""Tests for the KVTC (Sink-Middle-Window) compression strategy."""

import pytest

from src.core.codex import KVTCStrategy, KVTCResult
from src.mcp_server import compress_content


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_long_text(
    head: str = "",
    middle: str = "",
    tail: str = "",
    sink_chars: int = 500,
    window_chars: int = 1000,
) -> str:
    """Build a text string where *head*, *middle*, and *tail* are padded to
    fill the sink, middle, and window regions exactly."""
    head_padded = head.ljust(sink_chars, ".")
    tail_padded = tail.rjust(window_chars, ".")
    # Ensure the middle is large enough that overall text > sink + window
    if len(middle) == 0:
        middle = "A" * 2000
    return head_padded + middle + tail_padded


# ---------------------------------------------------------------------------
# KVTCStrategy – core logic
# ---------------------------------------------------------------------------

class TestKVTCStrategy:
    def setup_method(self):
        self.strategy = KVTCStrategy()

    def test_short_text_is_not_compressed(self):
        short = "This is a short text."
        result = self.strategy.compress(short)

        assert result.was_compressed is False
        assert result.text == short

    def test_head_is_preserved_exactly(self):
        """Test 1: System Prompt (first 500 chars) is bit-exact identical."""
        head = "SYSTEM PROMPT: You are a medical assistant."
        text = _make_long_text(head=head)
        result = self.strategy.compress(text)

        assert result.was_compressed is True
        # The head should be the first 500 chars of the original text
        expected_head = text[:500]
        assert result.head == expected_head
        # The head must also appear at the very start of the output
        assert result.text.startswith(expected_head)

    def test_tail_is_preserved_exactly(self):
        """Test 2: Recent Context (last 1000 chars) is bit-exact identical."""
        tail = "Patient reports feeling better after medication."
        text = _make_long_text(tail=tail)
        result = self.strategy.compress(text)

        assert result.was_compressed is True
        expected_tail = text[-1000:]
        assert result.tail == expected_tail
        # The tail must appear at the very end of the output
        assert result.text.endswith(expected_tail)

    def test_token_reduction_exceeds_50_percent(self):
        """Test 3: Overall token reduction is still > 50%.

        Uses a simple whitespace-based token estimate since tiktoken requires
        network access to download its encoding data.
        """

        def _estimate_tokens(text: str) -> int:
            """Rough token count: split on whitespace."""
            return len(text.split())

        # Build a large, repetitive middle section to ensure good compression
        middle = (
            "Chief complaint: chest pain. HR 110, BP 130/85, Temp 39.2C. "
            "Medication: aspirin. Patient reports chest pain radiating to "
            "left arm. Pain is sharp. "
        ) * 50
        text = _make_long_text(middle=middle)

        result = self.strategy.compress(text)
        assert result.was_compressed is True

        original_tokens = _estimate_tokens(text)
        compressed_tokens = _estimate_tokens(result.text)
        reduction = 1 - (compressed_tokens / original_tokens)

        assert reduction > 0.50, (
            f"Token reduction was only {reduction:.1%}, expected > 50%"
        )

    def test_compressed_middle_is_present(self):
        text = _make_long_text()
        result = self.strategy.compress(text)

        assert result.compressed_middle is not None
        assert "[...Context Compressed...]" in result.text
        assert "[...Recent Context...]" in result.text

    def test_custom_sink_and_window_sizes(self):
        sink = 200
        window = 300
        text = "X" * 1000  # large enough
        result = self.strategy.compress(text, sink_chars=sink, window_chars=window)

        assert result.was_compressed is True
        assert result.head == text[:sink]
        assert result.tail == text[-window:]


# ---------------------------------------------------------------------------
# MCP Server – compress_content tool
# ---------------------------------------------------------------------------

class TestCompressContentTool:
    def test_default_strategy_is_kvtc(self):
        text = _make_long_text()
        result = compress_content(text)

        assert isinstance(result, KVTCResult)
        assert result.was_compressed is True

    def test_unsupported_strategy_raises(self):
        with pytest.raises(ValueError, match="Unsupported compression strategy"):
            compress_content("hello", strategy="unknown")

    def test_preserves_head_and_tail(self):
        head = "HEAD_MARKER"
        tail = "TAIL_MARKER"
        text = _make_long_text(head=head, tail=tail)
        result = compress_content(text)

        assert result.text.startswith(text[:500])
        assert result.text.endswith(text[-1000:])
