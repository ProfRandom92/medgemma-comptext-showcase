"""Doctor Agent - Clinical decision support from compressed patient state."""


class DoctorAgent:
    """Receives a compressed patient state (JSON only, never raw text)
    and produces a mock clinical recommendation."""

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
