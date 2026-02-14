"""Safety tests for the Medical KVTC Sandwich Strategy."""

import pytest

from src.core.codex import MedicalKVTCStrategy
from src.mcp_server import compress_content


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_long_text(
    header: str, middle: str, recent: str, *, sink: int = 800, window: int = 1500
) -> str:
    """Build a test string guaranteed to have distinct sink / middle / window regions."""
    header_part = header.ljust(sink, ".")
    recent_part = recent.rjust(window, ".")
    return header_part + middle + recent_part


# ---------------------------------------------------------------------------
# MedicalKVTCStrategy unit tests
# ---------------------------------------------------------------------------

class TestMedicalKVTCStrategy:
    def setup_method(self):
        self.strategy = MedicalKVTCStrategy()

    # -- system prompt integrity ------------------------------------------

    def test_system_prompt_integrity(self):
        """First 800 chars must be bit-exact identical after compression."""
        header = "SYSTEM PROMPT: You are a medical assistant. " * 20
        middle = "Patient history entry. " * 200
        recent = "Current symptom: severe headache. " * 50
        raw = _build_long_text(header, middle, recent)

        compressed = self.strategy.compress(raw)

        assert compressed[: self.strategy.sink_size] == raw[: self.strategy.sink_size]

    # -- recent context integrity -----------------------------------------

    def test_recent_context_integrity(self):
        """Last 1500 chars must be bit-exact identical after compression."""
        header = "SYSTEM PROMPT: Medical disclaimer here. " * 20
        middle = "Intermediate notes. " * 200
        recent = "Patient reports acute chest pain radiating to left arm. " * 30
        raw = _build_long_text(header, middle, recent)

        compressed = self.strategy.compress(raw)

        assert compressed[-self.strategy.window_size :] == raw[-self.strategy.window_size :]

    # -- compression ratio ------------------------------------------------

    def test_compression_ratio(self):
        """The middle part must actually be reduced in size."""
        header = "H" * 800
        # Build a highly redundant middle to ensure compression
        middle = ("The patient was seen yesterday. " * 100) + (
            "The patient was seen yesterday. " * 100
        )
        recent = "R" * 1500
        raw = header + middle + recent

        compressed = self.strategy.compress(raw)

        assert len(compressed) < len(raw)

    # -- short text pass-through ------------------------------------------

    def test_short_text_unchanged(self):
        """Text shorter than sink + window is returned unchanged."""
        short = "Short clinical note."
        assert self.strategy.compress(short) == short

    # -- exact boundary text unchanged ------------------------------------

    def test_boundary_text_unchanged(self):
        """Text exactly sink + window long is returned unchanged."""
        exact = "A" * (800 + 1500)
        assert self.strategy.compress(exact) == exact


# ---------------------------------------------------------------------------
# compress_content (MCP server entry-point) tests
# ---------------------------------------------------------------------------

class TestCompressContent:
    def test_defaults_to_medical_safe(self):
        """compress_content uses medical_safe mode by default."""
        header = "D" * 800
        middle = "Repetitive note. " * 300
        recent = "W" * 1500
        raw = header + middle + recent

        result = compress_content(raw)

        # Header and recent must be preserved
        assert result[:800] == header
        assert result[-1500:] == recent
        # Middle should be compressed
        assert len(result) < len(raw)

    def test_mode_parameter_accepted(self):
        """The mode parameter is accepted without error."""
        result = compress_content("Hello", mode="medical_safe")
        assert result == "Hello"
