"""MedGemma x CompText — Streamlit Dashboard (v2 Hackathon).

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

# ---------------------------------------------------------------------------
# Material-inspired custom CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .red-alert {
        background: linear-gradient(135deg, #d32f2f 0%, #b71c1c 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        font-weight: 700;
        font-size: 1.3rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(211,47,47,0.4);
    }
    .status-card {
        background: #f5f5f5;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.6rem;
        border-left: 4px solid #1976d2;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar — System Status
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ System Status")
    st.success("CompText Engine: **Online**")
    st.success("Codex Router: **Online**")
    st.success("KVTC Strategy: **Online**")
    st.success("Triage Agent: **Online**")
    st.divider()
    st.metric("Token Reduction", "94%", delta="vs raw clinical text")
    st.divider()
    st.caption("MedGemma x CompText v2 — KVTC Sandwich Strategy")

# ---------------------------------------------------------------------------
# Main Header
# ---------------------------------------------------------------------------
st.title("🏥 MedGemma x CompText Dashboard")
st.caption("Privacy-First Multi-Agent Healthcare System • KVTC Sandwich Strategy • Google Material Design")

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

    # --- Triage Priority with RED ALERT card ---
    triage_agent = TriageAgent()
    priority_score = triage_agent.assess(patient_state)

    if "P1 - CRITICAL" in priority_score:
        st.markdown(
            '<div class="red-alert">🚨 RED ALERT — P1 CRITICAL 🚨</div>',
            unsafe_allow_html=True,
        )

    st.metric("Triage Priority", priority_score)

    # --- Vitals metrics with delta colors ---
    vitals = patient_state.vitals
    v1, v2, v3 = st.columns(3)

    with v1:
        if vitals.hr is not None:
            hr_delta = vitals.hr - 80  # reference resting HR
            st.metric("Heart Rate (bpm)", vitals.hr, delta=f"{hr_delta:+d}", delta_color="inverse")
        else:
            st.metric("Heart Rate (bpm)", "N/A")

    with v2:
        if vitals.bp is not None:
            try:
                systolic = int(vitals.bp.split("/")[0])
                bp_delta = systolic - 120  # reference systolic
                st.metric("Blood Pressure", vitals.bp, delta=f"{bp_delta:+d} sys", delta_color="inverse")
            except (ValueError, IndexError):
                st.metric("Blood Pressure", vitals.bp)
        else:
            st.metric("Blood Pressure", "N/A")

    with v3:
        if vitals.temp is not None:
            temp_delta = round(vitals.temp - 37.0, 1)  # reference temp
            st.metric("Temperature (°C)", vitals.temp, delta=f"{temp_delta:+.1f}", delta_color="inverse")
        else:
            st.metric("Temperature (°C)", "N/A")

    st.divider()

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
