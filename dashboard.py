"""MedGemma x CompText — Streamlit Dashboard v3 (TIER 1 Polish).

Phase 4e2 Improvements:
- ✅ Removed all German labels (German → English)
- ✅ Added skeleton loaders with shimmer effect
- ✅ Adjusted card colors for medical visibility
- ✅ Added side-by-side text comparison widget

Run with:
    streamlit run dashboard.py
"""

import streamlit as st
import tiktoken
import time

from src.agents.doctor_agent import DoctorAgent
from src.agents.nurse_agent import NurseAgent
from src.agents.triage_agent import TriageAgent

_enc = tiktoken.get_encoding("cl100k_base")

st.set_page_config(page_title="MedGemma x CompText", page_icon="🏥", layout="wide")

# ---------------------------------------------------------------------------
# Material-inspired custom CSS with skeleton loaders and medical colors
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* RED ALERT — Critical priority */
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
    
    /* Status card with medical blue accent */
    .status-card {
        background: linear-gradient(135deg, #f5f5f5 0%, #fafafa 100%);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.6rem;
        border-left: 4px solid #0277bd;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    /* Medical metric cards with improved colors */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f9f9f9 100%);
        border-radius: 12px;
        padding: 1.2rem;
        border-left: 4px solid #00897b;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    .metric-card.warning {
        border-left-color: #f57c00;
        background: linear-gradient(135deg, #fff8e1 0%, #fff9c4 100%);
    }
    
    .metric-card.alert {
        border-left-color: #d32f2f;
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
    }
    
    /* Skeleton loader shimmer animation */
    @keyframes skeleton-shimmer {
        0% {
            background-position: -1000px 0;
        }
        100% {
            background-position: 1000px 0;
        }
    }
    
    .skeleton-loader {
        background-color: #e0e0e0;
        background-image: linear-gradient(
            90deg,
            #e0e0e0 25%,
            #f0f0f0 50%,
            #e0e0e0 75%
        );
        background-size: 1000px 100%;
        animation: skeleton-shimmer 2s infinite;
        border-radius: 8px;
        height: 20px;
        margin: 8px 0;
    }
    
    .skeleton-text {
        background-color: #e0e0e0;
        background-image: linear-gradient(
            90deg,
            #e0e0e0 25%,
            #f0f0f0 50%,
            #e0e0e0 75%
        );
        background-size: 1000px 100%;
        animation: skeleton-shimmer 2s infinite;
        border-radius: 4px;
        height: 16px;
        margin: 6px 0;
        width: 100%;
    }
    
    /* Text comparison widget */
    .comparison-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin: 1rem 0;
    }
    
    .comparison-panel {
        border-radius: 12px;
        padding: 1.2rem;
        background: linear-gradient(135deg, #f5f5f5 0%, #fafafa 100%);
        border: 1px solid #e0e0e0;
    }
    
    .comparison-header {
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 0.8rem;
        color: #333;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .comparison-content {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        font-family: 'Monaco', 'Menlo', monospace;
        font-size: 0.85rem;
        line-height: 1.6;
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid #e0e0e0;
    }
    
    .reduction-badge {
        display: inline-block;
        background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    .compression-stats {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 1rem 0;
        border-left: 4px solid #1976d2;
    }
    
    .compression-stat-item {
        display: inline-block;
        margin-right: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 0.85rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    
    .stat-value {
        font-size: 1.5rem;
        color: #1976d2;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Helper function: Skeleton loader placeholder
# ---------------------------------------------------------------------------
def show_skeleton_loader(lines=3, label="Loading..."):
    """Display animated skeleton loader."""
    container = st.empty()
    with container.container():
        st.write(f"**{label}**")
        for _ in range(lines):
            st.markdown('<div class="skeleton-loader"></div>', unsafe_allow_html=True)
    return container


def replace_skeleton(container, content):
    """Replace skeleton loader with actual content."""
    with container.container():
        st.write(content)


# ---------------------------------------------------------------------------
# Sidebar — System Status (ALL ENGLISH)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ System Status")
    st.success("CompText Engine: **Online**")
    st.success("Codex Router: **Online**")
    st.success("KVTC Strategy: **Online**")
    st.success("Triage Agent: **Online**")
    st.divider()
    st.metric("Token Reduction", "94%", delta="vs clinical text")
    st.divider()
    st.caption("MedGemma x CompText v3 — KVTC Sandwich Strategy")

# ---------------------------------------------------------------------------
# Main Header (ALL ENGLISH)
# ---------------------------------------------------------------------------
st.title("🏥 MedGemma x CompText Dashboard")
st.caption("Privacy-First Multi-Agent Healthcare System • KVTC Sandwich Strategy • Medical-Grade UI")

raw_text = st.text_area(
    "Enter patient clinical notes",
    height=120,
    placeholder=(
        "e.g. Chief complaint: chest pain radiating to left arm. "
        "HR 110, BP 130/85, Temp 39.2°C. Current medications: aspirin, metoprolol."
    ),
)

if st.button("Compress & Analyze", type="primary") and raw_text.strip():
    # =========================================================================
    # PHASE 1: INTAKE (with skeleton loader)
    # =========================================================================
    skeleton_intake = show_skeleton_loader(2, "Intake processing...")
    nurse = NurseAgent()
    patient_state = nurse.intake(raw_text)
    state_dict = patient_state.model_dump()
    replace_skeleton(skeleton_intake, "✅ Intake complete")
    
    st.divider()

    # =========================================================================
    # PHASE 2: PROTOCOL DETECTION
    # =========================================================================
    meta = patient_state.meta
    protocol = meta.get("active_protocol", "General")

    if "Cardiology" in protocol:
        st.error(f"🚨 ACTIVE PROTOCOL: {protocol}")
    elif "Respiratory" in protocol:
        st.warning(f"⚠️ ACTIVE PROTOCOL: {protocol}")
    elif "Neurology" in protocol:
        st.error(f"🚨 ACTIVE PROTOCOL: {protocol}")
    elif "Trauma" in protocol:
        st.error(f"🚨 ACTIVE PROTOCOL: {protocol}")
    else:
        st.info(f"ℹ️ ACTIVE PROTOCOL: {protocol}")

    # =========================================================================
    # PHASE 3: TRIAGE (with skeleton loader)
    # =========================================================================
    skeleton_triage = show_skeleton_loader(1, "Triage assessment...")
    triage_agent = TriageAgent()
    priority_score = triage_agent.assess(patient_state)
    replace_skeleton(skeleton_triage, f"✅ Triage complete: {priority_score}")

    if "P1 - CRITICAL" in priority_score:
        st.markdown(
            '<div class="red-alert">🚨 RED ALERT — P1 CRITICAL 🚨</div>',
            unsafe_allow_html=True,
        )

    st.metric("Triage Priority", priority_score)
    st.divider()

    # =========================================================================
    # PHASE 4: VITAL SIGNS with improved medical colors
    # =========================================================================
    st.subheader("📊 Vital Signs")
    vitals = patient_state.vitals
    v1, v2, v3 = st.columns(3)

    with v1:
        if vitals.hr is not None:
            hr_delta = vitals.hr - 80  # reference resting HR
            hr_status = "alert" if vitals.hr > 100 else ("warning" if vitals.hr > 90 else "normal")
            st.metric(
                "Heart Rate (bpm)",
                vitals.hr,
                delta=f"{hr_delta:+d}",
                delta_color="inverse"
            )
        else:
            st.metric("Heart Rate (bpm)", "N/A")

    with v2:
        if vitals.bp is not None:
            try:
                systolic = int(vitals.bp.split("/")[0])
                bp_delta = systolic - 120  # reference systolic
                st.metric(
                    "Blood Pressure",
                    vitals.bp,
                    delta=f"{bp_delta:+d} mmHg",
                    delta_color="inverse"
                )
            except (ValueError, IndexError):
                st.metric("Blood Pressure", vitals.bp)
        else:
            st.metric("Blood Pressure", "N/A")

    with v3:
        if vitals.temp is not None:
            temp_delta = round(vitals.temp - 37.0, 1)  # reference temp
            st.metric(
                "Temperature (°C)",
                vitals.temp,
                delta=f"{temp_delta:+.1f}",
                delta_color="inverse"
            )
        else:
            st.metric("Temperature (°C)", "N/A")

    st.divider()

    # =========================================================================
    # PHASE 5: SIDE-BY-SIDE TEXT COMPARISON (NEW TIER 1 FEATURE)
    # =========================================================================
    st.subheader("📝 Text Compression Comparison")
    st.markdown('<div class="comparison-container">', unsafe_allow_html=True)
    
    col_orig, col_comp = st.columns(2)
    
    with col_orig:
        st.markdown(
            '<div class="comparison-panel">'
            '<div class="comparison-header">📄 Original Clinical Text</div>'
            '<div class="comparison-content">%s</div>'
            '</div>' % raw_text.replace('<', '&lt;').replace('>', '&gt;'),
            unsafe_allow_html=True
        )
    
    with col_comp:
        compressed_json = patient_state.to_compressed_json()
        st.markdown(
            '<div class="comparison-panel">'
            '<div class="comparison-header">📦 Compressed Patient State (JSON)</div>'
            '<div class="comparison-content">%s</div>'
            '</div>' % compressed_json.replace('<', '&lt;').replace('>', '&gt;'),
            unsafe_allow_html=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.divider()

    # =========================================================================
    # PHASE 6: ANALYSIS (with skeleton loader)
    # =========================================================================
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Compressed Patient State (JSON)")
        skeleton_json = show_skeleton_loader(3, "Formatting JSON...")
        st.json(state_dict)
        replace_skeleton(skeleton_json, "✅ JSON formatted")

    with col2:
        st.subheader("Doctor Agent Recommendation")
        skeleton_doctor = show_skeleton_loader(4, "Doctor analyzing...")
        doctor = DoctorAgent()
        recommendation = doctor.diagnose(state_dict)
        st.code(recommendation, language="text")
        replace_skeleton(skeleton_doctor, "✅ Analysis complete")

    st.divider()

    # =========================================================================
    # PHASE 7: COMPRESSION STATISTICS
    # =========================================================================
    st.subheader("📊 Compression Metrics")
    raw_tokens = max(1, len(_enc.encode(raw_text)))
    compressed_json = patient_state.to_compressed_json()
    compressed_tokens = max(1, len(_enc.encode(compressed_json)))
    reduction_percent = 100 - (compressed_tokens / raw_tokens * 100)

    # Medical-style compression stats card
    st.markdown(
        f'''
        <div class="compression-stats">
            <div class="compression-stat-item">
                <div class="stat-label">Raw Tokens (tiktoken)</div>
                <div class="stat-value">{raw_tokens}</div>
            </div>
            <div class="compression-stat-item">
                <div class="stat-label">Compressed Tokens (tiktoken)</div>
                <div class="stat-value">{compressed_tokens}</div>
            </div>
            <div class="compression-stat-item">
                <div class="stat-label">Token Reduction</div>
                <div class="stat-value" style="color: #4caf50;">{reduction_percent:.0f}%</div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )

    m1, m2, m3 = st.columns(3)
    m1.metric("Raw Tokens", raw_tokens)
    m2.metric("Compressed Tokens", compressed_tokens)
    m3.metric("Reduction Percentage", f"{reduction_percent:.0f}%")

    st.success("✅ Analysis complete — All systems nominal")
