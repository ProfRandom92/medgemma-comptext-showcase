"""Tests for FHIR export from PatientState."""

import json

import pytest

from src.core.models import PatientState, Vitals


class TestPatientStateToFhir:
    """Verify that to_fhir() produces a valid FHIR Bundle structure."""

    def test_bundle_structure(self):
        state = PatientState(
            chief_complaint="chest pain",
            vitals=Vitals(hr=110, bp="130/85", temp=39.2),
        )
        bundle = state.to_fhir()

        assert bundle["resourceType"] == "Bundle"
        assert bundle["type"] == "collection"
        assert "id" in bundle
        assert "timestamp" in bundle
        assert isinstance(bundle["entry"], list)

    def test_chief_complaint_observation(self):
        state = PatientState(chief_complaint="headache")
        bundle = state.to_fhir()
        entries = bundle["entry"]

        complaint_obs = [
            e for e in entries
            if e["resource"]["code"]["coding"][0]["code"] == "8661-1"
        ]
        assert len(complaint_obs) == 1
        assert complaint_obs[0]["resource"]["valueString"] == "headache"
        assert complaint_obs[0]["resource"]["resourceType"] == "Observation"
        assert complaint_obs[0]["resource"]["status"] == "final"

    def test_heart_rate_observation(self):
        state = PatientState(vitals=Vitals(hr=72))
        bundle = state.to_fhir()
        entries = bundle["entry"]

        hr_obs = [
            e for e in entries
            if e["resource"]["code"]["coding"][0]["code"] == "8867-4"
        ]
        assert len(hr_obs) == 1
        assert hr_obs[0]["resource"]["valueQuantity"]["value"] == 72
        assert hr_obs[0]["resource"]["valueQuantity"]["unit"] == "beats/minute"

    def test_blood_pressure_observation(self):
        state = PatientState(vitals=Vitals(bp="120/80"))
        bundle = state.to_fhir()
        entries = bundle["entry"]

        bp_obs = [
            e for e in entries
            if e["resource"]["code"]["coding"][0]["code"] == "85354-9"
        ]
        assert len(bp_obs) == 1
        components = bp_obs[0]["resource"]["component"]
        assert len(components) == 2

        systolic = components[0]
        assert systolic["valueQuantity"]["value"] == 120
        assert systolic["code"]["coding"][0]["code"] == "8480-6"

        diastolic = components[1]
        assert diastolic["valueQuantity"]["value"] == 80
        assert diastolic["code"]["coding"][0]["code"] == "8462-4"

    def test_temperature_observation(self):
        state = PatientState(vitals=Vitals(temp=38.5))
        bundle = state.to_fhir()
        entries = bundle["entry"]

        temp_obs = [
            e for e in entries
            if e["resource"]["code"]["coding"][0]["code"] == "8310-5"
        ]
        assert len(temp_obs) == 1
        assert temp_obs[0]["resource"]["valueQuantity"]["value"] == 38.5
        assert temp_obs[0]["resource"]["valueQuantity"]["unit"] == "degrees Celsius"

    def test_empty_state_produces_empty_entries(self):
        state = PatientState()
        bundle = state.to_fhir()

        assert bundle["resourceType"] == "Bundle"
        assert bundle["entry"] == []

    def test_full_state_entry_count(self):
        state = PatientState(
            chief_complaint="fever",
            vitals=Vitals(hr=100, bp="140/90", temp=39.0),
        )
        bundle = state.to_fhir()
        # chief_complaint + HR + BP + temp = 4 entries
        assert len(bundle["entry"]) == 4

    def test_fhir_json_serializable(self):
        state = PatientState(
            chief_complaint="cough",
            vitals=Vitals(hr=88, bp="118/76", temp=37.2),
        )
        bundle = state.to_fhir()
        # Must be JSON-serializable without errors
        serialized = json.dumps(bundle)
        assert isinstance(serialized, str)
        parsed = json.loads(serialized)
        assert parsed["resourceType"] == "Bundle"
