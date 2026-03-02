# Yoga Practice Guide — Domain Q&A Chatbot

A domain-specific chatbot that answers questions about **yoga practice**, covering asanas (poses) and pranayama (breathwork techniques).

## What it covers

- **Asanas** — Sanskrit and English names, alignment cues, physical benefits, common mistakes
- **Pose modifications** — variations for different body types and experience levels
- **General contraindications** — which poses to approach carefully given physical attributes
- **Pranayama** — technique names, breath ratios, durations, and practical effects on the body
- **Breathwork + poses** — how breathwork complements specific poses or sequences
- **Sequencing** — what poses and breath techniques pair well together

## Out of scope

- Religious dimensions of yoga
- Injuries requiring medical help 
- General fitness programming or physical therapy
- Mental health guidance

## Safety handling

Any question containing keywords suggesting pain, injury, medical conditions, pregnancy, or post-surgery recovery is intercepted by a Python backstop **before** reaching the LLM and redirected to a qualified yoga instructor or healthcare professional.

---

## Live URL

https://yoga-chatbot-962383938047.us-central1.run.app

---

## Running locally

### Prerequisites

1. A Google Cloud project with Vertex AI enabled
2. Application Default Credentials configured (`gcloud auth application-default login`)

### Setup

Create a `.env` file in the project root:

```
VERTEXAI_PROJECT=your-project-id
VERTEXAI_LOCATION=us-central1
```

Install dependencies and start the server:

```bash
uv run python app.py
```

The app runs at `http://localhost:8000`.

---

## Running evaluations

```bash
uv run pytest evals/ -v
```

This runs three test suites:

| Suite | Description |
|---|---|
| `test_golden.py` | 10 in-domain golden-reference MaaJ evals (≥6/10 each) |
| `test_rubric.py` | 10 rubric-based MaaJ evals (≥6/10 each) |
| `test_deterministic.py` | 20 deterministic keyword/refusal tests across 3 categories, with per-category pass rates |


