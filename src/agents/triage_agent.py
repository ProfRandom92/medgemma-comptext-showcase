"""Triage Agent - Priority assessment from compressed patient state."""

from __future__ import annotations

from src.core.models import PatientState


class TriageAgent:
    """Assigns a triage priority level based on patient state."""

    def assess(self, patient_state: PatientState) -> str:
        """Assess triage priority from a compressed patient state.

        Args:
            patient_state: A PatientState produced by the CompText protocol.

        Returns:
            A string indicating the triage priority level.
        """
        protocol = patient_state.meta.get("active_protocol", "")
        vitals = patient_state.vitals

        # Parse systolic BP from string like "160/90"
        systolic = None
        if vitals.bp:
            try:
                systolic = int(vitals.bp.split("/")[0])
            except (ValueError, IndexError):
                pass

        # P1 - CRITICAL: high-acuity protocols or critical vitals
        critical_protocols = ("Cardiology", "Trauma", "Neurology")
        if any(p in protocol for p in critical_protocols):
            return "\U0001f534 P1 - CRITICAL"
        if vitals.hr is not None and vitals.hr > 120:
            return "\U0001f534 P1 - CRITICAL"
        if systolic is not None and systolic > 160:
            return "\U0001f534 P1 - CRITICAL"

        # P2 - URGENT: respiratory or fever
        if "Respiratory" in protocol:
            return "\U0001f7e1 P2 - URGENT"
        if vitals.temp is not None and vitals.temp > 39.0:
            return "\U0001f7e1 P2 - URGENT"

        # P3 - STANDARD: everything else
        return "\U0001f7e2 P3 - STANDARD"
