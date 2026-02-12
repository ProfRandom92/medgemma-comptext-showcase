"""Pydantic models for CompText patient state representation."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class Vitals(BaseModel):
    """Patient vital signs."""

    hr: int | None = None
    bp: str | None = None
    temp: float | None = None


class PatientState(BaseModel):
    """Compressed patient state produced by the CompText protocol."""

    chief_complaint: str | None = None
    vitals: Vitals = Field(default_factory=Vitals)
    medication: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)
    specialist_data: dict[str, Any] = Field(default_factory=dict)

    def to_compressed_json(self) -> str:
        """Dump the model as JSON, excluding None fields for high compression."""
        data = self.model_dump(exclude_none=True)
        # Also strip None values inside arbitrary dicts (e.g. specialist_data)
        for key in ("specialist_data", "meta"):
            if key in data and isinstance(data[key], dict):
                data[key] = {k: v for k, v in data[key].items() if v is not None}
        return json.dumps(data)

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
