"""
Integration Tests for Medical Text Compression Pipeline
Tests: End-to-end compression flow, clinical data samples, metrics
Coverage: Real compression scenarios with medical text
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
import time

# Add api directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "api"))

from main_enhanced import app


@pytest.fixture(scope="module")
def client():
    """Create test client with lifespan context manager support."""
    with TestClient(app) as test_client:
        yield test_client


class TestCompressionPipelineIntegration:
    """Integration tests for full compression pipeline"""

    # Sample clinical texts for testing
    SAMPLE_CASES = {
        "acute_mi": {
            "text": """
                CHIEF COMPLAINT: Chest pain
                HISTORY OF PRESENT ILLNESS: 65-year-old male presents to emergency department 
                with acute onset substernal chest pain radiating to left arm. Pain began 2 hours ago 
                while at rest. Patient reports associated shortness of breath, diaphoresis, and nausea.
                PAST MEDICAL HISTORY: Hypertension, hyperlipidemia, diabetes mellitus type 2
                MEDICATIONS: Lisinopril 20mg daily, atorvastatin 80mg daily, metformin 1000mg BID
                ALLERGIES: NKDA
                VITAL SIGNS: BP 160/95, HR 110, RR 22, O2 sat 96%
                PHYSICAL EXAMINATION: Alert and oriented, diaphoretic, in distress
                CARDIAC: Tachycardic, no murmurs
                LUNGS: Clear bilaterally
                ABDOMEN: Soft, non-tender
                EKG: ST elevation 2mm in leads II, III, aVF with reciprocal ST depression
                LAB RESULTS: Troponin 2.5 ng/mL (high), CK-MB 85 U/L (high), BNP 400 pg/mL
                IMPRESSION: Acute ST elevation MI inferior wall
                PLAN: Cardiac catheterization, PCI, dual antiplatelet therapy, beta blocker
            """,
            "expected_ratio_min": 0.50,
            "category": "Acute MI"
        },
        "sepsis_case": {
            "text": """
                PATIENT: 78-year-old female with fever, chills, and confusion
                PRESENTATION: Admitted from nursing home with fever (39.2°C), altered mental status
                VITALS: BP 90/60, HR 115, RR 28, O2 sat 90% on room air
                LABS: WBC 18.2, Lactate 4.2, Procalcitonin 8.5, CRP 180
                CULTURES: Blood cultures drawn, pending
                IMAGING: Chest X-ray shows RLL infiltrate, consistent with pneumonia
                PAST MEDICAL: COPD, CHF, CKD stage 3
                MEDICATIONS: Furosemide, albuterol inhaler, aspirin
                ASSESSMENT: Sepsis secondary to community-acquired pneumonia
                ANTIBIOTICS: Ceftriaxone 2g IV Q12H + azithromycin 500mg IV Q24H started
                SUPPORT: IV fluids bolus, vasopressor evaluation if needed
                FOLLOW-UP: Repeat lactate in 3 hours, reassess mental status
            """,
            "expected_ratio_min": 0.50,
            "category": "Sepsis"
        },
        "routine_visit": {
            "text": """
                OFFICE NOTE - ROUTINE VISIT
                Patient: 45-year-old male
                Chief Complaint: Annual physical examination
                History: No acute complaints, feeling well
                Vitals: BP 128/82, HR 72, Weight 180 lbs (stable)
                Physical Exam: General healthy appearance, lungs clear, heart regular rate and rhythm
                Assessment: Hypertension controlled, otherwise healthy
                Plan: Continue current antihypertensive, recheck BP in 3 months, routine lab work annual
            """,
            "expected_ratio_min": 0.50,
            "category": "Routine"
        }
    }

    @pytest.mark.parametrize("case_name,case_data", SAMPLE_CASES.items())
    def test_compression_with_clinical_samples(self, client, case_name, case_data):
        """[Test] Compression works with various clinical samples"""
        payload = {"clinical_text": case_data["text"]}
        response = client.post("/api/process", json=payload)
        
        assert response.status_code == 200, f"Failed for {case_name}"
        data = response.json()
        assert data["compression"]["compressed_data"] is not None
        assert data["compression"]["compression_ratio"] > 0

    @pytest.mark.parametrize("case_name,case_data", SAMPLE_CASES.items())
    def test_compression_ratio_meets_targets(self, client, case_name, case_data):
        """[Test] Compression ratio meets target"""
        payload = {"clinical_text": case_data["text"]}
        response = client.post("/api/process", json=payload)
        
        data = response.json()
        ratio = data["compression"]["compression_ratio"]
        
        assert ratio >= case_data["expected_ratio_min"], \
            f"{case_name}: ratio {ratio} below minimum {case_data['expected_ratio_min']}"

    @pytest.mark.parametrize("case_name,case_data", SAMPLE_CASES.items())
    def test_compression_time_within_budget(self, client, case_name, case_data):
        """[Perf] Compression stays within <50ms budget"""
        payload = {"clinical_text": case_data["text"]}
        
        start = time.time()
        response = client.post("/api/process", json=payload)
        total_time = (time.time() - start) * 1000
        
        assert response.status_code == 200
        data = response.json()
        compression_time = data["compression"]["compression_time_ms"]
        
        # Compression time should be under 50ms
        assert compression_time < 50, \
            f"{case_name}: {compression_time}ms exceeds 50ms budget"

    def test_compression_preserves_medical_data(self, client):
        """[Test] Compression preserves critical medical information"""
        original = """
            DIAGNOSIS: Type 2 Diabetes Mellitus with Hypertension
            MEDICATIONS: Metformin 1000mg BID, Lisinopril 20mg daily
            ALLERGIES: Penicillin (rash), Sulfa (anaphylaxis)
            LAB RESULTS: HbA1c 7.2%, Creatinine 1.1, eGFR 70
        """
        payload = {"clinical_text": original}
        response = client.post("/api/process", json=payload)
        
        data = response.json()
        compressed = str(data["compression"]["compressed_data"]).lower()
        
        # Check that medication data is preserved
        assert "metformin" in compressed

    def test_batch_processing_multiple_records(self, client):
        """[Test] Multiple records can be processed sequentially"""
        test_cases = [
            "Patient with fever and cough, ongoing symptoms for three days",
            "Acute chest pain with EKG changes, patient in distress",
            "Follow-up visit for diabetes management with recent lab results"
        ]
        
        results = []
        for text in test_cases:
            payload = {"clinical_text": text}
            response = client.post("/api/process", json=payload)
            assert response.status_code == 200
            results.append(response.json())
        
        assert len(results) == 3
        for result in results:
            assert result["status"] == "success"

    def test_compression_consistency(self, client):
        """[Test] Same input produces consistent compression"""
        text = "Patient with acute myocardial infarction requiring immediate intervention"
        
        response1 = client.post("/api/process", json={"clinical_text": text})
        response2 = client.post("/api/process", json={"clinical_text": text})
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Compression ratios should be identical or very close
        assert abs(data1["compression"]["compression_ratio"] - data2["compression"]["compression_ratio"]) < 0.001


class TestEndToEndFlow:
    """End-to-end flow tests"""

    def test_complete_workflow(self, client):
        """[Test] Complete workflow: health -> examples -> process"""
        # 1. Check health
        health_response = client.get("/health")
        assert health_response.status_code == 200
        
        # 2. Get examples
        examples_response = client.get("/api/examples")
        assert examples_response.status_code == 200
        examples_data = examples_response.json()
        
        # 3. Process first example if available
        examples = examples_data.get("examples", [])
        if examples and len(examples) > 0:
            example_text = examples[0].get("clinical_text", "")
            if example_text:
                process_response = client.post(
                    "/api/process",
                    json={"clinical_text": example_text}
                )
                assert process_response.status_code == 200
                data = process_response.json()
                assert data["status"] == "success"

    def test_dashboard_metrics_flow(self, client):
        """[Test] Dashboard metrics collection flow"""
        # Simulate dashboard requesting metrics
        metrics_data = []
        
        for i in range(3):
            payload = {"clinical_text": f"Test case {i}: Patient symptoms and findings documented here"}
            response = client.post("/api/process", json=payload)
            if response.status_code == 200:
                data = response.json()
                metrics_data.append({
                    "ratio": data["compression"]["compression_ratio"],
                    "time": data["performance"]["total_time_ms"]
                })
        
        # Verify metrics collected
        assert len(metrics_data) == 3
        avg_ratio = sum(m["ratio"] for m in metrics_data) / len(metrics_data)
        avg_time = sum(m["time"] for m in metrics_data) / len(metrics_data)
        
        assert 0.0 < avg_ratio <= 1.0
        assert avg_time < 500


class TestLoadSimulation:
    """Tests for handling multiple concurrent requests"""

    def test_sequential_load(self, client):
        """[Perf] Handle 10 sequential requests"""
        import time
        
        start = time.time()
        
        for i in range(10):
            payload = {"clinical_text": f"Patient case number {i} with various symptoms described here"}
            response = client.post("/api/process", json=payload)
            assert response.status_code == 200
        
        total_time = time.time() - start
        avg_time = total_time / 10
        
        # Average should be under 100ms per request
        assert avg_time < 0.1, f"Average time {avg_time}s exceeds 0.1s budget"

    def test_rapid_health_checks(self, client):
        """[Perf] Handle 20 rapid health check requests"""
        import time
        
        start = time.time()
        
        for _ in range(20):
            response = client.get("/health")
            assert response.status_code == 200
        
        total_time = time.time() - start
        
        # All 20 should complete under 1 second
        assert total_time < 1.0, f"Health checks took {total_time}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=api", "--cov-report=html"])
