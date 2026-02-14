"""Doctor Agent - Clinical decision support from compressed patient state."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    import torch

    _TORCH_AVAILABLE = True
except ImportError:
    _TORCH_AVAILABLE = False

# ---------------------------------------------------------------------------
# GPU-accelerated Doctor (PaliGemma) — loaded lazily when CUDA is available
# ---------------------------------------------------------------------------

_transformers_doctor_instance: TransformersDoctor | None = None


def get_transformers_doctor() -> TransformersDoctor | None:
    """Return a singleton TransformersDoctor if a GPU is available, else None."""
    global _transformers_doctor_instance
    if _transformers_doctor_instance is not None:
        return _transformers_doctor_instance

    if not _TORCH_AVAILABLE or not torch.cuda.is_available():
        return None

    _transformers_doctor_instance = TransformersDoctor()
    return _transformers_doctor_instance


class TransformersDoctor:
    """Real AI doctor using google/paligemma-3b-pt-224 (multimodal).

    Only instantiated when ``torch.cuda.is_available()`` is True.
    Uses 4-bit quantisation via *bitsandbytes* when the library is present.
    """

    MODEL_ID = "google/paligemma-3b-pt-224"

    def __init__(self) -> None:
        from transformers import AutoProcessor, PaliGemmaForConditionalGeneration

        quantization_config = None
        try:
            from transformers import BitsAndBytesConfig

            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
            )
            logger.info("Loading %s with 4-bit quantisation", self.MODEL_ID)
        except ImportError:
            logger.info(
                "bitsandbytes not found – loading %s at full precision",
                self.MODEL_ID,
            )

        self.processor = AutoProcessor.from_pretrained(self.MODEL_ID)
        self.model = PaliGemmaForConditionalGeneration.from_pretrained(
            self.MODEL_ID,
            quantization_config=quantization_config,
            device_map="auto",
        )

    def diagnose(
        self, context_text: str, image_path: str | None = None
    ) -> str:
        """Run inference on text (and optionally an image).

        Args:
            context_text: Clinical context / prompt.
            image_path: Optional path to a medical image (e.g. X-ray).

        Returns:
            Generated text from the model.
        """
        from PIL import Image

        image = None
        if image_path:
            image = Image.open(image_path).convert("RGB")

        inputs = self.processor(
            text=context_text,
            images=image,
            return_tensors="pt",
        ).to(self.model.device)

        with torch.inference_mode():
            output_ids = self.model.generate(**inputs, max_new_tokens=256)

        return self.processor.decode(output_ids[0], skip_special_tokens=True)


# ---------------------------------------------------------------------------
# Mock / Edge Doctor (CPU fallback)
# ---------------------------------------------------------------------------


class DoctorAgent:
    """Receives a compressed patient state (JSON only, never raw text)
    and produces a clinical recommendation.

    When a GPU is available and ML dependencies are installed the agent
    delegates to ``TransformersDoctor``; otherwise it falls back to
    deterministic rule-based logic (Edge Simulation Mode).
    """

    def __init__(self) -> None:
        self._ai_doctor = get_transformers_doctor()
        if self._ai_doctor is None:
            logger.warning(
                "Running in Edge Simulation Mode – no GPU detected or ML "
                "libraries missing.  Using rule-based fallback."
            )

    def diagnose(self, state: dict) -> str:
        """Generate a medical recommendation from a compressed state.

        Args:
            state: A compressed patient_state dictionary produced by NurseAgent.

        Returns:
            A string containing the clinical recommendation.
        """
        # --- AI path (GPU) ---
        if self._ai_doctor is not None:
            context = self._build_prompt(state)
            return self._ai_doctor.diagnose(context)

        # --- Fallback mock path (CPU / Edge) ---
        return self._mock_diagnose(state)

    # -- helpers ----------------------------------------------------------

    @staticmethod
    def _build_prompt(state: dict) -> str:
        complaint = state.get("chief_complaint", "unspecified symptoms")
        vitals = state.get("vitals", {})
        parts = [f"Patient presents with {complaint}."]
        if vitals.get("hr"):
            parts.append(f"Heart rate: {vitals['hr']} bpm.")
        if vitals.get("bp"):
            parts.append(f"Blood pressure: {vitals['bp']}.")
        if vitals.get("temp"):
            parts.append(f"Temperature: {vitals['temp']}°C.")
        med = state.get("medication")
        if med:
            parts.append(f"Current medication: {med}.")
        parts.append("Provide a clinical assessment and recommendation.")
        return " ".join(parts)

    @staticmethod
    def _mock_diagnose(state: dict) -> str:
        vitals = state.get("vitals", {})
        hr = vitals.get("hr")
        temp = vitals.get("temp")
        bp = vitals.get("bp")
        complaint = state.get("chief_complaint", "unspecified symptoms")
        medication = state.get("medication")

        findings: list[str] = []
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
