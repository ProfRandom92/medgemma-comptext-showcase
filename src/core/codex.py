"""Codex System - Modular clinical domain handlers for CompText."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod


class ClinicalModule(ABC):
    """Abstract base class for domain-specific clinical modules."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the clinical module."""

    @property
    @abstractmethod
    def protocol_label(self) -> str:
        """Protocol label shown in the meta field (e.g. '🫀 Cardiology Protocol')."""

    @property
    @abstractmethod
    def keywords(self) -> list[str]:
        """Keywords that trigger this module."""

    @abstractmethod
    def extract(self, text: str) -> dict:
        """Extract domain-specific fields from clinical text.

        Args:
            text: Raw clinical text.

        Returns:
            A dictionary of extracted specialist fields.
        """


class CardiologyCodex(ClinicalModule):
    """Cardiology-specific clinical module."""

    _RADIATION_PATTERN = re.compile(
        r"(?:radiat(?:es?|ing|ion)\s*(?:to)?\s*)(.+?)(?:\.|,|;|$)",
        re.IGNORECASE,
    )
    _PAIN_QUALITY_PATTERN = re.compile(
        r"(?:pain\s+(?:is\s+)?(?:described\s+as\s+)?)(sharp|dull|crushing|stabbing|burning|pressure|tight|squeezing|aching)",
        re.IGNORECASE,
    )

    @property
    def name(self) -> str:
        return "Cardiology"

    @property
    def protocol_label(self) -> str:
        return "\U0001fac0 Cardiology Protocol"

    @property
    def keywords(self) -> list[str]:
        return ["chest pain", "heart", "pressure"]

    def extract(self, text: str) -> dict:
        radiation = self._extract_first(self._RADIATION_PATTERN, text)
        pain_quality = self._extract_first(self._PAIN_QUALITY_PATTERN, text)
        return {
            "radiation": radiation,
            "pain_quality": pain_quality,
        }

    @staticmethod
    def _extract_first(pattern: re.Pattern, text: str) -> str | None:
        match = pattern.search(text)
        return match.group(1).strip() if match else None


class RespiratoryCodex(ClinicalModule):
    """Respiratory-specific clinical module."""

    _TRIGGERS_PATTERN = re.compile(
        r"(?:trigger(?:s|ed)?\s*(?:by|include|:)\s*)(.+?)(?:\.|,|;|$)",
        re.IGNORECASE,
    )
    _BREATH_SOUNDS_PATTERN = re.compile(
        r"(?:breath sounds?\s*[:\-]?\s*)(clear|diminished|wheezes?|crackles?|rhonchi|stridor|absent)",
        re.IGNORECASE,
    )

    @property
    def name(self) -> str:
        return "Respiratory"

    @property
    def protocol_label(self) -> str:
        return "\U0001fab7 Respiratory Protocol"

    @property
    def keywords(self) -> list[str]:
        return ["breath", "asthma", "wheezing"]

    def extract(self, text: str) -> dict:
        triggers = self._extract_first(self._TRIGGERS_PATTERN, text)
        breath_sounds = self._extract_first(self._BREATH_SOUNDS_PATTERN, text)
        return {
            "triggers": triggers,
            "breath_sounds": breath_sounds,
        }

    @staticmethod
    def _extract_first(pattern: re.Pattern, text: str) -> str | None:
        match = pattern.search(text)
        return match.group(1).strip() if match else None


class CodexRouter:
    """Selects the appropriate clinical module based on input text."""

    def __init__(self) -> None:
        self._modules: list[ClinicalModule] = [
            CardiologyCodex(),
            RespiratoryCodex(),
        ]

    def route(self, text: str) -> ClinicalModule | None:
        """Return the first matching clinical module for the given text.

        Args:
            text: Raw clinical text.

        Returns:
            The matched ClinicalModule, or None if no module matches.
        """
        lower_text = text.lower()
        for module in self._modules:
            for keyword in module.keywords:
                if keyword in lower_text:
                    return module
        return None
