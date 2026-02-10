"""MedGemma x CompText — Streamlit Dashboard.

Run with:
    streamlit run dashboard.py
"""

import streamlit as st
import tiktoken

from src.agents.doctor_agent import DoctorAgent
from src.agents.nurse_agent import NurseAgent
from src.agents.triage_agent import TriageAgent

_enc = tiktoken.get_encoding("cl100k_base")

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
    state_dict = patient_state.model_dump()

    # --- Active Codex Banner ---
    meta = patient_state.meta
    protocol = meta.get("active_protocol", "General")

    if "Cardiology" in protocol:
        st.error(f"🚨 ACTIVE CODEX: {protocol}")
    elif "Respiratory" in protocol:
        st.warning(f"🚨 ACTIVE CODEX: {protocol}")
    elif "Neurology" in protocol:
        st.error(f"🚨 ACTIVE CODEX: {protocol}")
    elif "Trauma" in protocol:
        st.error(f"🚨 ACTIVE CODEX: {protocol}")
    else:
        st.info(f"ℹ️ ACTIVE CODEX: {protocol}")

    # --- Triage Priority ---
    triage_agent = TriageAgent()
    priority_score = triage_agent.assess(patient_state)
    st.metric("Triage Priority", priority_score)

    # --- Results columns ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Compressed Patient State")
        st.json(state_dict)

    with col2:
        st.subheader("Doctor Agent Response")
        doctor = DoctorAgent()
        recommendation = doctor.diagnose(state_dict)
        st.code(recommendation, language="text")

    # --- Token comparison (tiktoken cl100k_base) ---
    raw_tokens = max(1, len(_enc.encode(raw_text)))
    compressed_json = patient_state.to_compressed_json()
    compressed_tokens = max(1, len(_enc.encode(compressed_json)))

    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Raw Tokens (tiktoken)", raw_tokens)
    m2.metric("Compressed Tokens (tiktoken)", compressed_tokens)
    m3.metric("Reduction", f"{100 - (compressed_tokens / raw_tokens * 100):.0f}%")
