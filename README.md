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
data leaves the edge device. Combined with Google's **MedGemma** foundation model,
this architecture delivers:

| Benefit | Detail |
|---|---|
| 🔒 **Privacy by Design** | Raw text never leaves the device; only anonymised JSON is sent to the model. |
| ⚡ **94 % Token Reduction** | Fewer tokens → faster inference, lower cost, and the ability to run on constrained hardware. |
| 🤖 **Multi-Agent Workflow** | A *Nurse Agent* handles intake & compression; a *Doctor Agent* handles diagnosis — each with a single responsibility. |
| 🏥 **Edge-Ready** | Small enough to run on tablets in rural clinics or field hospitals. |

This project is our submission for the **MedGemma Impact Challenge** on Kaggle. We
believe that the biggest barrier to deploying medical AI at scale is not model
quality — it is **context efficiency**. CompText removes that barrier.

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the interactive demo
python demo_cli.py
```

### Example input

```
Patient has fever 39C, HR 110, BP 130/85. Chief complaint: chest pain. Medication: aspirin.
```

---

## Project Structure

```
├── demo_cli.py              # Rich terminal UI demo
├── requirements.txt
├── src/
│   ├── core/
│   │   └── comptext.py      # CompText compression protocol
│   └── agents/
│       ├── nurse_agent.py    # Intake & compression agent
│       └── doctor_agent.py   # Diagnosis agent
└── tests/
    └── test_comptext.py      # Unit tests
```

---

## How It Works

1. **User enters symptoms** in plain English.
2. The **Nurse Agent** compresses the text via `CompTextProtocol.compress()`.
3. A token-comparison table shows the savings.
4. The **Doctor Agent** receives *only* the compressed JSON and returns a clinical recommendation.

---

## License

This project is provided for the MedGemma Impact Challenge evaluation only.