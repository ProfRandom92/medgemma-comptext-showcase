"""Tests for CompTextCache and AINativeRecord."""

import json

import pytest

from src.core.cache_manager import CompTextCache
from src.core.codex import MedicalKVTCStrategy
from src.core.future_ehr import AINativeRecord


# ---------------------------------------------------------------------------
# CompTextCache
# ---------------------------------------------------------------------------

class TestCompTextCache:
    def setup_method(self):
        self.cache = CompTextCache()

    def test_miss_returns_none(self):
        assert self.cache.get("unknown text") is None

    def test_put_and_get(self):
        self.cache.put("hello world", "compressed")
        assert self.cache.get("hello world") == "compressed"

    def test_size_tracks_entries(self):
        assert self.cache.size == 0
        self.cache.put("a", "1")
        assert self.cache.size == 1
        self.cache.put("b", "2")
        assert self.cache.size == 2

    def test_clear_removes_all(self):
        self.cache.put("a", "1")
        self.cache.clear()
        assert self.cache.size == 0
        assert self.cache.get("a") is None

    def test_same_input_same_key(self):
        self.cache.put("text", "result")
        assert self.cache.get("text") == "result"

    def test_different_input_different_key(self):
        self.cache.put("text1", "r1")
        self.cache.put("text2", "r2")
        assert self.cache.get("text1") == "r1"
        assert self.cache.get("text2") == "r2"


# ---------------------------------------------------------------------------
# MedicalKVTCStrategy caching integration
# ---------------------------------------------------------------------------

class TestKVTCCaching:
    def test_cache_hit_returns_same_result(self):
        strategy = MedicalKVTCStrategy(sink_size=10, window_size=10)
        long_text = "H" * 10 + "M" * 200 + "R" * 10
        result1 = strategy.compress(long_text)
        result2 = strategy.compress(long_text)
        assert result1 == result2
        assert strategy._cache.size == 1

    def test_short_text_bypasses_cache(self):
        strategy = MedicalKVTCStrategy(sink_size=100, window_size=100)
        short_text = "short"
        result = strategy.compress(short_text)
        assert result == short_text
        assert strategy._cache.size == 0


# ---------------------------------------------------------------------------
# AINativeRecord
# ---------------------------------------------------------------------------

class TestAINativeRecord:
    def setup_method(self):
        self.ehr = AINativeRecord()
        self.raw = (
            "Chief complaint: chest pain. HR 110, BP 130/85, "
            "Temp 39.2C. Medication: aspirin."
        )

    def test_save_returns_metrics(self):
        result = self.ehr.save_record("PT-001", self.raw)
        assert result["patient_id"] == "PT-001"
        assert result["raw_chars"] == len(self.raw)
        assert result["compressed_chars"] > 0
        assert "compressed_json" in result

    def test_load_returns_saved_data(self):
        self.ehr.save_record("PT-001", self.raw)
        loaded = self.ehr.load_record("PT-001")
        assert loaded is not None
        assert "chief_complaint" in loaded

    def test_load_unknown_returns_none(self):
        assert self.ehr.load_record("UNKNOWN") is None

    def test_get_stats_returns_savings(self):
        self.ehr.save_record("PT-001", self.raw)
        stats = self.ehr.get_stats("PT-001", self.raw)
        assert "storage_saved_pct" in stats
        assert "tokens_saved_pct" in stats
        assert stats["raw_chars"] == len(self.raw)

    def test_get_stats_unknown_returns_error(self):
        stats = self.ehr.get_stats("UNKNOWN", self.raw)
        assert "error" in stats
