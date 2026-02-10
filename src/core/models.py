"""Pydantic models for CompText patient state representation."""

from __future__ import annotations

import json
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
