"""Tests for CompTextProtocol, NurseAgent, DoctorAgent, and Codex system."""

import json

import pytest

from src.core.comptext import CompTextProtocol
from src.core.codex import (
    CardiologyCodex,
    ClinicalModule,
    CodexRouter,
    RespiratoryCodex,
)
from src.core.models import PatientState, Vitals
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

        assert result.chief_complaint == "chest pain"
        assert result.vitals.hr == 110
        assert result.vitals.bp == "130/85"
        assert result.vitals.temp == 39.2
        assert result.medication == "aspirin"

    def test_compress_missing_fields_are_none(self):
        raw = "Patient says they feel fine."
        result = self.protocol.compress(raw)

        assert result.vitals.hr is None
        assert result.vitals.bp is None
        assert result.vitals.temp is None

    def test_compress_returns_patient_state(self):
        result = self.protocol.compress("HR 80")
        assert isinstance(result, PatientState)
        assert result.vitals is not None

    def test_compress_with_fever_keyword(self):
        raw = "Patient has fever 38.5C and HR 100."
        result = self.protocol.compress(raw)
        assert result.vitals.temp == 38.5
        assert result.vitals.hr == 100


# ---------------------------------------------------------------------------
# NurseAgent
# ---------------------------------------------------------------------------

class TestNurseAgent:
    def test_intake_returns_compressed_state(self):
        nurse = NurseAgent()
        state = nurse.intake("Chief complaint: headache. HR 72, BP 120/80.")

        assert state.chief_complaint == "headache"
        assert state.vitals.hr == 72
        assert state.vitals.bp == "120/80"


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


# ---------------------------------------------------------------------------
# Codex System
# ---------------------------------------------------------------------------

class TestCodexRouter:
    def setup_method(self):
        self.router = CodexRouter()

    def test_routes_chest_pain_to_cardiology(self):
        module = self.router.route("Patient presents with chest pain.")
        assert module is not None
        assert module.name == "Cardiology"

    def test_routes_heart_to_cardiology(self):
        module = self.router.route("Heart rate elevated, palpitations noted.")
        assert module is not None
        assert module.name == "Cardiology"

    def test_routes_asthma_to_respiratory(self):
        module = self.router.route("Patient has asthma, wheezing on exam.")
        assert module is not None
        assert module.name == "Respiratory"

    def test_routes_breath_to_respiratory(self):
        module = self.router.route("Shortness of breath since yesterday.")
        assert module is not None
        assert module.name == "Respiratory"

    def test_returns_none_for_unmatched(self):
        module = self.router.route("Patient has a headache.")
        assert module is None


class TestCardiologyCodex:
    def setup_method(self):
        self.codex = CardiologyCodex()

    def test_extracts_radiation(self):
        result = self.codex.extract("Chest pain radiating to left arm.")
        assert result["radiation"] is not None
        assert "left arm" in result["radiation"]

    def test_extracts_pain_quality(self):
        result = self.codex.extract("Chest pain is sharp and constant.")
        assert result["pain_quality"] == "sharp"

    def test_returns_none_when_no_match(self):
        result = self.codex.extract("Heart rate elevated.")
        assert result["radiation"] is None
        assert result["pain_quality"] is None


class TestRespiratoryCodex:
    def setup_method(self):
        self.codex = RespiratoryCodex()

    def test_extracts_triggers(self):
        result = self.codex.extract("Asthma triggered by dust exposure.")
        assert result["triggers"] is not None
        assert "dust" in result["triggers"]

    def test_extracts_breath_sounds(self):
        result = self.codex.extract("Breath sounds: diminished on left side.")
        assert result["breath_sounds"] == "diminished"

    def test_returns_none_when_no_match(self):
        result = self.codex.extract("Patient has wheezing.")
        assert result["triggers"] is None
        assert result["breath_sounds"] is None


class TestCompTextProtocolMeta:
    def setup_method(self):
        self.protocol = CompTextProtocol()

    def test_compress_includes_meta_for_cardiology(self):
        raw = "Chief complaint: chest pain. HR 110."
        result = self.protocol.compress(raw)
        assert result.meta is not None
        assert result.meta["active_protocol"] == CardiologyCodex().protocol_label

    def test_compress_includes_meta_for_respiratory(self):
        raw = "Patient has asthma. HR 90."
        result = self.protocol.compress(raw)
        assert result.meta is not None
        assert result.meta["active_protocol"] == RespiratoryCodex().protocol_label

    def test_compress_includes_general_when_no_match(self):
        raw = "Patient has a headache. HR 72."
        result = self.protocol.compress(raw)
        assert result.meta["active_protocol"] == "General"

    def test_compress_includes_specialist_data(self):
        raw = "Chest pain radiating to left arm. HR 110."
        result = self.protocol.compress(raw)
        assert result.specialist_data is not None
        assert "radiation" in result.specialist_data


# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------

class TestVitalsModel:
    def test_vitals_defaults_to_none(self):
        v = Vitals()
        assert v.hr is None
        assert v.bp is None
        assert v.temp is None

    def test_vitals_with_values(self):
        v = Vitals(hr=80, bp="120/80", temp=37.0)
        assert v.hr == 80
        assert v.bp == "120/80"
        assert v.temp == 37.0


class TestPatientStateModel:
    def test_to_compressed_json_excludes_none(self):
        state = PatientState(
            chief_complaint="headache",
            vitals=Vitals(hr=72),
            meta={"active_protocol": "General"},
        )
        compressed = state.to_compressed_json()
        parsed = json.loads(compressed)

        assert "chief_complaint" in parsed
        assert parsed["vitals"]["hr"] == 72
        # bp and temp are None so should be excluded
        assert "bp" not in parsed["vitals"]
        assert "temp" not in parsed["vitals"]
        # medication is None so should be excluded
        assert "medication" not in parsed

    def test_to_compressed_json_includes_meta(self):
        state = PatientState(
            meta={"active_protocol": "🫀 Cardiology Protocol"},
        )
        compressed = state.to_compressed_json()
        parsed = json.loads(compressed)
        assert parsed["meta"]["active_protocol"] == "🫀 Cardiology Protocol"

    def test_model_dump_returns_dict(self):
        state = PatientState(
            chief_complaint="cough",
            vitals=Vitals(hr=90),
        )
        d = state.model_dump()
        assert isinstance(d, dict)
        assert d["chief_complaint"] == "cough"
        assert d["vitals"]["hr"] == 90
