"""Triage Agent - Priority assessment from compressed patient state."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from src.core.models import PatientState

# Display strings keyed by priority level
_DISPLAY = {
    "P1": "\U0001f534 P1 - CRITICAL",
    "P2": "\U0001f7e1 P2 - URGENT",
    "P3": "\U0001f7e2 P3 - STANDARD",
}

_PRIORITY_NAME = {
    "P1": "CRITICAL",
    "P2": "URGENT",
    "P3": "STANDARD",
}


class TriageResult(BaseModel):
    """Structured triage assessment result."""

    priority_level: Literal["P1", "P2", "P3"]
    priority_name: str
    display: str
    confidence: float = 0.90


class TriageAgent:
    """Assigns a triage priority level based on patient state."""

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_systolic(bp: str | None) -> int | None:
        """Extract systolic value from a BP string like '160/90'."""
        if not bp:
            return None
        try:
            return int(bp.split("/")[0])
        except (ValueError, IndexError):
            return None

    @staticmethod
    def _classify(patient_state: PatientState) -> Literal["P1", "P2", "P3"]:
        """Determine the priority level from *patient_state*."""
        protocol = patient_state.meta.get("active_protocol", "")
        vitals = patient_state.vitals
        systolic = TriageAgent._parse_systolic(vitals.bp)

        # P1 – CRITICAL: high-acuity protocols or critical vitals
        critical_protocols = ("Cardiology", "Trauma", "Neurology")
        if any(p in protocol for p in critical_protocols):
            return "P1"
        if vitals.hr is not None and vitals.hr > 125:
            return "P1"
        if systolic is not None and systolic > 165:
            return "P1"
        if vitals.temp is not None and vitals.temp > 40:
            return "P1"
        if vitals.temp is not None and vitals.temp < 35:
            return "P1"

        # P2 – URGENT: respiratory, elevated vitals, or fever
        if "Respiratory" in protocol:
            return "P2"
        if vitals.hr is not None and vitals.hr >= 100:
            return "P2"
        if vitals.hr is not None and vitals.hr < 50:
            return "P2"
        if systolic is not None and systolic >= 160:
            return "P2"
        if vitals.temp is not None and vitals.temp >= 38:
            return "P2"

        # P3 – STANDARD
        return "P3"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def triage(self, patient_state: PatientState) -> TriageResult:
        """Return a structured triage result for *patient_state*.

        Args:
            patient_state: A PatientState produced by the CompText protocol.

        Returns:
            A :class:`TriageResult` with validated priority level.
        """
        level = self._classify(patient_state)
        return TriageResult(
            priority_level=level,
            priority_name=_PRIORITY_NAME[level],
            display=_DISPLAY[level],
        )

    def assess(self, patient_state: PatientState) -> str:
        """Assess triage priority (legacy convenience wrapper).

        Args:
            patient_state: A PatientState produced by the CompText protocol.

        Returns:
            A human-readable string such as ``"🔴 P1 - CRITICAL"``.
        """
        return self.triage(patient_state).display
