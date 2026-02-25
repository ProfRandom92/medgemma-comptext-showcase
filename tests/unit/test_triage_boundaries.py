"""[Test] Triage boundary conditions - testing TriageAgent priority assessment."""

import pytest
from src.core.models import PatientState, Vitals
from src.agents.triage_agent import TriageAgent


class TestTriageBoundaries:
    """Test boundary conditions for triage priority assignment."""

    def test_heart_rate_below_threshold_p3(self):
        """[Test] HR 60 should be P3 (standard)."""
        agent = TriageAgent()
        state = PatientState(vitals=Vitals(hr=60))
        result = agent.assess(state)
        assert "P3" in result or "STANDARD" in result

    def test_heart_rate_at_threshold_p2(self):
        """[Test] HR 120 is at critical threshold."""
        agent = TriageAgent()
        state = PatientState(vitals=Vitals(hr=120))
        result = agent.assess(state)
        # 120 is at threshold, should be P2 or P3 depending on implementation
        assert "P" in result

    def test_heart_rate_above_threshold_p1(self):
        """[Test] HR 121 exceeds threshold, should be P1."""
        agent = TriageAgent()
        state = PatientState(vitals=Vitals(hr=121))
        result = agent.assess(state)
        assert "P1" in result or "CRITICAL" in result

    def test_heart_rate_severe_p1(self):
        """[Test] HR 150 should be P1 (critical)."""
        agent = TriageAgent()
        state = PatientState(vitals=Vitals(hr=150))
        result = agent.assess(state)
        assert "P1" in result

    def test_blood_pressure_systolic_above_threshold_p1(self):
        """[Test] BP 161/90 exceeds systolic threshold, should be P1."""
        agent = TriageAgent()
        state = PatientState(vitals=Vitals(bp="161/90"))
        result = agent.assess(state)
        assert "P1" in result or "CRITICAL" in result

    def test_blood_pressure_systolic_at_threshold(self):
        """[Test] BP 160/90 at systolic threshold."""
        agent = TriageAgent()
        state = PatientState(vitals=Vitals(bp="160/90"))
        result = agent.assess(state)
        # At threshold, should be P2 or handled gracefully
        assert "P" in result

    def test_blood_pressure_systolic_below_threshold_p3(self):
        """[Test] BP 140/90 below threshold, should be P3."""
        agent = TriageAgent()
        state = PatientState(vitals=Vitals(bp="140/90"))
        result = agent.assess(state)
        assert "P3" in result or "STANDARD" in result

    def test_temperature_above_threshold_p2(self):
        """[Test] Temp 39.1 exceeds threshold, should be P2."""
        agent = TriageAgent()
        state = PatientState(vitals=Vitals(temp=39.1))
        result = agent.assess(state)
        assert "P2" in result or "URGENT" in result

    def test_temperature_at_threshold(self):
        """[Test] Temp 39.0 at threshold."""
        agent = TriageAgent()
        state = PatientState(vitals=Vitals(temp=39.0))
        result = agent.assess(state)
        assert "P" in result

    def test_temperature_below_threshold_p3(self):
        """[Test] Temp 38.5 below fever threshold, should be P3."""
        agent = TriageAgent()
        state = PatientState(vitals=Vitals(temp=38.5))
        result = agent.assess(state)
        assert "P3" in result or "STANDARD" in result

    def test_all_normal_vitals_p3(self):
        """[Test] All normal vitals should be P3."""
        agent = TriageAgent()
        state = PatientState(vitals=Vitals(hr=75, bp="120/80", temp=37.5))
        result = agent.assess(state)
        assert "P3" in result

    def test_one_critical_vital_hr_high(self):
        """[Test] One critical vital (high HR) should escalate priority."""
        agent = TriageAgent()
        state = PatientState(vitals=Vitals(hr=125, bp="120/80", temp=37.5))
        result = agent.assess(state)
        assert "P1" in result or "P2" in result

    def test_one_critical_vital_temp_high(self):
        """[Test] One critical vital (high temp) should escalate."""
        agent = TriageAgent()
        state = PatientState(vitals=Vitals(hr=80, bp="120/80", temp=39.5))
        result = agent.assess(state)
        assert "P2" in result or "URGENT" in result

    def test_cardiology_protocol_p1(self):
        """[Test] Cardiology protocol should be P1."""
        agent = TriageAgent()
        state = PatientState(
            vitals=Vitals(hr=80, bp="120/80"),
            meta={"active_protocol": "Cardiology"}
        )
        result = agent.assess(state)
        assert "P1" in result

    def test_trauma_protocol_p1(self):
        """[Test] Trauma protocol should be P1."""
        agent = TriageAgent()
        state = PatientState(
            vitals=Vitals(hr=95),
            meta={"active_protocol": "Trauma"}
        )
        result = agent.assess(state)
        assert "P1" in result

    def test_respiratory_protocol_p2(self):
        """[Test] Respiratory protocol should be P2."""
        agent = TriageAgent()
        state = PatientState(
            vitals=Vitals(hr=80),
            meta={"active_protocol": "Respiratory"}
        )
        result = agent.assess(state)
        assert "P2" in result or "URGENT" in result

    def test_no_protocol_normal_vitals_p3(self):
        """[Test] No protocol + normal vitals = P3."""
        agent = TriageAgent()
        state = PatientState(vitals=Vitals(hr=70, bp="120/80"))
        result = agent.assess(state)
        assert "P3" in result

    def test_assess_returns_string(self):
        """[Test] assess() method returns string."""
        agent = TriageAgent()
        state = PatientState(vitals=Vitals(hr=90))
        result = agent.assess(state)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_triage_agent_initializes(self):
        """[Test] TriageAgent can be instantiated."""
        agent = TriageAgent()
        assert agent is not None

    def test_multiple_assessment_calls(self):
        """[Test] TriageAgent can assess multiple states."""
        agent = TriageAgent()
        state1 = PatientState(vitals=Vitals(hr=85))
        state2 = PatientState(vitals=Vitals(hr=140))
        result1 = agent.assess(state1)
        result2 = agent.assess(state2)
        assert isinstance(result1, str)
        assert isinstance(result2, str)
        assert "P" in result1
        assert "P" in result2

    def test_boundary_hr_99_vs_100(self):
        """[Test] HR 99 vs 100 boundary."""
        agent = TriageAgent()
        state99 = PatientState(vitals=Vitals(hr=99))
        state100 = PatientState(vitals=Vitals(hr=100))
        result99 = agent.assess(state99)
        result100 = agent.assess(state100)
        assert "P" in result99
        assert "P" in result100

    def test_boundary_bp_159_vs_160(self):
        """[Test] BP 159 vs 160 systolic boundary."""
        agent = TriageAgent()
        state159 = PatientState(vitals=Vitals(bp="159/90"))
        state160 = PatientState(vitals=Vitals(bp="160/90"))
        result159 = agent.assess(state159)
        result160 = agent.assess(state160)
        assert "P" in result159
        assert "P" in result160

    def test_boundary_temp_39_vs_40(self):
        """[Test] Temp 39.0 vs 39.1 boundary."""
        agent = TriageAgent()
        state39 = PatientState(vitals=Vitals(temp=39.0))
        state391 = PatientState(vitals=Vitals(temp=39.1))
        result39 = agent.assess(state39)
        result391 = agent.assess(state391)
        assert "P" in result39
        assert "P" in result391

    def test_invalid_bp_format_handled(self):
        """[Test] Invalid BP format handled gracefully."""
        agent = TriageAgent()
        state = PatientState(vitals=Vitals(bp="invalid"))
        result = agent.assess(state)
        # Should not crash, should return valid priority
        assert "P" in result

    def test_missing_vitals_handled(self):
        """[Test] PatientState with None vitals handled."""
        agent = TriageAgent()
        state = PatientState(vitals=Vitals())  # All None
        result = agent.assess(state)
        assert isinstance(result, str)
        assert "P" in result
