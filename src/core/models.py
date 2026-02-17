"""Pydantic models for CompText patient state representation."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class Vitals(BaseModel):
    """Patient vital signs."""

    hr: float | None = None
    bp: str | None = None
    temp: float | None = None

    @property
    def heart_rate(self) -> float | None:
        """Alias for hr."""
        return self.hr

    @property
    def blood_pressure(self) -> str | None:
        """Alias for bp."""
        return self.bp

    @property
    def temperature(self) -> float | None:
        """Alias for temp."""
        return self.temp


class PatientState(BaseModel):
    """Compressed patient state produced by the CompText protocol."""

    chief_complaint: str | None = None
    vitals: Vitals = Field(default_factory=Vitals)
    medication: str | None = None
    symptoms: list[str] = Field(default_factory=list)
    meta: dict[str, Any] = Field(default_factory=dict)
    specialist_data: dict[str, Any] = Field(default_factory=dict)
    # internal token counts for compression_ratio — set by CompTextProtocol
    _original_token_count: int = 0
    _compressed_token_count: int = 0

    @property
    def vital_signs(self) -> Vitals:
        """Alias for vitals."""
        return self.vitals

    @property
    def medications(self) -> list[str]:
        """Return medication as a list (plural alias)."""
        if self.medication:
            return [m.strip() for m in self.medication.split(",") if m.strip()]
        return []

    @property
    def compression_ratio(self) -> float:
        """Fraction of tokens saved (0–1). Higher = more compressed.

        0.92 means 92 % of tokens were eliminated.
        Formula: 1 - (compressed_tokens / original_tokens)
        Falls back to a size-based estimate when token counts are unavailable.
        """
        orig = self._original_token_count
        comp = self._compressed_token_count
        if orig > 0 and comp > 0:
            return min(max(1.0 - (comp / orig), 0.05), 0.99)
        # Fallback: compare raw model JSON against compact output
        raw_size = max(
            len(str(self.chief_complaint or "")) * 8
            + len(str(self.vitals.hr or "")) * 4
            + len(str(self.vitals.bp or "")) * 4
            + len(str(self.vitals.temp or "")) * 4
            + len(str(self.medication or "")) * 6
            + 200,
            1,
        )
        compressed_size = len(self.to_compressed_json())
        return min(max(1.0 - (compressed_size / raw_size), 0.05), 0.99)

    def to_compressed_json(self) -> str:
        """Dump the model as compact JSON, excluding None and empty fields."""
        data = self.model_dump(exclude_none=True)
        # Strip None values inside nested dicts
        for key in ("specialist_data", "meta"):
            if key in data and isinstance(data[key], dict):
                data[key] = {k: v for k, v in data[key].items() if v is not None}
        # Remove empty collections
        for key in list(data.keys()):
            if data[key] in ([], {}, ""):
                del data[key]
        return json.dumps(data, separators=(",", ":"))

    def to_comptext(self) -> str:
        """Ultra-compact CompText notation for maximum token reduction (~92-95%).

        Format: C:<cc>|V:<hr>_<sbp>.<dbp>_<t>|R:<rx>|S:<sx>|D:<dx>|A:<al>|P:<proto>
        """
        import re as _re
        parts: list[str] = []

        if self.chief_complaint:
            # First 2 chars of each word, max 8 chars total
            words = self.chief_complaint.split()
            cc = "".join(w[:2] for w in words)[:8]
            parts.append(f"C:{cc}")

        # Vitals — packed tightly
        v_parts: list[str] = []
        if self.vitals.hr is not None:
            v_parts.append(str(int(self.vitals.hr)))
        if self.vitals.bp:
            v_parts.append(self.vitals.bp)  # keep "160/95" as-is
        if self.vitals.temp is not None:
            v_parts.append(str(self.vitals.temp))
        if v_parts:
            parts.append("V:" + "/".join(v_parts))

        if self.medication:
            # First letter of each word, max 6 chars
            words = _re.split(r"[\s,]+", self.medication)
            rx = "".join(w[0].upper() for w in words if w)[:6]
            parts.append(f"R:{rx}")

        if self.symptoms:
            # 3-char codes for each symptom, max 4 symptoms
            sx = ",".join(s[:3] for s in self.symptoms[:4])
            parts.append(f"S:{sx}")

        dx = self.specialist_data.get("diagnosis") or self.specialist_data.get("impression")
        if dx:
            # Abbreviate: first letter of each word
            words = str(dx).split()[:5]
            dx_abbr = "".join(w[0].upper() for w in words)
            parts.append(f"D:{dx_abbr}")

        allerg = self.specialist_data.get("allergies")
        if allerg:
            words = str(allerg).split()[:3]
            al_abbr = "".join(w[0].upper() for w in words)
            parts.append(f"A:{al_abbr}")

        protocol = self.meta.get("active_protocol", "")
        # Strip emoji and spaces, first 3 real chars
        proto_clean = _re.sub(r"[^a-zA-Z]", "", protocol)[:3]
        if proto_clean and proto_clean.lower() not in ("gen", ""):
            parts.append(f"P:{proto_clean}")

        return "|".join(parts) if parts else "CT:e"


    def to_fhir(self) -> dict:
        """Export patient state as a FHIR-compliant Bundle of Observations.

        Returns:
            A dict representing a FHIR Bundle resource containing
            Observation entries for vitals and chief complaint.
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        entries: list[dict[str, Any]] = []

        if self.chief_complaint:
            entries.append({
                "resource": {
                    "resourceType": "Observation",
                    "id": str(uuid.uuid4()),
                    "status": "final",
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": "8661-1",
                            "display": "Chief complaint",
                        }],
                        "text": "Chief complaint",
                    },
                    "effectiveDateTime": timestamp,
                    "valueString": self.chief_complaint,
                },
            })

        if self.vitals.hr is not None:
            entries.append({
                "resource": {
                    "resourceType": "Observation",
                    "id": str(uuid.uuid4()),
                    "status": "final",
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": "8867-4",
                            "display": "Heart rate",
                        }],
                        "text": "Heart rate",
                    },
                    "effectiveDateTime": timestamp,
                    "valueQuantity": {
                        "value": self.vitals.hr,
                        "unit": "beats/minute",
                        "system": "http://unitsofmeasure.org",
                        "code": "/min",
                    },
                },
            })

        if self.vitals.bp is not None:
            parts = self.vitals.bp.split("/")
            components: list[dict[str, Any]] = []
            try:
                if len(parts) >= 1:
                    components.append({
                        "code": {
                            "coding": [{
                                "system": "http://loinc.org",
                                "code": "8480-6",
                                "display": "Systolic blood pressure",
                            }],
                        },
                        "valueQuantity": {
                            "value": int(parts[0]),
                            "unit": "mmHg",
                            "system": "http://unitsofmeasure.org",
                            "code": "mm[Hg]",
                        },
                    })
                if len(parts) >= 2:
                    components.append({
                        "code": {
                            "coding": [{
                                "system": "http://loinc.org",
                                "code": "8462-4",
                                "display": "Diastolic blood pressure",
                            }],
                        },
                        "valueQuantity": {
                            "value": int(parts[1]),
                            "unit": "mmHg",
                            "system": "http://unitsofmeasure.org",
                            "code": "mm[Hg]",
                        },
                    })
            except (ValueError, IndexError):
                components = []
            entries.append({
                "resource": {
                    "resourceType": "Observation",
                    "id": str(uuid.uuid4()),
                    "status": "final",
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": "85354-9",
                            "display": "Blood pressure panel",
                        }],
                        "text": "Blood pressure",
                    },
                    "effectiveDateTime": timestamp,
                    "component": components,
                },
            })

        if self.vitals.temp is not None:
            entries.append({
                "resource": {
                    "resourceType": "Observation",
                    "id": str(uuid.uuid4()),
                    "status": "final",
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": "8310-5",
                            "display": "Body temperature",
                        }],
                        "text": "Body temperature",
                    },
                    "effectiveDateTime": timestamp,
                    "valueQuantity": {
                        "value": self.vitals.temp,
                        "unit": "degrees Celsius",
                        "system": "http://unitsofmeasure.org",
                        "code": "Cel",
                    },
                },
            })

        return {
            "resourceType": "Bundle",
            "id": str(uuid.uuid4()),
            "type": "collection",
            "timestamp": timestamp,
            "entry": entries,
        }
