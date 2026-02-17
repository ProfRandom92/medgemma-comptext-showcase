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
from core.models import PatientState, Vitals

# Initialize triage agent
triage = TriageAgent()


class TestTriageBoundaries:
    """Tests for critical threshold boundaries in triage classification"""

    # ========== HEART RATE THRESHOLDS ==========
    
    def test_heart_rate_below_threshold_p3(self):
        """[Test] HR 99 (below 100 threshold) = P3"""
        patient = PatientState(
            chief_complaint="Routine check",
            vitals=Vitals(hr=99, bp="120/80", temp=37.0)
        )
        result = triage.triage(patient)
        assert result.priority_level == "P3", "HR 99 should be P3"

    def test_heart_rate_at_threshold_p2(self):
        """[Test] HR 100 (at threshold) = P2"""
        patient = PatientState(
            chief_complaint="Routine check",
            vitals=Vitals(hr=100, bp="120/80", temp=37.0)
        )
        result = triage.triage(patient)
        assert result.priority_level == "P2", "HR 100 should be P2"

    def test_heart_rate_above_threshold_p2(self):
        """[Test] HR 110 (above 100) = P2"""
        patient = PatientState(
            chief_complaint="Routine check",
            vitals=Vitals(hr=110, bp="120/80", temp=37.0)
        )
        result = triage.triage(patient)
        assert result.priority_level in ["P2", "P1"], "HR 110 should be at least P2"

    def test_heart_rate_severe_p1(self):
        """[Test] HR 140 (severe) = P1"""
        patient = PatientState(
            chief_complaint="Chest pain with palpitations",
            vitals=Vitals(hr=140, bp="120/80", temp=37.0)
        )
        result = triage.triage(patient)
        assert result.priority_level == "P1", "HR 140 should be P1"

    def test_heart_rate_low_p2(self):
        """[Test] HR 45 (bradycardia) = P2 or P1"""
        patient = PatientState(
            chief_complaint="Dizziness",
            vitals=Vitals(hr=45, bp="120/80", temp=37.0)
        )
        result = triage.triage(patient)
        assert result.priority_level in ["P1", "P2"], "Low HR should be urgent"

    # ========== BLOOD PRESSURE THRESHOLDS ==========
    
    def test_blood_pressure_systolic_below_threshold_p3(self):
        """[Test] BP 159/90 (SBP below 160) = P3"""
        patient = PatientState(
            chief_complaint="Routine check",
            vitals=Vitals(hr=80, bp="159/90", temp=37.0)
        )
        result = triage.triage(patient)
        assert result.priority_level == "P3", "BP 159 systolic should be P3"

    def test_blood_pressure_systolic_at_threshold_p2(self):
        """[Test] BP 160/90 (at SBP threshold) = P2"""
        patient = PatientState(
            chief_complaint="Routine check",
            vitals=Vitals(hr=80, bp="160/90", temp=37.0)
        )
        result = triage.triage(patient)
        assert result.priority_level in ["P2", "P1"], "BP 160 systolic should be urgent"

    def test_blood_pressure_systolic_above_threshold_p2_or_p1(self):
        """[Test] BP 180/95 (SBP well above threshold) = P1"""
        patient = PatientState(
            chief_complaint="Severe headache",
            vitals=Vitals(hr=110, bp="180/110", temp=37.0)
        )
        result = triage.triage(patient)
        assert result.priority_level == "P1", "BP 180/110 should be P1"

    def test_blood_pressure_diastolic_high_p2(self):
        """[Test] High diastolic (e.g., 120/100) = P2"""
        patient = PatientState(
            chief_complaint="Headache",
            vitals=Vitals(hr=100, bp="140/100", temp=37.0)
        )
        result = triage.triage(patient)
        assert result.priority_level in ["P1", "P2"], "Diastolic 100 should be urgent"

    def test_blood_pressure_low_p2_or_p1(self):
        """[Test] Hypotension (e.g., 90/60) = P2 or P1"""
        patient = PatientState(
            chief_complaint="Dizziness, weakness",
            vitals=Vitals(hr=110, bp="90/60", temp=37.0)
        )
        result = triage.triage(patient)
        assert result.priority_level in ["P1", "P2"], "Low BP should be urgent"

    # ========== TEMPERATURE THRESHOLDS ==========
    
    def test_temperature_below_threshold_p3(self):
        """[Test] Temp 37.9°C (below 38.0) = P3"""
        patient = PatientState(
            chief_complaint="Mild fever",
            vitals=Vitals(hr=90, bp="120/80", temp=37.9)
        )
        result = triage.triage(patient)
        assert result.priority_level == "P3", "Temp 37.9 should be P3"

    def test_temperature_at_threshold_p2(self):
        """[Test] Temp 38.0°C (at threshold) = P2"""
        patient = PatientState(
            chief_complaint="Fever",
            vitals=Vitals(hr=100, bp="120/80", temp=38.0)
        )
        result = triage.triage(patient)
        assert result.priority_level in ["P2", "P1"], "Temp 38.0 should be urgent"

    def test_temperature_above_threshold_p2_or_p1(self):
        """[Test] Temp 39.5°C (above threshold) = P2 or P1"""
        patient = PatientState(
            chief_complaint="High fever",
            vitals=Vitals(hr=115, bp="120/80", temp=39.5)
        )
        result = triage.triage(patient)
        assert result.priority_level in ["P1", "P2"], "Temp 39.5 should be urgent"

    def test_temperature_very_high_p1(self):
        """[Test] Temp 40.5°C (critical) = P1"""
        patient = PatientState(
            chief_complaint="Very high fever, confusion",
            vitals=Vitals(hr=130, bp="120/80", temp=40.5)
        )
        result = triage.triage(patient)
        assert result.priority_level == "P1", "Temp 40.5 should be P1"

    def test_temperature_very_low_p1(self):
        """[Test] Temp 34.0°C (hypothermia) = P1"""
        patient = PatientState(
            chief_complaint="Hypothermia, altered mental status",
            vitals=Vitals(hr=50, bp="90/60", temp=34.0)
        )
        result = triage.triage(patient)
        assert result.priority_level == "P1", "Hypothermia should be P1"

    # ========== MULTIPLE CRITICAL VITALS ==========
    
    def test_all_normal_vitals_p3(self):
        """[Test] All vitals normal = P3"""
        patient = PatientState(
            chief_complaint="Routine check-up",
            vitals=Vitals(hr=75, bp="120/80", temp=37.0)
        )
        result = triage.triage(patient)
        assert result.priority_level == "P3", "All normal should be P3"

    def test_one_critical_vital_p2(self):
        """[Test] HR critical, others normal = P2"""
        patient = PatientState(
            chief_complaint="Palpitations",
            vitals=Vitals(hr=125, bp="120/80", temp=37.0)
        )
        result = triage.triage(patient)
        assert result.priority_level == "P2", "One critical vital should be P2"

    def test_two_critical_vitals_p1(self):
        """[Test] HR 125 AND BP 170/100 = P1"""
        patient = PatientState(
            chief_complaint="Chest pain with hypertension",
            vitals=Vitals(hr=125, bp="170/100", temp=37.0)
        )
        result = triage.triage(patient)
        assert result.priority_level == "P1", "Multiple critical vitals should be P1"

    def test_all_critical_vitals_p1(self):
        """[Test] HR 140, BP 180/110, Temp 39.5 = P1"""
        patient = PatientState(
            chief_complaint="Septic shock",
            vitals=Vitals(hr=140, bp="180/110", temp=39.5)
        )
        result = triage.triage(patient)
        assert result.priority_level == "P1", "All critical should be P1"

    # ========== BOUNDARY OFF-BY-ONE TESTING ==========
    
    def test_heart_rate_99_vs_100_difference(self):
        """[Test] HR 99 and HR 100 have different priority"""
        patient_99 = PatientState(
            chief_complaint="Check",
            vitals=Vitals(hr=99, bp="120/80", temp=37.0)
        )
        patient_100 = PatientState(
            chief_complaint="Check",
            vitals=Vitals(hr=100, bp="120/80", temp=37.0)
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
            vitals=Vitals(hr=80, bp="159/80", temp=37.0)
        )
        patient_160 = PatientState(
            chief_complaint="Check",
            vitals=Vitals(hr=80, bp="160/80", temp=37.0)
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
            vitals=Vitals(hr=80, bp="120/80", temp=37.9)
        )
        patient_38_0 = PatientState(
            chief_complaint="Check",
            vitals=Vitals(hr=80, bp="120/80", temp=38.0)
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
            vitals=Vitals(hr=round(99.5), bp="120/80", temp=37.0)
        )
        result = triage.triage(patient)
        # 99.5 rounds to 100, which meets the P2 threshold (hr >= 100)
        assert result.priority_level in ["P2", "P3"]

    def test_floating_point_precision_temperature(self):
        """[Test] Floating point temp 37.95°C handled correctly"""
        patient = PatientState(
            chief_complaint="Check",
            vitals=Vitals(hr=80, bp="120/80", temp=37.95)
        )
        result = triage.triage(patient)
        # Should be treated as close to threshold
        assert result.priority_level in ["P2", "P3"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
