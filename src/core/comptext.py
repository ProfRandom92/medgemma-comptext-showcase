"""CompText Protocol - Privacy-first patient data compression engine (v5 mock)."""

import re


class CompTextProtocol:
    """Simulates the CompText v5 compression engine.

    Extracts structured medical data from raw clinical text using regex,
    compressing it into a clean JSON representation. This reduces token
    usage by ~94% while preserving clinically relevant information.
    """

    # Patterns for extracting clinical data — explicit labels first, then fallback
    _CHIEF_COMPLAINT_PRIMARY = re.compile(
        r"(?:chief complaint|cc|complaint|presenting with|presents with)\s*[:\-]?\s*(.+?)(?:\.|,|;|$)",
        re.IGNORECASE,
    )
    _CHIEF_COMPLAINT_FALLBACK = re.compile(
        r"(?:patient has)\s*[:\-]?\s*(.+?)(?:\.|,|;|$)",
        re.IGNORECASE,
    )
    _HR_PATTERN = re.compile(
        r"(?:hr|heart rate)\s*[:\-]?\s*(\d+)", re.IGNORECASE
    )
    _BP_PATTERN = re.compile(
        r"(?:bp|blood pressure)\s*[:\-]?\s*(\d+/\d+)", re.IGNORECASE
    )
    _TEMP_PATTERN = re.compile(
        r"(?:temp|temperature|fever)\s*[:\-]?\s*(\d+\.?\d*)\s*(?:°?\s*[CcFf])?",
        re.IGNORECASE,
    )
    _MEDICATION_PATTERN = re.compile(
        r"(?:medication|med|prescribed|taking|on)\s*[:\-]?\s*(.+?)(?:\.|,|;|$)",
        re.IGNORECASE,
    )

    def compress(self, raw_text: str) -> dict:
        """Compress raw clinical text into a structured JSON representation.

        Args:
            raw_text: Free-form clinical text containing patient information.

        Returns:
            A dictionary with extracted clinical fields.
        """
        chief_complaint = (
            self._extract_first(self._CHIEF_COMPLAINT_PRIMARY, raw_text)
            or self._extract_first(self._CHIEF_COMPLAINT_FALLBACK, raw_text)
        )
        hr = self._extract_first(self._HR_PATTERN, raw_text)
        bp = self._extract_first(self._BP_PATTERN, raw_text)
        temp = self._extract_first(self._TEMP_PATTERN, raw_text)
        medication = self._extract_first(self._MEDICATION_PATTERN, raw_text)

        return {
            "chief_complaint": chief_complaint,
            "vitals": {
                "hr": int(hr) if hr else None,
                "bp": bp,
                "temp": float(temp) if temp else None,
            },
            "medication": medication,
        }

    @staticmethod
    def _extract_first(pattern: re.Pattern, text: str) -> str | None:
        """Return the first capture group match or None."""
        match = pattern.search(text)
        return match.group(1).strip() if match else None
