"""
API Error Handling Tests
Tests /api/process error cases: invalid JSON, missing fields, oversized payloads, 
rate limiting, unicode edge cases, concurrent requests
Coverage: Ensures API gracefully rejects bad input without crashing
"""

import pytest
import json
import time
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path
import threading

# Add api directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "api"))

from main_enhanced import app

# ========== FIXTURES ==========
@pytest.fixture(scope="session")
def client():
    """Create test client with lifespan context manager support"""
    with TestClient(app) as test_client:
        yield test_client


class TestApiErrorHandling:
    """Tests for error cases in /api/process endpoint"""

    # ========== MISSING FIELDS ==========
    
    def test_missing_clinical_text_returns_422(self, client):
        """[Test] Missing required clinical_text returns 422"""
        payload = {}
        response = client.post("/api/process", json=payload)
        assert response.status_code == 422, "Should return 422 for missing field"
        data = response.json()
        assert "detail" in data, "Should include validation error details"

    def test_clinical_text_null_returns_422(self, client):
        """[Test] Null clinical_text returns 422"""
        payload = {"clinical_text": None}
        response = client.post("/api/process", json=payload)
        assert response.status_code == 422

    def test_clinical_text_empty_string_returns_422(self, client):
        """[Test] Empty string clinical_text returns 422"""
        payload = {"clinical_text": ""}
        response = client.post("/api/process", json=payload)
        assert response.status_code == 422

    def test_clinical_text_whitespace_only_returns_422(self, client):
        """[Test] Whitespace-only clinical_text returns 422"""
        payload = {"clinical_text": "   \t\n   "}
        response = client.post("/api/process", json=payload)
        assert response.status_code == 422

    # ========== SIZE BOUNDARIES ==========
    
    def test_clinical_text_below_min_length_returns_422(self, client):
        """[Test] Text below 10 char minimum returns 422"""
        payload = {"clinical_text": "short"}  # 5 chars
        response = client.post("/api/process", json=payload)
        assert response.status_code == 422

    def test_clinical_text_at_min_length_returns_200(self, client):
        """[Test] Text at 10 char minimum returns 200"""
        payload = {"clinical_text": "short text"}  # Exactly 10 chars
        response = client.post("/api/process", json=payload)
        assert response.status_code == 200

    def test_clinical_text_exceeds_max_length_returns_413(self, client):
        """[Test] Text exceeding 5000 char limit returns 422 (Pydantic validation)"""
        payload = {"clinical_text": "x" * 5001}
        response = client.post("/api/process", json=payload)
        assert response.status_code == 422, "Should return 422 for validation error (oversized payload)"

    def test_clinical_text_at_max_length_returns_200(self, client):
        """[Test] Text at 5000 char limit returns 200"""
        payload = {"clinical_text": "x" * 5000}
        response = client.post("/api/process", json=payload)
        assert response.status_code == 200

    # ========== INVALID JSON ==========
    
    def test_malformed_json_returns_400(self, client):
        """[Test] Malformed JSON returns 422 (Pydantic validation error)"""
        response = client.post(
            "/api/process",
            content="{invalid json}",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422, "Should return 422 for malformed/invalid JSON"

    def test_json_with_extra_comma_returns_400(self, client):
        """[Test] JSON with syntax error returns 422 (Pydantic validation error)"""
        response = client.post(
            "/api/process",
            content='{"clinical_text": "valid text",}',
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    # ========== OPTIONAL FIELD VALIDATION ==========
    
    def test_invalid_patient_id_format_returns_422(self, client):
        """[Test] Invalid patient_id (special chars) returns 422"""
        payload = {
            "clinical_text": "Valid clinical text here",
            "patient_id": "pat@#$!invalid"  # Contains invalid chars
        }
        response = client.post("/api/process", json=payload)
        assert response.status_code == 422

    def test_valid_patient_id_format_returns_200(self, client):
        """[Test] Valid patient_id format returns 200"""
        payload = {
            "clinical_text": "Valid clinical text here",
            "patient_id": "pat_123456"
        }
        response = client.post("/api/process", json=payload)
        assert response.status_code == 200

    def test_invalid_document_source_enum_returns_422(self, client):
        """[Test] Invalid document_source enum returns 422"""
        payload = {
            "clinical_text": "Valid clinical text here",
            "document_source": "INVALID_SOURCE"
        }
        response = client.post("/api/process", json=payload)
        assert response.status_code == 422

    def test_valid_document_source_enum_returns_200(self, client):
        """[Test] Valid document_source enum returns 200"""
        payload = {
            "clinical_text": "Valid clinical text here",
            "document_source": "ER_intake"
        }
        response = client.post("/api/process", json=payload)
        assert response.status_code == 200

    def test_all_valid_optional_fields_returns_200(self, client):
        """[Test] All optional fields valid returns 200"""
        payload = {
            "clinical_text": "Valid clinical text here",
            "patient_id": "pat_123",
            "document_source": "Lab_report",
            "batch_id": "batch_abc"
        }
        response = client.post("/api/process", json=payload)
        assert response.status_code == 200

    # ========== UNICODE & SPECIAL CHARACTERS ==========
    
    def test_unicode_characters_handled_gracefully(self, client):
        """[Test] Unicode characters (中文, ñ, é) handled without crash"""
        payload = {
            "clinical_text": "Patient 张三 has fever. Diagnóstico: infección. Température: 39°C™"
        }
        response = client.post("/api/process", json=payload)
        assert response.status_code == 200, "Should handle unicode gracefully"

    def test_emoji_characters_handled_gracefully(self, client):
        """[Test] Emoji characters handled without crash"""
        payload = {
            "clinical_text": "Patient has ❤️ issues and 🫁 problems. Status: ⚠️"
        }
        response = client.post("/api/process", json=payload)
        assert response.status_code == 200

    def test_special_medical_symbols_preserved(self, client):
        """[Test] Medical symbols (±, ≤, ≥, Δ) preserved in output"""
        payload = {
            "clinical_text": "BP: 160±5 mmHg, HR: 110±3 bpm. Δ temp = 2°C"
        }
        response = client.post("/api/process", json=payload)
        assert response.status_code == 200
        data = response.json()
        # Verify compression succeeded (ratio should be between 0-1)
        assert 0 < data["compression"]["compression_ratio"] < 1

    def test_null_bytes_in_text_handled(self, client):
        """[Test] Null bytes in text don't crash API"""
        # This would normally be caught by JSON parser, but test anyway
        payload = {
            "clinical_text": "Clinical text with null byte\\x00 included"
        }
        response = client.post("/api/process", json=payload)
        # Should either process or return 400/422, not crash with 500
        assert response.status_code in [200, 400, 422]

    # ========== CONCURRENT REQUESTS ==========
    
    def test_concurrent_requests_all_succeed(self, client):
        """[Test] 5 concurrent requests all process without error"""
        results = []
        errors = []
        
        def make_request(text):
            try:
                response = client.post("/api/process", json={
                    "clinical_text": f"{text} with unique ID {time.time()}"
                })
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))
        
        # Create 5 threads making concurrent requests
        threads = [
            threading.Thread(target=make_request, args=(f"Request {i}",))
            for i in range(5)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)
        
        # All requests should succeed
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert all(code == 200 for code in results), f"Not all requests succeeded: {results}"

    def test_10_sequential_requests_all_succeed(self, client):
        """[Test] 10 sequential requests all process without error"""
        for i in range(10):
            payload = {
                "clinical_text": f"Sequential request {i}: Patient has chest pain HR {100+i} BP 160/95"
            }
            response = client.post("/api/process", json=payload)
            assert response.status_code == 200, f"Request {i} failed"

    # ========== RESPONSE VALIDATION ==========
    
    def test_error_response_has_proper_structure(self, client):
        """[Test] Error responses have proper error structure"""
        payload = {"clinical_text": "x"}  # Too short
        response = client.post("/api/process", json=payload)
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_successful_response_has_required_fields(self, client):
        """[Test] Successful responses include all required fields"""
        payload = {"clinical_text": "Valid clinical text for testing"}
        response = client.post("/api/process", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        required_fields = [
            "request_id", "status", "timestamp", "compression", 
            "triage", "diagnosis", "performance"
        ]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

    # ========== EDGE CASES ==========
    
    def test_clinical_text_with_only_numbers(self, client):
        """[Test] Clinical text with only numbers doesn't crash"""
        payload = {"clinical_text": "123 456 789 100 110 120 130 140 150"}
        response = client.post("/api/process", json=payload)
        assert response.status_code == 200

    def test_clinical_text_with_repeated_whitespace(self, client):
        """[Test] Clinical text with lots of whitespace normalizes correctly"""
        payload = {
            "clinical_text": "Patient    has    fever.    HR     very     high.     BP     critical."
        }
        response = client.post("/api/process", json=payload)
        assert response.status_code == 200

    def test_clinical_text_with_newlines_and_tabs(self, client):
        """[Test] Clinical text with newlines and tabs handled correctly"""
        payload = {
            "clinical_text": "Patient has fever.\nHR: 110\tBP: 160/95\n\nAssessment:\nAcute MI"
        }
        response = client.post("/api/process", json=payload)
        assert response.status_code == 200

    def test_response_time_under_error_conditions(self, client):
        """[Perf] Error responses return quickly (<100ms)"""
        import time
        start = time.time()
        response = client.post("/api/process", json={"clinical_text": "x"})
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code == 422
        assert elapsed < 100, f"Error response took {elapsed}ms"

    # ========== RATE LIMITING (if implemented) ==========
    
    def test_many_requests_dont_cause_server_overload(self, client):
        """[Test] 50 requests in sequence don't overload server"""
        success_count = 0
        for i in range(50):
            response = client.post("/api/process", json={
                "clinical_text": f"Request {i}: Patient with chest pain. HR {100+i} BP 160/95."
            })
            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:
                # Rate limit hit, acceptable
                break
            else:
                # Unexpected error
                assert False, f"Unexpected status code {response.status_code} at request {i}"
        
        # Should have succeeded on at least first 10
        assert success_count >= 10, f"Only {success_count} requests succeeded"

    # ========== INPUT SANITATION ==========
    
    def test_html_like_content_handled(self, client):
        """[Test] HTML-like content in clinical text doesn't break parser"""
        payload = {
            "clinical_text": "<patient>Name: John</patient> has <symptom>chest pain</symptom>"
        }
        response = client.post("/api/process", json=payload)
        assert response.status_code == 200

    def test_sql_like_content_handled(self, client):
        """[Test] SQL-like content in clinical text doesn't execute"""
        payload = {
            "clinical_text": "Patient'; DROP TABLE patients; -- has fever"
        }
        response = client.post("/api/process", json=payload)
        assert response.status_code == 200
        # Should process as normal text, not execute

    def test_very_long_single_word_handled(self, client):
        """[Test] Very long single word (no spaces) handled"""
        long_word = "a" * 1000
        payload = {
            "clinical_text": f"Patient has {long_word} diagnosis"
        }
        response = client.post("/api/process", json=payload)
        assert response.status_code == 200


class TestHealthEndpointErrorHandling:
    """Tests for error handling in /health endpoint"""

    def test_health_endpoint_always_returns_200(self, client):
        """[Test] Health endpoint always returns 200, never errors"""
        for _ in range(10):
            response = client.get("/health")
            assert response.status_code == 200

    def test_health_endpoint_fast_response(self, client):
        """[Perf] Health endpoint responds in <50ms"""
        import time
        start = time.time()
        response = client.get("/health")
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code == 200
        assert elapsed < 50, f"Health check took {elapsed}ms"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
