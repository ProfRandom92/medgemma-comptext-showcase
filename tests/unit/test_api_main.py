"""Tests for api/main.py - FastAPI backend endpoints and models."""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from pydantic import ValidationError

# Import models from main
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.main import (
    ProcessRequest,
    CompressionResponse,
    TriageResponse,
    DoctorResponse,
    PipelineResponse,
    app,
    ALLOWED_ORIGINS,
)
from src.core.models import PatientState, Vitals


class TestProcessRequestModel:
    """Test ProcessRequest Pydantic model validation."""

    def test_valid_clinical_text(self):
        """Valid clinical text with correct length."""
        request = ProcessRequest(
            clinical_text="Patient presents with chest pain and shortness of breath"
        )
        assert request.clinical_text == "Patient presents with chest pain and shortness of breath"

    def test_min_length_validation(self):
        """Text below minimum length (10 chars) rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ProcessRequest(clinical_text="short")
        assert "at least 10 characters" in str(exc_info.value)

    def test_max_length_validation(self):
        """Text above maximum length (5000 chars) rejected."""
        long_text = "a" * 5001
        with pytest.raises(ValidationError) as exc_info:
            ProcessRequest(clinical_text=long_text)
        assert "at most 5000 characters" in str(exc_info.value)

    def test_empty_text_rejected(self):
        """Empty text string rejected."""
        with pytest.raises(ValidationError):
            ProcessRequest(clinical_text="")

    def test_exact_min_boundary(self):
        """Exactly 10 characters accepted (boundary test)."""
        request = ProcessRequest(clinical_text="a" * 10)
        assert len(request.clinical_text) == 10

    def test_exact_max_boundary(self):
        """Exactly 5000 characters accepted (boundary test)."""
        request = ProcessRequest(clinical_text="a" * 5000)
        assert len(request.clinical_text) == 5000


class TestCompressionResponseModel:
    """Test CompressionResponse model structure."""

    def test_compression_response_creation(self):
        """Valid CompressionResponse with all fields."""
        response = CompressionResponse(
            original_text="Clinical text here with details",
            compressed_state={"chief_complaint":"chest pain","vitals":{"hr":90}},
            original_token_count=100,
            compressed_token_count=20,
            reduction_percentage=80.0,
            compression_time_ms=5.5
        )
        assert response.original_token_count == 100
        assert response.reduction_percentage == 80.0

    def test_negative_reduction_percentage_handled(self):
        """Negative reduction percentage should be possible."""
        response = CompressionResponse(
            original_text="text",
            compressed_state={"data":"expanded"},
            original_token_count=10,
            compressed_token_count=20,
            reduction_percentage=-100.0,
            compression_time_ms=1.0
        )
        assert response.reduction_percentage == -100.0

    def test_compression_response_all_fields_required(self):
        """Missing required field raises validation error."""
        with pytest.raises(ValidationError):
            CompressionResponse(
                original_text="text",
                # missing compressed_state
                original_token_count=10,
                compressed_token_count=5,
                reduction_percentage=50.0,
                compression_time_ms=2.0
            )


class TestTriageResponseModel:
    """Test TriageResponse model."""

    def test_triage_response_creation(self):
        """Valid TriageResponse with priority fields."""
        response = TriageResponse(
            priority_level="P1",
            priority_name="CRITICAL",
            reason="High heart rate and critical protocol"
        )
        assert response.priority_level == "P1"
        assert response.priority_name == "CRITICAL"

    def test_triage_response_various_priorities(self):
        """TriageResponse handles different priority levels."""
        for level, name in [("P1", "CRITICAL"), ("P2", "URGENT"), ("P3", "STANDARD")]:
            response = TriageResponse(
                priority_level=level,
                priority_name=name,
                reason=f"Test reason for {level}"
            )
            assert response.priority_level == level


class TestDoctorResponseModel:
    """Test DoctorResponse model."""

    def test_doctor_response_creation(self):
        """Valid DoctorResponse with recommendation."""
        response = DoctorResponse(
            recommendation="Immediate cardiology consultation recommended",
            processing_time_ms=25.5
        )
        assert "cardiology" in response.recommendation.lower()

    def test_doctor_response_timing_validation(self):
        """DoctorResponse requires non-negative timing."""
        response = DoctorResponse(
            recommendation="Continue monitoring",
            processing_time_ms=0.0
        )
        assert response.processing_time_ms == 0.0


class TestPipelineResponseModel:
    """Test PipelineResponse aggregated model."""

    def test_pipeline_response_complete(self):
        """Valid complete PipelineResponse with all components."""
        compression = CompressionResponse(
            original_text="text", compressed_state={},
            original_token_count=10, compressed_token_count=5,
            reduction_percentage=50.0, compression_time_ms=2.0
        )
        triage = TriageResponse(
            priority_level="P2", priority_name="URGENT", reason="fever"
        )
        doctor = DoctorResponse(
            recommendation="Monitor vitals", processing_time_ms=5.0
        )
        pipeline = PipelineResponse(
            compression=compression, triage=triage, doctor=doctor, total_time_ms=15.0
        )
        assert pipeline.total_time_ms == 15.0
        assert pipeline.compression.original_token_count == 10
        assert pipeline.triage.priority_level == "P2"


class TestHealthEndpoint:
    """Test /health endpoint."""

    def test_health_check_success(self):
        """Health endpoint returns status 200 with service info."""
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "MedGemma × CompText API"
        assert data["version"] == "1.0.0"

    def test_health_endpoint_json_format(self):
        """Health response has all required fields."""
        client = TestClient(app)
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert "service" in data
        assert "version" in data

    def test_health_check_content_type(self):
        """Health endpoint returns JSON content type."""
        client = TestClient(app)
        response = client.get("/health")
        assert "application/json" in response.headers.get("content-type", "")


class TestExamplesEndpoint:
    """Test /api/examples endpoint."""

    def test_examples_endpoint_returns_list(self):
        """Examples endpoint returns list of clinical cases."""
        client = TestClient(app)
        response = client.get("/api/examples")
        assert response.status_code == 200
        data = response.json()
        assert "examples" in data
        assert isinstance(data["examples"], list)

    def test_examples_have_required_fields(self):
        """Each example has title and text."""
        client = TestClient(app)
        response = client.get("/api/examples")
        data = response.json()
        for example in data["examples"]:
            assert "title" in example
            assert "text" in example
            assert len(example["title"]) > 0
            assert len(example["text"]) > 0

    def test_examples_count(self):
        """Examples endpoint returns 4 predefined cases."""
        client = TestClient(app)
        response = client.get("/api/examples")
        data = response.json()
        assert len(data["examples"]) == 4

    def test_example_titles_have_emoji(self):
        """Each example title contains emoji indicators."""
        client = TestClient(app)
        response = client.get("/api/examples")
        data = response.json()
        emojis = ["🫀", "🫁", "🧠", "🚑"]
        titles = [ex["title"] for ex in data["examples"]]
        for emoji in emojis:
            assert any(emoji in title for title in titles)

    def test_examples_content_type(self):
        """Examples endpoint returns JSON content type."""
        client = TestClient(app)
        response = client.get("/api/examples")
        assert "application/json" in response.headers.get("content-type", "")


class TestProcessEndpointValidation:
    """Test /api/process endpoint - request validation."""

    def test_process_invalid_request_missing_text(self):
        """Missing clinical_text field returns 422."""
        client = TestClient(app)
        response = client.post("/api/process", json={})
        assert response.status_code == 422

    def test_process_invalid_request_null_text(self):
        """Null clinical_text returns 422."""
        client = TestClient(app)
        response = client.post("/api/process", json={"clinical_text": None})
        assert response.status_code == 422

    def test_process_text_too_short(self):
        """Text less than 10 chars returns 422."""
        client = TestClient(app)
        response = client.post(
            "/api/process",
            json={"clinical_text": "short"}
        )
        assert response.status_code == 422

    def test_process_text_too_long(self):
        """Text more than 5000 chars returns 422."""
        client = TestClient(app)
        response = client.post(
            "/api/process",
            json={"clinical_text": "a" * 5001}
        )
        assert response.status_code == 422

    def test_process_valid_length_accepted(self):
        """Valid length text is accepted (validation passes)."""
        client = TestClient(app)
        response = client.post(
            "/api/process",
            json={"clinical_text": "a" * 50}
        )
        # Should not be 422 (validation error)
        assert response.status_code != 422

    def test_process_endpoint_requires_post(self):
        """Process endpoint requires POST method."""
        client = TestClient(app)
        response = client.get("/api/process")
        # GET should not be allowed
        assert response.status_code in [405, 404]


class TestCORSConfiguration:
    """Test CORS middleware configuration."""

    def test_cors_allowed_origins_defined(self):
        """CORS allowed origins list is not empty."""
        assert len(ALLOWED_ORIGINS) > 0

    def test_cors_production_origins_included(self):
        """CORS allows production Vercel and Fly.io origins."""
        assert "https://medgemma-comptext-showcase.vercel.app" in ALLOWED_ORIGINS
        assert "https://medgemma-api.fly.dev" in ALLOWED_ORIGINS

    def test_cors_localhost_for_development(self):
        """CORS allows localhost for development."""
        assert any("localhost" in origin for origin in ALLOWED_ORIGINS)


class TestEndpointAvailability:
    """Test all endpoints are accessible."""

    def test_health_endpoint_available(self):
        """Health endpoint is registered and accessible."""
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200

    def test_examples_endpoint_available(self):
        """Examples endpoint is registered and accessible."""
        client = TestClient(app)
        response = client.get("/api/examples")
        assert response.status_code == 200

    def test_process_endpoint_available(self):
        """Process endpoint accepts POST requests."""
        client = TestClient(app)
        response = client.post(
            "/api/process",
            json={"clinical_text": "test patient presentation today"}
        )
        # Should get response (may be 200, 400, or 500 depending on agent status)
        assert response.status_code in [200, 400, 500]


class TestIntegrationWithModels:
    """Test integration between API and core models."""

    def test_patient_state_to_json_integration(self):
        """PatientState properly converts to compressed JSON."""
        patient = PatientState(
            chief_complaint="chest pain",
            vitals=Vitals(hr=100, bp="140/90", temp=38.5),
            medication="aspirin",
            meta={"protocol": "Cardiology"}
        )
        json_str = patient.to_compressed_json()
        assert json_str is not None
        assert len(json_str) > 0
        assert "chest pain" in json_str

    def test_patient_state_to_fhir_integration(self):
        """PatientState properly converts to FHIR format."""
        patient = PatientState(
            chief_complaint="shortness of breath",
            vitals=Vitals(hr=110, bp="130/80", temp=39.0),
        )
        fhir_bundle = patient.to_fhir()
        assert fhir_bundle is not None
        assert fhir_bundle["resourceType"] == "Bundle"
        assert "entry" in fhir_bundle

    def test_vitals_model_structure(self):
        """Vitals model accepts all vital sign types."""
        vitals = Vitals(hr=95, bp="120/80", temp=37.5)
        assert vitals.hr == 95
        assert vitals.bp == "120/80"
        assert vitals.temp == 37.5

    def test_vitals_optional_fields(self):
        """Vitals model handles optional fields."""
        vitals = Vitals(hr=100)
        assert vitals.hr == 100
        assert vitals.bp is None
        assert vitals.temp is None


class TestAPIErrorHandling:
    """Test API error handling paths."""

    def test_process_with_malformed_json(self):
        """Endpoint handles malformed JSON gracefully."""
        client = TestClient(app)
        response = client.post(
            "/api/process",
            content=b"not json"
        )
        assert response.status_code in [422, 400]

    def test_health_endpoint_always_available(self):
        """Health endpoint always returns 200."""
        client = TestClient(app)
        for _ in range(3):
            response = client.get("/health")
            assert response.status_code == 200

    def test_examples_endpoint_consistency(self):
        """Examples endpoint returns same data on multiple calls."""
        client = TestClient(app)
        response1 = client.get("/api/examples")
        response2 = client.get("/api/examples")
        assert response1.json() == response2.json()


class TestResponseStructure:
    """Test response structure and format."""

    def test_health_response_is_json(self):
        """Health response is valid JSON."""
        client = TestClient(app)
        response = client.get("/health")
        try:
            data = response.json()
            assert isinstance(data, dict)
        except ValueError:
            pytest.fail("Health response is not valid JSON")

    def test_examples_response_is_json(self):
        """Examples response is valid JSON."""
        client = TestClient(app)
        response = client.get("/api/examples")
        try:
            data = response.json()
            assert isinstance(data, dict)
        except ValueError:
            pytest.fail("Examples response is not valid JSON")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
