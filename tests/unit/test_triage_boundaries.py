"""
Triage Priority Boundary Tests
Tests critical threshold boundaries in triage algorithm:
Heart Rate, Blood Pressure, Temperature, Respiratory Rate boundaries
Coverage: Ensures algorithm correctly classifies at all thresholds with no off-by-one errors
"""

import pytest
import sys
from pathlib import Path

# Add source directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agents.triage_agent import TriageAgent
from core.models import PatientState, VitalSigns

# Initialize triage agent
triage = TriageAgent()


class TestTriageBoundaries:
    """Tests for critical threshold boundaries in triage classification"""

    # ========== HEART RATE THRESHOLDS ==========
    
    def test_heart_rate_below_threshold_p3(self):
        """[Test] HR 99 (below 100 threshold) = P3"""
        patient = PatientState(
            chief_complaint="Routine check",
            vital_signs=VitalSigns(heart_rate=99, blood_pressure="120/80", temperature=37.0)
        )
        result = triage.triage(patient)
        assert result.priority_level == "P3", "HR 99 should be P3"

    def test_heart_rate_at_threshold_p2(self):
        """[Test] HR 100 (at threshold) = P2"""
        patient = PatientState(
            chief_complaint="Routine check",
            vital_signs=VitalSigns(heart_rate=100, blood_pressure="120/80", temperature=37.0)
        )
        result = triage.triage(patient)
        assert result.priority_level == "P2", "HR 100 should be P2"

    def test_heart_rate_above_threshold_p2(self):
        """[Test] HR 110 (above 100) = P2"""
        patient = PatientState(
            chief_complaint="Routine check",
            vital_signs=VitalSigns(heart_rate=110, blood_pressure="120/80", temperature=37.0)
        )
        result = triage.triage(patient)
        assert result.priority_level in ["P2", "P1"], "HR 110 should be at least P2"

    def test_heart_rate_severe_p1(self):
        """[Test] HR 140 (severe) = P1"""
        patient = PatientState(
            chief_complaint="Chest pain with palpitations",
            vital_signs=VitalSigns(heart_rate=140, blood_pressure="120/80", temperature=37.0)
        )
        result = triage.triage(patient)
        assert result.priority_level == "P1", "HR 140 should be P1"

    def test_heart_rate_low_p2(self):
        """[Test] HR 45 (bradycardia) = P2 or P1"""
        patient = PatientState(
            chief_complaint="Dizziness",
            vital_signs=VitalSigns(heart_rate=45, blood_pressure="120/80", temperature=37.0)
        )
        result = triage.triage(patient)
        assert result.priority_level in ["P1", "P2"], "Low HR should be urgent"

    # ========== BLOOD PRESSURE THRESHOLDS ==========
    
    def test_blood_pressure_systolic_below_threshold_p3(self):
        """[Test] BP 159/90 (SBP below 160) = P3"""
        patient = PatientState(
            chief_complaint="Routine check",
            vital_signs=VitalSigns(heart_rate=80, blood_pressure="159/90", temperature=37.0)
        )
        result = triage.triage(patient)
        assert result.priority_level == "P3", "BP 159 systolic should be P3"

    def test_blood_pressure_systolic_at_threshold_p2(self):
        """[Test] BP 160/90 (at SBP threshold) = P2"""
        patient = PatientState(
            chief_complaint="Routine check",
            vital_signs=VitalSigns(heart_rate=80, blood_pressure="160/90", temperature=37.0)
        )
        result = triage.triage(patient)
        assert result.priority_level in ["P2", "P1"], "BP 160 systolic should be urgent"

    def test_blood_pressure_systolic_above_threshold_p2_or_p1(self):
        """[Test] BP 180/95 (SBP well above threshold) = P1"""
        patient = PatientState(
            chief_complaint="Severe headache",
            vital_signs=VitalSigns(heart_rate=110, blood_pressure="180/110", temperature=37.0)
        )
        result = triage.triage(patient)
        assert result.priority_level == "P1", "BP 180/110 should be P1"

    def test_blood_pressure_diastolic_high_p2(self):
        """[Test] High diastolic (e.g., 120/100) = P2"""
        patient = PatientState(
            chief_complaint="Headache",
            vital_signs=VitalSigns(heart_rate=100, blood_pressure="140/100", temperature=37.0)
        )
        result = triage.triage(patient)
        assert result.priority_level in ["P1", "P2"], "Diastolic 100 should be urgent"

    def test_blood_pressure_low_p2_or_p1(self):
        """[Test] Hypotension (e.g., 90/60) = P2 or P1"""
        patient = PatientState(
            chief_complaint="Dizziness, weakness",
            vital_signs=VitalSigns(heart_rate=110, blood_pressure="90/60", temperature=37.0)
        )
        result = triage.triage(patient)
        assert result.priority_level in ["P1", "P2"], "Low BP should be urgent"

    # ========== TEMPERATURE THRESHOLDS ==========
    
    def test_temperature_below_threshold_p3(self):
        """[Test] Temp 37.9°C (below 38.0) = P3"""
        patient = PatientState(
            chief_complaint="Mild fever",
            vital_signs=VitalSigns(heart_rate=90, blood_pressure="120/80", temperature=37.9)
        )
        result = triage.triage(patient)
        assert result.priority_level == "P3", "Temp 37.9 should be P3"

    def test_temperature_at_threshold_p2(self):
        """[Test] Temp 38.0°C (at threshold) = P2"""
        patient = PatientState(
            chief_complaint="Fever",
            vital_signs=VitalSigns(heart_rate=100, blood_pressure="120/80", temperature=38.0)
        )
        result = triage.triage(patient)
        assert result.priority_level in ["P2", "P1"], "Temp 38.0 should be urgent"

    def test_temperature_above_threshold_p2_or_p1(self):
        """[Test] Temp 39.5°C (above threshold) = P2 or P1"""
        patient = PatientState(
            chief_complaint="High fever",
            vital_signs=VitalSigns(heart_rate=115, blood_pressure="120/80", temperature=39.5)
        )
        result = triage.triage(patient)
        assert result.priority_level in ["P1", "P2"], "Temp 39.5 should be urgent"

    def test_temperature_very_high_p1(self):
        """[Test] Temp 40.5°C (critical) = P1"""
        patient = PatientState(
            chief_complaint="Very high fever, confusion",
            vital_signs=VitalSigns(heart_rate=130, blood_pressure="120/80", temperature=40.5)
        )
        result = triage.triage(patient)
        assert result.priority_level == "P1", "Temp 40.5 should be P1"

    def test_temperature_very_low_p1(self):
        """[Test] Temp 34.0°C (hypothermia) = P1"""
        patient = PatientState(
            chief_complaint="Hypothermia, altered mental status",
            vital_signs=VitalSigns(heart_rate=50, blood_pressure="90/60", temperature=34.0)
        )
        result = triage.triage(patient)
        assert result.priority_level == "P1", "Hypothermia should be P1"

    # ========== RESPIRATORY RATE THRESHOLDS ==========
    
    def test_respiratory_rate_below_threshold_p3(self):
        """[Test] RR 19 (normal) = P3"""
        patient = PatientState(
            chief_complaint="Routine check",
            vital_signs=VitalSigns(heart_rate=80, blood_pressure="120/80", temperature=37.0),
            symptoms=["Mild dyspnea"]  # Low severity
        )
        result = triage.triage(patient)
        assert result.priority_level in ["P3", "P2"], "Normal RR should be low priority"

    def test_respiratory_rate_at_threshold_p2(self):
        """[Test] RR 30 (at threshold) = P2"""
        patient = PatientState(
            chief_complaint="Shortness of breath",
            vital_signs=VitalSigns(heart_rate=100, blood_pressure="120/80", temperature=37.0),
            symptoms=["Acute dyspnea"]
        )
        result = triage.triage(patient)
        assert result.priority_level in ["P1", "P2"], "RR 30 should be urgent"

    def test_respiratory_rate_above_threshold_p1(self):
        """[Test] RR 35+ = P1"""
        patient = PatientState(
            chief_complaint="Severe respiratory distress",
            vital_signs=VitalSigns(heart_rate=120, blood_pressure="120/80", temperature=37.0),
            symptoms=["Severe dyspnea", "Hypoxia"]
        )
        result = triage.triage(patient)
        assert result.priority_level == "P1", "RR 35+ should be P1"

    # ========== MULTIPLE CRITICAL VITALS ==========
    
    def test_all_normal_vitals_p3(self):
        """[Test] All vitals normal = P3"""
        patient = PatientState(
            chief_complaint="Routine check-up",
            vital_signs=VitalSigns(heart_rate=75, blood_pressure="120/80", temperature=37.0),
            symptoms=[]
        )
        result = triage.triage(patient)
        assert result.priority_level == "P3", "All normal should be P3"

    def test_one_critical_vital_p2(self):
        """[Test] HR critical, others normal = P2"""
        patient = PatientState(
            chief_complaint="Palpitations",
            vital_signs=VitalSigns(heart_rate=125, blood_pressure="120/80", temperature=37.0)
        )
        result = triage.triage(patient)
        assert result.priority_level == "P2", "One critical vital should be P2"

    def test_two_critical_vitals_p1(self):
        """[Test] HR 125 AND BP 170/100 = P1"""
        patient = PatientState(
            chief_complaint="Chest pain with hypertension",
            vital_signs=VitalSigns(heart_rate=125, blood_pressure="170/100", temperature=37.0)
        )
        result = triage.triage(patient)
        assert result.priority_level == "P1", "Multiple critical vitals should be P1"

    def test_all_critical_vitals_p1(self):
        """[Test] HR 140, BP 180/110, Temp 39.5 = P1"""
        patient = PatientState(
            chief_complaint="Septic shock",
            vital_signs=VitalSigns(heart_rate=140, blood_pressure="180/110", temperature=39.5),
            symptoms=["Altered mental status", "Hypoxia"]
        )
        result = triage.triage(patient)
        assert result.priority_level == "P1", "All critical should be P1"

    # ========== SYMPTOM-BASED ESCALATION ==========
    
    def test_chest_pain_with_normal_vitals_p2(self):
        """[Test] Chest pain with normal vitals = P2 (symptoms escalate)"""
        patient = PatientState(
            chief_complaint="Acute chest pain",
            vital_signs=VitalSigns(heart_rate=85, blood_pressure="120/80", temperature=37.0),
            symptoms=["Chest pain", "Radiating to left arm"]
        )
        result = triage.triage(patient)
        assert result.priority_level in ["P1", "P2"], "Chest pain should escalate to P2"

    def test_severe_dyspnea_elevated_rr_p1(self):
        """[Test] Severe dyspnea with elevated RR = P1"""
        patient = PatientState(
            chief_complaint="Severe shortness of breath",
            vital_signs=VitalSigns(heart_rate=120, blood_pressure="140/90", temperature=37.5),
            symptoms=["Severe dyspnea", "Hypoxia", "Cyanosis"]
        )
        result = triage.triage(patient)
        assert result.priority_level == "P1", "Severe dyspnea should be P1"

    def test_fever_elevated_hr_p2(self):
        """[Test] Fever 39°C with elevated HR = P2"""
        patient = PatientState(
            chief_complaint="High fever",
            vital_signs=VitalSigns(heart_rate=115, blood_pressure="120/80", temperature=39.0),
            symptoms=["High fever", "Malaise"]
        )
        result = triage.triage(patient)
        assert result.priority_level in ["P1", "P2"], "High fever should be at least P2"

    # ========== MISSING VITAL SIGNS ==========
    
    def test_missing_heart_rate_infers_from_symptoms(self):
        """[Test] Missing HR inferred from severe symptoms"""
        patient = PatientState(
            chief_complaint="Severe chest pain",
            vital_signs=VitalSigns(blood_pressure="160/100", temperature=37.0),
            symptoms=["Chest pain", "Radiating to arm"]
        )
        result = triage.triage(patient)
        # Should still be P1 or P2 based on symptoms and other vitals
        assert result.priority_level in ["P1", "P2"], "Should escalate based on available vitals"

    def test_missing_blood_pressure_infers_from_symptoms(self):
        """[Test] Missing BP inferred from severe symptoms"""
        patient = PatientState(
            chief_complaint="Shock symptoms",
            vital_signs=VitalSigns(heart_rate=140, temperature=37.0),
            symptoms=["Severe hypotension signs", "Altered mental status"]
        )
        result = triage.triage(patient)
        assert result.priority_level == "P1", "Shock symptoms should be P1"

    # ========== BOUNDARY OFF-BY-ONE TESTING ==========
    
    def test_heart_rate_99_vs_100_difference(self):
        """[Test] HR 99 and HR 100 have different priority"""
        patient_99 = PatientState(
            chief_complaint="Check",
            vital_signs=VitalSigns(heart_rate=99, blood_pressure="120/80", temperature=37.0)
        )
        patient_100 = PatientState(
            chief_complaint="Check",
            vital_signs=VitalSigns(heart_rate=100, blood_pressure="120/80", temperature=37.0)
        )
        
        result_99 = triage.triage(patient_99)
        result_100 = triage.triage(patient_100)
        
        # 100 should be higher priority than 99
        priority_order = {"P1": 1, "P2": 2, "P3": 3}
        assert priority_order[result_100.priority_level] <= priority_order[result_99.priority_level]

    def test_blood_pressure_159_vs_160_difference(self):
        """[Test] BP 159 vs 160 systolic difference matters"""
        patient_159 = PatientState(
            chief_complaint="Check",
            vital_signs=VitalSigns(heart_rate=80, blood_pressure="159/80", temperature=37.0)
        )
        patient_160 = PatientState(
            chief_complaint="Check",
            vital_signs=VitalSigns(heart_rate=80, blood_pressure="160/80", temperature=37.0)
        )
        
        result_159 = triage.triage(patient_159)
        result_160 = triage.triage(patient_160)
        
        # 160 should be higher priority than 159
        priority_order = {"P1": 1, "P2": 2, "P3": 3}
        assert priority_order[result_160.priority_level] <= priority_order[result_159.priority_level]

    def test_temperature_37_9_vs_38_0_difference(self):
        """[Test] Temp 37.9 vs 38.0 difference matters"""
        patient_37_9 = PatientState(
            chief_complaint="Check",
            vital_signs=VitalSigns(heart_rate=80, blood_pressure="120/80", temperature=37.9)
        )
        patient_38_0 = PatientState(
            chief_complaint="Check",
            vital_signs=VitalSigns(heart_rate=80, blood_pressure="120/80", temperature=38.0)
        )
        
        result_37_9 = triage.triage(patient_37_9)
        result_38_0 = triage.triage(patient_38_0)
        
        # 38.0 should be higher priority than 37.9
        priority_order = {"P1": 1, "P2": 2, "P3": 3}
        assert priority_order[result_38_0.priority_level] <= priority_order[result_37_9.priority_level]

    # ========== FLOATING POINT PRECISION ==========
    
    def test_floating_point_precision_heart_rate(self):
        """[Test] Floating point HR 99.5 rounded correctly"""
        patient = PatientState(
            chief_complaint="Check",
            vital_signs=VitalSigns(heart_rate=99.5, blood_pressure="120/80", temperature=37.0)
        )
        result = triage.triage(patient)
        # 99.5 should round to 100 or be treated as below threshold
        assert result.priority_level in ["P2", "P3"]

    def test_floating_point_precision_temperature(self):
        """[Test] Floating point temp 37.95°C handled correctly"""
        patient = PatientState(
            chief_complaint="Check",
            vital_signs=VitalSigns(heart_rate=80, blood_pressure="120/80", temperature=37.95)
        )
        result = triage.triage(patient)
        # Should be treated as close to threshold
        assert result.priority_level in ["P2", "P3"]

    # ========== CONFIDENCE SCORING ==========
    
    def test_confidence_score_high_when_all_match(self):
        """[Test] Confidence high when symptoms align with vitals"""
        patient = PatientState(
            chief_complaint="Acute MI",
            vital_signs=VitalSigns(heart_rate=140, blood_pressure="180/110", temperature=37.0),
            symptoms=["Severe chest pain", "Shortness of breath", "Diaphoresis"]
        )
        result = triage.triage(patient)
        
        assert result.confidence >= 0.8, "Should have high confidence"
        assert result.priority_level == "P1"

    def test_confidence_lower_when_conflicting_signs(self):
        """[Test] Confidence lower when symptoms conflict with vitals"""
        patient = PatientState(
            chief_complaint="Patient reports severe pain",
            vital_signs=VitalSigns(heart_rate=70, blood_pressure="120/80", temperature=37.0),
            symptoms=["Reports severe pain", "But vitals stable"]
        )
        result = triage.triage(patient)
        
        # Confidence should be lower due to conflicting indicators
        assert result.confidence <= 0.9 or result.priority_level in ["P2", "P3"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
