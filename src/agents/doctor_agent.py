"""Doctor Agent - Clinical decision support from compressed patient state."""

from __future__ import annotations


class DoctorAgent:
    """Receives a compressed patient state (JSON only, never raw text)
    and produces a mock clinical recommendation."""

    # Protocol-specific treatment plans (simulates MedGemma-7b output)
    _PLANS: dict[str, dict] = {
        "Trauma": {
            "immediate_actions": [
                "Secure Airway (C-spine precautions)",
                "2x Large Bore IV Access",
                "Administer 1L Normal Saline bolus",
                "Apply direct pressure to active bleeding",
            ],
            "imaging": [
                "CT Trauma Pan-Scan",
                "Chest X-Ray (portable)",
                "Pelvis X-Ray",
            ],
            "consults": [
                "Trauma Surgery",
                "Orthopaedics (if fracture suspected)",
            ],
        },
        "Neurology": {
            "immediate_actions": [
                "Call Code Stroke",
                "Obtain IV Access",
                "Check Blood Glucose",
                "NIH Stroke Scale Assessment",
            ],
            "imaging": [
                "CT Head non-contrast (STAT)",
                "CT Angiography Head & Neck",
            ],
            "consults": [
                "Neurology",
                "Interventional Radiology (if LVO suspected)",
            ],
        },
        "Cardiology": {
            "immediate_actions": [
                "12-Lead ECG (STAT)",
                "Administer Aspirin 325 mg PO",
                "Establish IV Access",
                "Initiate ACLS Protocol",
                "Continuous cardiac monitoring",
            ],
            "imaging": [
                "Chest X-Ray",
                "Point-of-Care Echocardiogram",
            ],
            "consults": [
                "Cardiology",
                "Cardiac Catheterisation Lab (if STEMI)",
            ],
        },
    }

    _DEFAULT_PLAN: dict = {
        "immediate_actions": [
            "Complete primary assessment (ABCDE)",
            "Establish IV Access",
            "Continuous vital-sign monitoring",
        ],
        "imaging": [
            "As clinically indicated",
        ],
        "consults": [
            "Attending Physician review",
        ],
    }

    def generate_plan(self, protocol_name: str, patient_data: dict) -> dict:
        """Generate a protocol-specific clinical plan (simulates MedGemma-7b).

        Args:
            protocol_name: The active protocol (e.g. 'Trauma', 'Cardiology').
            patient_data: Compressed patient state dictionary.

        Returns:
            A dictionary with keys ``immediate_actions``, ``imaging``, and
            ``consults``.
        """
        for key, plan in self._PLANS.items():
            if key in protocol_name:
                return dict(plan)
        return dict(self._DEFAULT_PLAN)

    def diagnose(self, state: dict) -> str:
        """Generate a mock medical recommendation from a compressed state.

        Args:
            state: A compressed patient_state dictionary produced by NurseAgent.

        Returns:
            A string containing the mock clinical recommendation.
        """
        vitals = state.get("vitals", {})
        hr = vitals.get("hr")
        temp = vitals.get("temp")
        bp = vitals.get("bp")
        complaint = state.get("chief_complaint", "unspecified symptoms")
        medication = state.get("medication")

        findings = []
        if hr and hr > 100:
            findings.append(f"elevated HR ({hr} bpm)")
        if temp and temp >= 38.0:
            findings.append(f"fever ({temp}°C)")
        if bp:
            systolic = int(bp.split("/")[0])
            if systolic >= 140:
                findings.append(f"hypertension (BP {bp})")

        if not findings:
            summary = "Vitals within normal limits."
        else:
            summary = "Noted: " + ", ".join(findings) + "."

        recommendation = (
            f"[MedGemma Assessment]\n"
            f"  Chief Complaint: {complaint}\n"
            f"  {summary}\n"
        )

        if medication:
            recommendation += f"  Current Medication: {medication}\n"

        if findings:
            recommendation += (
                "  Recommendation: Monitor closely, consider further workup "
                "and supportive care."
            )
        else:
            recommendation += (
                "  Recommendation: Continue current management, "
                "routine follow-up advised."
            )

        return recommendation
