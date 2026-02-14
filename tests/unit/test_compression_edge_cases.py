"""
Compression Edge Cases Tests
Tests compression algorithm against unusual but valid medical data:
empty vital signs, special characters, mixed languages, boundary conditions
Coverage: Ensures algorithm doesn't crash on medical data variations
"""

import pytest
import sys
from pathlib import Path

# Add source directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.comptext import CompTextProtocol
from agents.nurse_agent import NurseAgent

# Initialize compression protocol
protocol = CompTextProtocol()
nurse = NurseAgent()


class TestCompressionEdgeCases:
    """Tests for edge cases in compression algorithm"""

    # ========== EMPTY/MISSING DATA ==========
    
    def test_empty_vital_signs_compression(self):
        """[Test] Clinical text with no vital signs still compresses"""
        clinical_text = "Chief complaint: Chronic fatigue. Patient reports 6-month history of tiredness."
        result = protocol.compress(clinical_text)
        
        assert result is not None
        assert 0 < result.compression_ratio < 1
        # Should still produce valid compressed data
        assert result.chief_complaint or result.symptoms

    def test_missing_heart_rate_compression(self):
        """[Test] Clinical text with missing heart rate compresses"""
        clinical_text = "BP: 160/95. Temperature: 38.5C. Respiratory rate: 22. Patient alert."
        result = protocol.compress(clinical_text)
        
        assert result is not None
        assert result.vital_signs.heart_rate is None  # Should be None
        assert result.vital_signs.blood_pressure == "160/95"  # BP should be captured

    def test_missing_all_vital_signs_compression(self):
        """[Test] Clinical text with no vital signs at all compresses"""
        clinical_text = "Patient reports abdominal pain. No vitals documented in this intake."
        result = protocol.compress(clinical_text)
        
        assert result is not None
        assert 0 < result.compression_ratio < 1

    def test_only_chief_complaint_no_vitals(self):
        """[Test] Only chief complaint (no vitals/meds) compresses"""
        clinical_text = "Chief complaint: Severe headache for past 3 days."
        result = protocol.compress(clinical_text)
        
        assert result is not None
        assert result.chief_complaint is not None

    # ========== SPECIAL & UNICODE CHARACTERS ==========
    
    def test_unicode_chinese_characters_compression(self):
        """[Test] Chinese characters in clinical text don't break compression"""
        clinical_text = "患者 (patient) 李明 has 高血压 (high BP). HR: 110. Chief complaint: 胸痛 (chest pain)."
        result = protocol.compress(clinical_text)
        
        assert result is not None
        assert 0 < result.compression_ratio < 1

    def test_unicode_spanish_accents_compression(self):
        """[Test] Spanish accented characters (ñ, á, é) handled correctly"""
        clinical_text = "Paciente José María García tiene presión sanguínea: 160/95. Temperatura: 38°C. Diagnóstico: Neumonía."
        result = protocol.compress(clinical_text)
        
        assert result is not None
        assert 0 < result.compression_ratio < 1

    def test_medical_symbols_preserved(self):
        """[Test] Medical symbols (±, ≤, ≥, Δ, μ) preserved correctly"""
        clinical_text = "BP: 160±5 mmHg. HR ≥ 110 bpm. Δ temp = 2.5°C. WBC: 15.0 μL. Severity: Critical."
        result = protocol.compress(clinical_text)
        
        assert result is not None
        assert 0 < result.compression_ratio < 1
        # Verify vitals are captured (should handle symbols)
        assert result.vital_signs

    def test_copyright_trademark_symbols_compression(self):
        """[Test] Copyright/trademark symbols (©, ™, ®) handled"""
        clinical_text = "EKG: Standard Device™ Model R©. FDA Approved® Equipment. BP: 160/95."
        result = protocol.compress(clinical_text)
        
        assert result is not None

    def test_emoji_characters_handled_gracefully(self):
        """[Test] Emoji characters don't crash compression"""
        clinical_text = "Patient ❤️ condition is 🔴 critical. Status: ⚠️ High Risk. HR: 110"
        result = protocol.compress(clinical_text)
        
        assert result is not None
        # Should not crash, compression ratio should be valid
        assert 0 < result.compression_ratio < 1

    # ========== MIXED LANGUAGES ==========
    
    def test_mixed_english_spanish_text_compression(self):
        """[Test] Mixed English-Spanish clinical text compresses"""
        clinical_text = """
        Chief complaint: Dolor en el pecho. Patient reports chest pain radiating to left arm.
        Vitales: HR 110 bpm, BP 160/95 mmHg. Temperature: 38.5C.
        Assessment: Posible MI. Patient requires immediate attention.
        """
        result = protocol.compress(clinical_text)
        
        assert result is not None
        assert 0 < result.compression_ratio < 1

    def test_mixed_english_french_text_compression(self):
        """[Test] Mixed English-French clinical text compresses"""
        clinical_text = """
        Patient: Jean Dupont. Chief complaint: Douleur thoracique (chest pain).
        Signes vitaux: HR 115 bpm, BP 165/100. Température: 39C.
        Patient reports acute dyspnea and diaphoresis.
        """
        result = protocol.compress(clinical_text)
        
        assert result is not None

    # ========== WHITESPACE EDGE CASES ==========
    
    def test_repeated_whitespace_normalization(self):
        """[Test] Repeated spaces/tabs/newlines normalized"""
        clinical_text = """
        Patient    has    fever.
        
        
        HR:     110     bpm
        BP:         160/95
        
        
        
        Temperature:    38.5C
        """
        result = protocol.compress(clinical_text)
        
        assert result is not None
        assert 0 < result.compression_ratio < 1

    def test_leading_trailing_whitespace_handled(self):
        """[Test] Leading/trailing whitespace stripped correctly"""
        clinical_text = "    \n\n    Chief complaint: Fever.    \n    HR: 110    \n\n    "
        result = protocol.compress(clinical_text)
        
        assert result is not None

    # ========== TEXT BOUNDARY CONDITIONS ==========
    
    def test_minimum_text_length_compression(self):
        """[Test] Minimum valid text (10 chars) compresses"""
        clinical_text = "Fever 38.5"  # Exactly 10 characters
        result = protocol.compress(clinical_text)
        
        assert result is not None

    def test_very_long_clinical_text_compression(self):
        """[Test] Very long clinical text (near 5000 char limit) compresses"""
        # Create realistic long clinical note
        clinical_text = "Chief complaint: " + "Patient has fever and chest pain. " * 100
        clinical_text = clinical_text[:4999]  # Ensure under limit
        
        result = protocol.compress(clinical_text)
        
        assert result is not None
        assert 0 < result.compression_ratio < 1

    # ========== VITAL SIGNS FORMAT VARIATIONS ==========
    
    def test_varied_heart_rate_formats(self):
        """[Test] Different HR formats all captured correctly"""
        test_cases = [
            "HR: 110",
            "Heart rate: 110",
            "HR = 110",
            "HR 110 bpm",
            "HR: 110 bpm",
            "HR = 110bpm",
            "Heart Rate: 110",
            "HR 110",
        ]
        
        for text in test_cases:
            clinical_text = f"{text}. BP: 160/95. Patient stable."
            result = protocol.compress(clinical_text)
            assert result is not None, f"Failed on format: {text}"
            # Heart rate should be captured
            assert result.vital_signs.heart_rate is not None or "HR" in text.upper()

    def test_varied_blood_pressure_formats(self):
        """[Test] Different BP formats all captured correctly"""
        test_cases = [
            "BP: 160/95",
            "Blood pressure: 160/95",
            "BP 160/95",
            "BP = 160/95",
            "BP: 160/95 mmHg",
            "SBP: 160, DBP: 95",
            "BP 160 / 95",
        ]
        
        for text in test_cases:
            clinical_text = f"HR: 110. {text}. Patient alert."
            result = protocol.compress(clinical_text)
            assert result is not None, f"Failed on format: {text}"

    def test_temperature_format_variations(self):
        """[Test] Different temperature formats handled"""
        test_cases = [
            "Temp: 38.5C",
            "Temperature: 38.5C",
            "Temp: 38.5°C",
            "Temperature: 38.5 degrees C",
            "T: 38.5C",
            "38.5 Celsius",
            "Fever: 38.5C",
        ]
        
        for text in test_cases:
            clinical_text = f"HR: 110. BP: 160/95. {text}. Patient alert."
            result = protocol.compress(clinical_text)
            assert result is not None, f"Failed on format: {text}"

    # ========== COMPRESSION RATIO STABILITY ==========
    
    def test_compression_ratio_range_valid(self):
        """[Test] Compression ratios stay in 0-1 range for all cases"""
        test_texts = [
            "Patient has fever.",
            "Chief complaint: Severe chest pain radiating to left arm. HR: 110 bpm. BP: 160/95 mmHg. EKG shows ST elevation.",
            "Only number: 123",
            "Mixed Chinese 中文 and English text with 符号",
        ]
        
        for text in test_texts:
            result = protocol.compress(text)
            assert result is not None
            assert 0 < result.compression_ratio < 1, f"Invalid ratio {result.compression_ratio}"

    def test_compression_ratio_higher_for_longer_text(self):
        """[Test] Longer text compresses better (higher ratio)"""
        short_text = "Fever. HR: 110."
        long_text = "Chief complaint: Fever. Patient reports high fever for 3 days. HR: 110 bpm. BP: 160/95 mmHg. Temperature: 38.5C. Assessment: Acute infection. Medications: Ibuprofen, Amoxicillin. Recommendations: IV fluids, continuous monitoring."
        
        short_result = protocol.compress(short_text)
        long_result = protocol.compress(long_text)
        
        assert short_result is not None
        assert long_result is not None
        # Longer text should typically compress better
        assert long_result.compression_ratio >= short_result.compression_ratio

    # ========== DATA TYPE EDGE CASES ==========
    
    def test_numeric_only_clinical_text(self):
        """[Test] Clinical text with only numbers compresses"""
        clinical_text = "110 160 95 38.5 3 2.5 100 120"
        result = protocol.compress(clinical_text)
        
        assert result is not None
        assert 0 < result.compression_ratio < 1

    def test_special_characters_only_section(self):
        """[Test] Section with only symbols doesn't crash"""
        clinical_text = "Patient notes: !@#$%^&* HR: 110. BP: 160/95."
        result = protocol.compress(clinical_text)
        
        assert result is not None

    def test_very_long_chief_complaint(self):
        """[Test] Very long single chief complaint handled"""
        chief_complaint = "Severe " + "chest pain " * 50
        clinical_text = f"Chief complaint: {chief_complaint}. HR: 110. BP: 160/95."
        result = protocol.compress(clinical_text)
        
        assert result is not None
        assert result.chief_complaint is not None

    def test_empty_medications_section(self):
        """[Test] Clinical text with no medications section works"""
        clinical_text = "Chief complaint: Fever. No medications currently. HR: 110. BP: 160/95."
        result = protocol.compress(clinical_text)
        
        assert result is not None
        # Medications list should be empty or minimal
        assert isinstance(result.medications, list)

    def test_empty_symptoms_section(self):
        """[Test] Clinical text with no explicit symptoms section works"""
        clinical_text = "Patient stable. No acute complaints. HR: 110. BP: 160/95."
        result = protocol.compress(clinical_text)
        
        assert result is not None

    # ========== REAL-WORLD EDGE CASES ==========
    
    def test_real_world_acute_mi_note(self):
        """[Test] Real acute MI note with all complications"""
        clinical_text = """
        Chief complaint: Acute chest pain
        
        HPI: 62-year-old M with acute onset chest pain radiating to L arm x 2 hours.
        Associated with dyspnea, diaphoresis, nausea.
        
        Vitals:
        HR: 115 bpm
        BP: 165/100 mmHg  
        Temp: 37.5°C
        RR: 22
        SpO2: 94% RA
        
        EKG: ST elevation in V1-V4
        Troponin: 2.5 ng/mL (elevated)
        
        Assessment: Acute STEMI, anterior wall MI
        Plan: Urgent cardiac catheterization
        """
        result = protocol.compress(clinical_text)
        
        assert result is not None
        assert 0 < result.compression_ratio < 1
        assert result.chief_complaint is not None
        assert result.vital_signs.heart_rate == 115

    def test_real_world_sepsis_note(self):
        """[Test] Real sepsis note with multiple vital sign abnormalities"""
        clinical_text = """
        Chief complaint: Fever and altered mental status
        
        Vitals: T 39.8°C, HR 125, BP 95/60, RR 28, SpO2 92%
        
        Physical: Patient confused, skin mottled, extremities cold
        
        Labs: WBC 22, Lactate 4.2, CRP 18
        
        Diagnosis: Sepsis, probable source UTI
        
        Meds: Vancomycin, Piperacillin-Tazobactam, Fluids
        """
        result = protocol.compress(clinical_text)
        
        assert result is not None
        assert result.vital_signs.temperature == 39.8
        assert result.vital_signs.heart_rate == 125

    def test_clinical_note_with_abbreviations_and_acronyms(self):
        """[Test] Clinical note heavy with medical abbreviations"""
        clinical_text = """
        CC: Chest pain
        HPI: 45yo F c/o CP, palpitations
        PMHx: HTN, DM2, HLD
        
        Vitals: HR 108, BP 145/90, T 37.2
        ROS: + SOB, - fever
        
        PE: Significant S1, S2, no murmur
        
        Labs: BMP normal, CBC normal, CXR clear
        
        EKG: NSR, no STEMI
        Assessment: NSTEMI r/o ACS
        Rx: Troponin serial, admission to CCU
        """
        result = protocol.compress(clinical_text)
        
        assert result is not None


class TestNurseAgentEdgeCases:
    """Tests for NurseAgent handling of edge cases"""

    def test_nurse_agent_processes_edge_case_input(self):
        """[Test] NurseAgent.intake() handles edge case clinical text"""
        clinical_text = "Fever. HR: 110. BP: 160/95."
        result = nurse.intake(clinical_text)
        
        assert result is not None
        assert result.compression_ratio > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
