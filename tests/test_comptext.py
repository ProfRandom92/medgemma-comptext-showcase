"""Tests for CompTextProtocol, NurseAgent, and DoctorAgent."""

import pytest

from src.core.comptext import CompTextProtocol
from src.agents.nurse_agent import NurseAgent
from src.agents.doctor_agent import DoctorAgent


# ---------------------------------------------------------------------------
# CompTextProtocol
# ---------------------------------------------------------------------------

class TestCompTextProtocol:
    def setup_method(self):
        self.protocol = CompTextProtocol()

    def test_compress_extracts_all_fields(self):
        raw = (
            "Chief complaint: chest pain. HR 110, BP 130/85, "
            "Temp 39.2C. Medication: aspirin."
        )
        result = self.protocol.compress(raw)

        assert result["chief_complaint"] == "chest pain"
        assert result["vitals"]["hr"] == 110
        assert result["vitals"]["bp"] == "130/85"
        assert result["vitals"]["temp"] == 39.2
        assert result["medication"] == "aspirin"

    def test_compress_missing_fields_are_none(self):
        raw = "Patient says they feel fine."
        result = self.protocol.compress(raw)

        assert result["vitals"]["hr"] is None
        assert result["vitals"]["bp"] is None
        assert result["vitals"]["temp"] is None

    def test_compress_returns_dict(self):
        result = self.protocol.compress("HR 80")
        assert isinstance(result, dict)
        assert "vitals" in result

    def test_compress_with_fever_keyword(self):
        raw = "Patient has fever 38.5C and HR 100."
        result = self.protocol.compress(raw)
        assert result["vitals"]["temp"] == 38.5
        assert result["vitals"]["hr"] == 100


# ---------------------------------------------------------------------------
# NurseAgent
# ---------------------------------------------------------------------------

class TestNurseAgent:
    def test_intake_returns_compressed_state(self):
        nurse = NurseAgent()
        state = nurse.intake("Chief complaint: headache. HR 72, BP 120/80.")

        assert state["chief_complaint"] == "headache"
        assert state["vitals"]["hr"] == 72
        assert state["vitals"]["bp"] == "120/80"


# ---------------------------------------------------------------------------
# DoctorAgent
# ---------------------------------------------------------------------------

class TestDoctorAgent:
    def test_diagnose_with_elevated_vitals(self):
        doctor = DoctorAgent()
        state = {
            "chief_complaint": "chest pain",
            "vitals": {"hr": 120, "bp": "150/95", "temp": 39.0},
            "medication": "aspirin",
        }
        result = doctor.diagnose(state)

        assert "elevated HR" in result
        assert "fever" in result
        assert "hypertension" in result
        assert "aspirin" in result

    def test_diagnose_normal_vitals(self):
        doctor = DoctorAgent()
        state = {
            "chief_complaint": "routine checkup",
            "vitals": {"hr": 72, "bp": "120/80", "temp": 36.6},
            "medication": None,
        }
        result = doctor.diagnose(state)

        assert "within normal limits" in result.lower() or "routine follow-up" in result.lower()

    def test_diagnose_empty_state(self):
        doctor = DoctorAgent()
        result = doctor.diagnose({})

        assert isinstance(result, str)
        assert len(result) > 0
