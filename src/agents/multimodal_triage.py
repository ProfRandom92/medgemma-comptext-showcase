"""Multimodal Triage — X-ray + symptom analysis via PaliGemma.

Uses the *same* TransformersDoctor singleton to avoid loading the model
twice in GPU-constrained environments.
"""

from __future__ import annotations

import logging

from src.agents.doctor_agent import get_transformers_doctor

logger = logging.getLogger(__name__)


def analyze_xray(image_path: str, symptoms: str) -> str:
    """Analyse a medical image alongside symptom text.

    Args:
        image_path: Path to an X-ray (or other medical image) file.
        symptoms: Free-text clinical symptoms to include in the prompt.

    Returns:
        A string with the model's analysis, or a fallback message when
        no GPU / ML libraries are available.
    """
    doctor = get_transformers_doctor()

    if doctor is None:
        logger.warning(
            "Multimodal triage unavailable — running in Edge Simulation Mode."
        )
        return (
            f"[Edge Simulation] Multimodal analysis not available (no GPU). "
            f"Symptoms noted: {symptoms}. "
            f"Image: {image_path}. Manual review required."
        )

    prompt = (
        f"Analyze this medical image. Patient symptoms: {symptoms}. "
        "Provide observations and a preliminary assessment."
    )
    return doctor.diagnose(prompt, image_path=image_path)
