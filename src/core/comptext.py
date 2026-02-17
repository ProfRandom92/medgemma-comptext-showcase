"""CompText Protocol - Privacy-first patient data compression engine (v5 mock)."""

from __future__ import annotations

import re

from src.core.codex import CodexRouter
from src.core.models import PatientState, Vitals


class CompTextProtocol:
    """Simulates the CompText v5 compression engine.

    Extracts structured medical data from raw clinical text using regex,
    compressing it into a clean JSON representation. This reduces token
    usage by ~94% while preserving clinically relevant information.
    """

    # Patterns for extracting clinical data — explicit labels first, then fallback
    _CHIEF_COMPLAINT_PRIMARY = re.compile(
        r"(?:chief complaint|cc|complaint|presenting with|presents with)\s*[:\-]?\s*(.+?)(?:\.|,|;|$)",
        re.IGNORECASE | re.MULTILINE,
    )
    _CHIEF_COMPLAINT_FALLBACK = re.compile(
        r"(?:patient has|presenting complaint)\s*[:\-]?\s*(.+?)(?:\.|,|;|$)",
        re.IGNORECASE | re.MULTILINE,
    )
    _HR_PATTERN = re.compile(
        r"(?:hr|heart rate)\s*[:\-]?\s*(\d+)", re.IGNORECASE
    )
    _BP_PATTERN = re.compile(
        r"(?:bp|blood pressure)\s*[:\-]?\s*(\d+/\d+)", re.IGNORECASE
    )
    _TEMP_PATTERN = re.compile(
        r"(?:temp(?:erature)?|fever|\bT(?=\s))\s*[:\-]?\s*(\d+\.?\d*)\s*(?:°?\s*[CcFf])?",
        re.IGNORECASE,
    )
    _MEDICATION_PATTERN = re.compile(
        r"(?:medications?|meds?|prescribed|taking)\s*[:\-]\s*([^\n]{2,80})",
        re.IGNORECASE,
    )
    _DIAGNOSIS_PATTERN = re.compile(
        r"(?:diagnosis|impression|dx|assessment|diagnos(?:ed|tic))\s*[:\-]?\s*([^\n]{2,100})",
        re.IGNORECASE,
    )
    _ALLERGY_PATTERN = re.compile(
        r"(?:allerg(?:y|ies|ic)|nkda)\s*[:\-]?\s*([^\n]{2,100})",
        re.IGNORECASE,
    )

    def __init__(self) -> None:
        self._router = CodexRouter()

    _SYMPTOM_KEYWORDS = re.compile(
        r"\b(pain|nausea|vomiting|fatigue|fever|headache|dyspnea|shortness of breath|"
        r"chest pain|dizziness|weakness|syncope|palpitations|swelling|cough|"
        r"confusion|anxiety|depression|insomnia|rash|bleeding|diarrhea|constipation)\b",
        re.IGNORECASE,
    )

    def _extract_symptoms(self, text: str) -> list[str]:
        """Extract unique symptom keywords from clinical text."""
        return list({m.group(0).lower() for m in self._SYMPTOM_KEYWORDS.finditer(text)})

    def compress(self, raw_text: str) -> PatientState:
        """Compress raw clinical text into a structured PatientState model.

        Args:
            raw_text: Free-form clinical text containing patient information.

        Returns:
            A PatientState Pydantic model with extracted clinical fields.
        """
        # Token count approximation: chars/4 is standard LLM token estimate
        original_tokens = max(len(raw_text) // 4, 1)

        chief_complaint = (
            self._extract_first(self._CHIEF_COMPLAINT_PRIMARY, raw_text)
            or self._extract_first(self._CHIEF_COMPLAINT_FALLBACK, raw_text)
        )
        hr = self._extract_first(self._HR_PATTERN, raw_text)
        bp = self._extract_first(self._BP_PATTERN, raw_text)
        temp = self._extract_first(self._TEMP_PATTERN, raw_text)
        medication = self._extract_first(self._MEDICATION_PATTERN, raw_text)
        if medication:
            medication = medication.strip().rstrip(".,:;)")
        diagnosis = self._extract_first(self._DIAGNOSIS_PATTERN, raw_text)
        allergies = self._extract_first(self._ALLERGY_PATTERN, raw_text)

        symptoms = self._extract_symptoms(raw_text)
        codex = self._codex_fields(raw_text)

        # Merge extracted diagnosis/allergies into specialist_data
        if diagnosis:
            codex["specialist_data"]["diagnosis"] = diagnosis.strip()
        if allergies:
            codex["specialist_data"]["allergies"] = allergies.strip()

        state = PatientState(
            chief_complaint=chief_complaint,
            vitals=Vitals(
                hr=float(hr) if hr else None,
                bp=bp,
                temp=float(temp) if temp else None,
            ),
            medication=medication,
            symptoms=symptoms,
            meta=codex["meta"],
            specialist_data=codex["specialist_data"],
        )

        # Store token counts so compression_ratio property works accurately
        compressed_tokens = max(len(state.to_compressed_json()) // 4, 1)
        state._original_token_count = original_tokens
        state._compressed_token_count = compressed_tokens

        return state

    @staticmethod
    def _extract_first(pattern: re.Pattern, text: str) -> str | None:
        """Return the first capture group match or None."""
        match = pattern.search(text)
        return match.group(1).strip() if match else None

    def _codex_fields(self, raw_text: str) -> dict:
        """Return meta and specialist fields from the active codex module."""
        module = self._router.route(raw_text)
        if module is None:
            return {
                "meta": {"active_protocol": "General"},
                "specialist_data": {},
            }
        return {
            "meta": {"active_protocol": module.protocol_label},
            "specialist_data": module.extract(raw_text),
        }
