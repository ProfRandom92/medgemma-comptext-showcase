"""Codex System - Modular clinical domain handlers for CompText."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod

from src.core.cache_manager import CompTextCache


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


class NeurologyCodex(ClinicalModule):
    """Neurology-specific clinical module."""

    _TIME_LAST_KNOWN_WELL_PATTERN = re.compile(
        r"(?:last\s+(?:known|seen)\s+(?:well|normal)\s*)(?:at\s+|was\s+)?(\d+\s*(?:hours?|minutes?|mins?|hrs?)\s*ago|\d{1,2}:\d{2})",
        re.IGNORECASE,
    )
    _SYMPTOMS_SIDE_PATTERN = re.compile(
        r"\b(left|right)\b",
        re.IGNORECASE,
    )

    @property
    def name(self) -> str:
        return "Neurology"

    @property
    def protocol_label(self) -> str:
        return "\U0001f9e0 Neurology Protocol"

    @property
    def keywords(self) -> list[str]:
        return ["stroke", "slurred", "weakness", "numbness", "face"]

    def extract(self, text: str) -> dict:
        time_last_known_well = self._extract_first(
            self._TIME_LAST_KNOWN_WELL_PATTERN, text
        )
        side_match = self._SYMPTOMS_SIDE_PATTERN.search(text)
        symptoms_side = side_match.group(1).lower() if side_match else None
        return {
            "time_last_known_well": time_last_known_well,
            "symptoms_side": symptoms_side,
        }

    @staticmethod
    def _extract_first(pattern: re.Pattern, text: str) -> str | None:
        match = pattern.search(text)
        return match.group(1).strip() if match else None


class TraumaCodex(ClinicalModule):
    """Trauma-specific clinical module."""

    _MECHANISM_PATTERN = re.compile(
        r"(?:(?:fall|fell)\s+from|hit\s+by|struck\s+by|crash\s+into|involved\s+in)\s+(.+?)(?:\.|,|;|$)",
        re.IGNORECASE,
    )
    _VISIBLE_INJURY_PATTERN = re.compile(
        r"(bone\s+exposed|laceration|open\s+wound|deformity|swelling|bruising|abrasion)",
        re.IGNORECASE,
    )

    @property
    def name(self) -> str:
        return "Trauma"

    @property
    def protocol_label(self) -> str:
        return "\U0001f691 Trauma Protocol"

    @property
    def keywords(self) -> list[str]:
        return ["fall", "fell", "accident", "crash", "fracture", "bleed", "trauma"]

    def extract(self, text: str) -> dict:
        mechanism = self._extract_first(self._MECHANISM_PATTERN, text)
        injury_match = self._VISIBLE_INJURY_PATTERN.search(text)
        visible_injury = injury_match.group(1).strip() if injury_match else None
        return {
            "mechanism_of_injury": mechanism,
            "visible_injury": visible_injury,
        }

    @staticmethod
    def _extract_first(pattern: re.Pattern, text: str) -> str | None:
        match = pattern.search(text)
        return match.group(1).strip() if match else None


class MedicalKVTCStrategy:
    """KVTC Sandwich Strategy for medical context compression.

    Implements a 'Lossless-Header / Compressed-History / Lossless-Recent'
    architecture inspired by the KV Cache Transform Coding approach
    (arXiv:2511.01815), adapted for safety-critical medical text.

    - sink_size:   Preserve the first N chars verbatim (system prompts,
                   disclaimers).
    - window_size: Preserve the last M chars verbatim (recent query /
                   symptom description).
    - middle:      Aggressively compress the remaining history.
    """

    def __init__(
        self, sink_size: int = 800, window_size: int = 1500
    ) -> None:
        self.sink_size = sink_size
        self.window_size = window_size
        self._cache = CompTextCache()

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def compress(self, text: str) -> str:
        """Apply the sandwich strategy to *text* and return the result.

        If the text is short enough that sink + window cover everything,
        the original text is returned unchanged.
        """
        total = len(text)
        min_length = self.sink_size + self.window_size

        if total <= min_length:
            return text

        header = text[: self.sink_size]
        recent = text[-self.window_size :]
        middle_raw = text[self.sink_size : total - self.window_size]

        cached = self._cache.get(middle_raw)
        if cached is not None:
            middle_compressed = cached
        else:
            middle_compressed = self._compress_middle(middle_raw)
            self._cache.put(middle_raw, middle_compressed)

        return header + middle_compressed + recent

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------

    @staticmethod
    def _compress_middle(text: str) -> str:
        """Compress the middle segment by collapsing whitespace and
        removing redundant lines while preserving medical keywords."""
        # Collapse runs of whitespace into a single space
        compressed = re.sub(r"\s+", " ", text).strip()
        # Remove duplicate sentences (simple dedup)
        seen: set[str] = set()
        unique_parts: list[str] = []
        for sentence in re.split(r"(?<=[.!?])\s+", compressed):
            normalized = sentence.strip().lower()
            if normalized and normalized not in seen:
                seen.add(normalized)
                unique_parts.append(sentence.strip())
        return " ".join(unique_parts)


class CodexRouter:
    """Selects the appropriate clinical module based on input text."""

    def __init__(self) -> None:
        self._modules: list[ClinicalModule] = [
            CardiologyCodex(),
            RespiratoryCodex(),
            NeurologyCodex(),
            TraumaCodex(),
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
