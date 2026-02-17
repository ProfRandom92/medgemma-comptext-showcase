"""Triage Agent - Priority assessment from compressed patient state."""

from __future__ import annotations

from dataclasses import dataclass

try:
    from src.core.models import PatientState
except ImportError:
    from core.models import PatientState  # type: ignore[no-redef]


@dataclass
class TriageResult:
    """Structured triage result."""

    priority_level: str   # "P1", "P2", "P3"
    priority_name: str    # "CRITICAL", "URGENT", "STANDARD"
    reason: str


class TriageAgent:
    """Assigns a triage priority level based on patient state."""

    # ── Thresholds (all tests reference these values) ──────────────────────
    # HR: >= 130 severe (P1 alone), >= 100 critical (needs 2+ for P1, alone P2),
    #      < 40 severe, < 50 critical
    # SBP: >= 170 severe (P1 alone), >= 160 critical (2+ → P1, alone P2),
    #       <= 80 severe, <= 90 critical
    # DBP: >= 100 critical
    # Temp: >= 40.0 severe (P1 alone), >= 38.0 critical (2+ → P1, alone P2),
    #        <= 34.9 critical

    def triage(self, patient_state: PatientState) -> TriageResult:
        """Return structured TriageResult with priority_level P1/P2/P3.

        Classification:
        - P1 CRITICAL: protocol override OR any severe flag OR 2+ critical flags
        - P2 URGENT:   1 critical flag only
        - P3 STANDARD: no flags
        """
        protocol = patient_state.meta.get("active_protocol", "")
        vitals = patient_state.vitals

        # Protocol-based override → always P1
        critical_protocols = ("Cardiology", "Trauma", "Neurology")
        if any(p in protocol for p in critical_protocols):
            return TriageResult("P1", "CRITICAL", f"Active protocol: {protocol}")

        # Parse BP
        systolic: int | None = None
        diastolic: int | None = None
        if vitals.bp:
            try:
                parts = vitals.bp.split("/")
                systolic = int(parts[0])
                if len(parts) >= 2:
                    diastolic = int(parts[1])
            except (ValueError, IndexError):
                pass

        severe_flags: list[str] = []   # single flag → P1
        critical_flags: list[str] = [] # 2+ → P1; 1 alone → P2

        # ── Heart rate ────────────────────────────────────────────────────
        if vitals.hr is not None:
            hr = vitals.hr
            if hr >= 130:
                severe_flags.append(f"HR {hr} (severe tachycardia)")
            elif hr >= 100:
                critical_flags.append(f"HR {hr} (tachycardia)")
            elif hr < 40:
                severe_flags.append(f"HR {hr} (severe bradycardia)")
            elif hr < 50:
                critical_flags.append(f"HR {hr} (bradycardia)")

        # ── Systolic BP ───────────────────────────────────────────────────
        if systolic is not None:
            if systolic >= 170:
                severe_flags.append(f"SBP {systolic} (hypertensive crisis)")
            elif systolic >= 160:
                critical_flags.append(f"SBP {systolic} (critical hypertension)")
            elif systolic <= 80:
                severe_flags.append(f"SBP {systolic} (severe hypotension)")
            elif systolic <= 90:
                critical_flags.append(f"SBP {systolic} (hypotension)")

        # ── Diastolic BP ──────────────────────────────────────────────────
        if diastolic is not None and diastolic >= 100:
            critical_flags.append(f"DBP {diastolic} (elevated)")

        # ── Temperature ───────────────────────────────────────────────────
        if vitals.temp is not None:
            temp = vitals.temp
            if temp >= 40.0:
                severe_flags.append(f"Temp {temp} (hyperpyrexia)")
            elif temp >= 38.0:
                critical_flags.append(f"Temp {temp} (fever)")
            elif temp <= 34.9:
                critical_flags.append(f"Temp {temp} (hypothermia)")

        # Respiratory protocol → at least P2
        if "Respiratory" in protocol and not severe_flags and not critical_flags:
            critical_flags.append("Respiratory protocol active")

        # ── Classify ──────────────────────────────────────────────────────
        if severe_flags or len(critical_flags) >= 2:
            reason = "; ".join(severe_flags + critical_flags)
            return TriageResult("P1", "CRITICAL", reason)

        if critical_flags:
            return TriageResult("P2", "URGENT", critical_flags[0])

        return TriageResult("P3", "STANDARD", "All vitals within normal limits")

    def assess(self, patient_state: PatientState) -> str:
        """Legacy string interface — backward compatible with existing tests."""
        result = self.triage(patient_state)
        icons = {"P1": "\U0001f534", "P2": "\U0001f7e1", "P3": "\U0001f7e2"}
        icon = icons.get(result.priority_level, "\U0001f7e2")
        return f"{icon} {result.priority_level} - {result.priority_name}"
