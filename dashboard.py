"""MedGemma x CompText — Streamlit Dashboard.

Run with:
    streamlit run dashboard.py
"""

import json

import streamlit as st

from src.agents.doctor_agent import DoctorAgent
from src.agents.nurse_agent import NurseAgent

st.set_page_config(page_title="MedGemma x CompText", page_icon="🏥", layout="wide")

st.title("🏥 MedGemma x CompText Dashboard")
st.caption("Privacy-First Multi-Agent Healthcare System")

raw_text = st.text_area(
    "Enter patient symptoms",
    height=120,
    placeholder=(
        "e.g. Chief complaint: chest pain radiating to left arm. "
        "HR 110, BP 130/85, Temp 39.2C. Medication: aspirin."
    ),
)

if st.button("Compress & Analyse", type="primary") and raw_text.strip():
    nurse = NurseAgent()
    patient_state = nurse.intake(raw_text)

    # --- Active Codex Banner ---
    meta = patient_state.get("meta", {})
    protocol = meta.get("active_protocol", "General")

    if "Cardiology" in protocol:
        st.error(f"🚨 ACTIVE CODEX: {protocol}")
    elif "Respiratory" in protocol:
        st.warning(f"🚨 ACTIVE CODEX: {protocol}")
    else:
        st.info(f"ℹ️ ACTIVE CODEX: {protocol}")

    # --- Results columns ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Compressed Patient State")
        st.json(patient_state)

    with col2:
        st.subheader("Doctor Agent Response")
        doctor = DoctorAgent()
        recommendation = doctor.diagnose(patient_state)
        st.code(recommendation, language="text")

    # --- Token comparison ---
    raw_tokens = max(1, len(raw_text) // 4)
    compressed_json = json.dumps(patient_state, indent=2)
    compressed_tokens = max(1, len(compressed_json) // 4)

    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Raw Tokens", raw_tokens)
    m2.metric("Compressed Tokens", compressed_tokens)
    m3.metric("Reduction", f"{100 - (compressed_tokens / raw_tokens * 100):.0f}%")
