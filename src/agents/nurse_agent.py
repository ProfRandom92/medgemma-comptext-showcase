"""Nurse Agent - Intake and compression of patient data."""

from src.core.comptext import CompTextProtocol


class NurseAgent:
    """Simulates a triage nurse that collects patient information
    and compresses it using the CompText protocol before handoff."""

    def __init__(self) -> None:
        self._protocol = CompTextProtocol()

    def intake(self, raw_text: str) -> dict:
        """Process raw patient input and return a compressed patient state.

        Args:
            raw_text: Free-form text describing patient symptoms and vitals.

        Returns:
            A compressed patient_state dictionary.
        """
        return self._protocol.compress(raw_text)
