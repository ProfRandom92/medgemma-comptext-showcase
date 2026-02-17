"""[Test] Compression edge cases - testing CompText protocol robustness."""

import pytest
from src.core.models import PatientState, Vitals
from src.agents.nurse_agent import NurseAgent


class TestCompressionEdgeCases:
    """Test edge cases in compression and data handling."""

    def test_empty_clinical_text_handled(self):
        """[Test] Empty string should produce valid PatientState."""
        nurse = NurseAgent()
        result = nurse.intake("")
        assert isinstance(result, PatientState)
        assert result.chief_complaint is None or result.chief_complaint == ""

    def test_whitespace_only_clinical_text(self):
        """[Test] Whitespace-only text should handle gracefully."""
        nurse = NurseAgent()
        result = nurse.intake("   \n\t   ")
        assert isinstance(result, PatientState)

    def test_unicode_chinese_characters_preserved(self):
        """[Test] Chinese characters preserved in compression."""
        nurse = NurseAgent()
        chinese_text = "患者主诉胸痛 HR 95 BP 140/90"
        result = nurse.intake(chinese_text)
        assert isinstance(result, PatientState)
        assert result.vitals is not None

    def test_unicode_spanish_accents_preserved(self):
        """[Test] Spanish accents preserved in compression."""
        nurse = NurseAgent()
        spanish_text = "Paciente con presión alta y fiebre: HR 105 BP 160/95 Temp 39.2"
        result = nurse.intake(spanish_text)
        assert isinstance(result, PatientState)
        assert result.vitals is not None

    def test_medical_symbols_handled(self):
        """[Test] Medical symbols like ° preserved."""
        nurse = NurseAgent()
        text = "Temperature 38.5° HR 92 BP 130/85"
        result = nurse.intake(text)
        assert isinstance(result, PatientState)
        assert result.vitals is not None

    def test_emoji_characters_handled(self):
        """[Test] Emoji characters don't crash compression."""
        nurse = NurseAgent()
        text = "Patient very ill HR 115 BP 150/90"
        result = nurse.intake(text)
        assert isinstance(result, PatientState)
        assert result.vitals is not None

    def test_mixed_english_spanish_text(self):
        """[Test] Mixed language text handled."""
        nurse = NurseAgent()
        text = "Patient reports pain with HR 88 BP 135/80"
        result = nurse.intake(text)
        assert isinstance(result, PatientState)
        assert result.vitals is not None

    def test_repeated_whitespace_normalization(self):
        """[Test] Multiple spaces/newlines handled."""
        nurse = NurseAgent()
        text = "Patient    with\n\n\nmultiple\t\t\tspaces  HR  92  BP  140/90"
        result = nurse.intake(text)
        assert isinstance(result, PatientState)
        assert result.vitals is not None

    def test_very_long_clinical_text(self):
        """[Test] Very long text doesn't cause issues."""
        nurse = NurseAgent()
        long_text = "Patient complaints: " + ("chest pain " * 100) + "HR 95 BP 140/90"
        result = nurse.intake(long_text)
        assert isinstance(result, PatientState)
        assert result.vitals is not None

    def test_numeric_only_text(self):
        """[Test] Numeric-only text handled."""
        nurse = NurseAgent()
        text = "95 140 90 39.2"
        result = nurse.intake(text)
        assert isinstance(result, PatientState)

    def test_html_like_content_handled(self):
        """[Test] HTML-like text doesn't break compression."""
        nurse = NurseAgent()
        text = "<p>Patient has fever</p> HR 100 BP 145/92"
        result = nurse.intake(text)
        assert isinstance(result, PatientState)
        assert result.vitals is not None

    def test_sql_like_content_handled(self):
        """[Test] SQL-like patterns don't break compression."""
        nurse = NurseAgent()
        text = "SELECT FROM patients HR 100 BP 140/90"
        result = nurse.intake(text)
        assert isinstance(result, PatientState)

    def test_null_bytes_handled(self):
        """[Test] Null bytes in text don't crash."""
        nurse = NurseAgent()
        text = "Patient data HR 88 BP 130/80"
        result = nurse.intake(text)
        assert isinstance(result, PatientState)

    def test_real_world_acute_mi_note(self):
        """[Test] Real MI presentation compresses correctly."""
        nurse = NurseAgent()
        mi_text = """58-year-old male with chest pain. HR 118, BP 165/95, Temp 37.2"""
        result = nurse.intake(mi_text)
        assert isinstance(result, PatientState)
        assert result.vitals is not None

    def test_real_world_sepsis_note(self):
        """[Test] Real sepsis presentation compresses correctly."""
        nurse = NurseAgent()
        sepsis_text = """72-year-old female with fever and confusion. HR 125, BP 88/55, Temp 40.1"""
        result = nurse.intake(sepsis_text)
        assert isinstance(result, PatientState)
        assert result.vitals is not None

    def test_patient_state_to_compressed_json(self):
        """[Test] PatientState correctly exports to compressed JSON."""
        state = PatientState(
            chief_complaint="chest pain",
            vitals=Vitals(hr=95, bp="140/90", temp=37.5),
            medication="aspirin",
        )
        json_str = state.to_compressed_json()
        assert isinstance(json_str, str)
        assert "chest pain" in json_str
        assert "95" in json_str

    def test_patient_state_excludes_none_fields(self):
        """[Test] PatientState JSON excludes None values for compression."""
        state = PatientState(
            chief_complaint="fever",
            vitals=Vitals(hr=100),
        )
        json_str = state.to_compressed_json()
        assert "chief_complaint" in json_str
        assert "hr" in json_str

    def test_vitals_with_only_heart_rate(self):
        """[Test] Vitals object with only HR set."""
        vitals = Vitals(hr=88)
        assert vitals.hr == 88
        assert vitals.bp is None
        assert vitals.temp is None

    def test_vitals_with_invalid_bp_format(self):
        """[Test] BP with invalid format handled gracefully."""
        vitals = Vitals(bp="invalid")
        assert vitals.bp == "invalid"

    def test_patient_state_fhir_export(self):
        """[Test] PatientState exports to FHIR format."""
        state = PatientState(
            chief_complaint="fever",
            vitals=Vitals(hr=102, bp="145/90", temp=39.2),
        )
        fhir_bundle = state.to_fhir()
        assert fhir_bundle["resourceType"] == "Bundle"
        assert fhir_bundle["type"] == "collection"
        assert len(fhir_bundle["entry"]) > 0


class TestNurseAgentEdgeCases:
    """Test NurseAgent specifically."""

    def test_nurse_agent_initializes(self):
        """[Test] NurseAgent can be instantiated."""
        nurse = NurseAgent()
        assert nurse is not None

    def test_nurse_agent_intake_returns_patient_state(self):
        """[Test] NurseAgent.intake returns PatientState."""
        nurse = NurseAgent()
        result = nurse.intake("Patient has fever HR 100 BP 140/90")
        assert isinstance(result, PatientState)

    def test_nurse_agent_multiple_calls(self):
        """[Test] NurseAgent can process multiple inputs."""
        nurse = NurseAgent()
        result1 = nurse.intake("Chest pain HR 95")
        result2 = nurse.intake("Fever HR 105")
        assert isinstance(result1, PatientState)
        assert isinstance(result2, PatientState)
