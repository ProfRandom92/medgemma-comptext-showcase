# MedGemma x CompText: Solving the Context Bottleneck

> **A privacy-first, multi-agent healthcare system that compresses patient data by 94% before it ever reaches the LLM.**

---

## Mission Statement

Healthcare AI has a context problem. Large Language Models are powerful diagnostic
reasoners, but feeding them raw Electronic Health Records is **expensive, slow, and
a privacy risk**. Every extra token transmitted increases cost, latency, and the
surface area for data leakage.

**CompText** is our answer. It is a lightweight compression protocol that distils
free-form clinical narratives into structured, minimal-token JSON — *before* the
data leaves the edge device. A **Modular Codex System** routes each case through
domain-specific extractors — **Cardiology**, **Neurology**, **Trauma**, and
**Respiratory** — so the compressed output retains specialist-grade detail without
a single extra token. Combined with Google's **MedGemma** foundation model, this
architecture delivers:

| Benefit | Detail |
|---|---|
| 🔒 **Privacy by Design** | Raw text never leaves the device; only anonymised JSON is sent to the model. |
| ⚡ **94% Token Reduction** | Fewer tokens → faster inference, lower cost, and the ability to run on constrained hardware. |
| 🤖 **Multi-Agent Workflow** | A *Nurse Agent* handles intake & compression; a *Doctor Agent* handles diagnosis — each with a single responsibility. |
| 🧠 **Intelligent Triage** | A *Triage Agent* assigns P1/P2/P3 priority automatically based on protocol and vitals. |
| 🏥 **Edge-Ready** | Small enough to run on tablets in rural clinics or field hospitals. |

This project is our submission for the **MedGemma Impact Challenge** on Kaggle. We
believe that the biggest barrier to deploying medical AI at scale is not model
quality — it is **context efficiency**. CompText removes that barrier.

---

## 🧠 Intelligent Triage

The **TriageAgent** evaluates every compressed patient state and assigns a priority
level so clinicians see the most urgent cases first — without waiting for a full
LLM round-trip.

| Priority | Trigger | Example |
|---|---|---|
| 🔴 **P1 — CRITICAL** | Cardiology / Neurology / Trauma protocol, HR > 120, or systolic BP > 160 | Stroke with left-side weakness |
| 🟡 **P2 — URGENT** | Respiratory protocol or temperature > 39 °C | Asthma exacerbation with fever |
| 🟢 **P3 — STANDARD** | All other cases with stable vitals | Routine checkup, mild headache |

Because triage runs on the *compressed* state (not raw text), it adds **zero extra
tokens** to the LLM call and completes in microseconds on any device.

---

## Standard LLM Intake vs CompText Multi-Agent Workflow

| | Standard LLM Intake | CompText Multi-Agent Workflow |
|---|---|---|
| **Input** | Raw EHR text (hundreds of tokens) | Structured JSON (~6% of original) |
| **Privacy** | Full patient narrative sent to cloud | Only anonymised fields leave the device |
| **Domain Awareness** | None — model must infer specialty | Codex Router selects Cardiology / Neuro / Trauma / Respiratory automatically |
| **Triage** | Manual or absent | Automatic P1/P2/P3 via TriageAgent |
| **Latency** | High — large prompt, slow inference | Low — minimal tokens, fast response |
| **Cost** | ~$0.06 per 1K tokens (GPT-4 class) | ~$0.004 per call (94% fewer tokens) |
| **Agents** | Monolithic prompt | Nurse → Triage → Doctor pipeline, each with a single responsibility |
| **Extensibility** | Re-prompt the whole model | Add a new `ClinicalModule` subclass and register it in the `CodexRouter` |

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the interactive CLI demo
python demo_cli.py

# Or launch the Streamlit dashboard
streamlit run dashboard.py

# Run the test suite (44 tests)
python -m pytest tests/ -v
```

### Example input

```
Patient has fever 39C, HR 110, BP 130/85. Chief complaint: chest pain. Medication: aspirin.
```

---

## Project Structure

```
├── demo_cli.py              # Rich terminal UI demo
├── dashboard.py             # Streamlit dashboard with tiktoken metrics
├── requirements.txt
├── src/
│   ├── core/
│   │   ├── models.py        # Pydantic models (Vitals, PatientState)
│   │   ├── comptext.py      # CompText compression protocol
│   │   └── codex.py         # Modular Codex system (Cardiology, Neuro, Trauma, Respiratory)
│   └── agents/
│       ├── nurse_agent.py   # Intake & compression agent
│       ├── triage_agent.py  # P1/P2/P3 priority assessment agent
│       └── doctor_agent.py  # Diagnosis agent
└── tests/
    └── test_comptext.py     # 44 unit tests
```

---

## How It Works

1. **User enters symptoms** in plain English.
2. The **Nurse Agent** compresses the text via `CompTextProtocol.compress()`.
3. The **Codex Router** detects the clinical domain and enriches the state with specialist fields.
4. The **Triage Agent** assigns a P1 / P2 / P3 priority level from the compressed state.
5. A token-comparison table shows the savings.
6. The **Doctor Agent** receives *only* the compressed JSON and returns a clinical recommendation.

---

## License

This project is provided for the MedGemma Impact Challenge evaluation only.