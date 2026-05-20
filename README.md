# AI-Driven JEE Skill Assessment and SOCA Mentor

Research-oriented MVP for assessing JEE aspirants and generating personalized SOCA analysis: Strengths, Opportunities, Challenges, and Action Plan.

## Architecture

The system follows a modular EdTech AI pipeline:

1. **Questionnaire Layer**: Streamlit collects MCQ‑style, scale‑based, and short‑answer responses.
2. **Feature Extraction Layer**: `scoring/scoring_engine.py` converts responses into normalized academic and behavioral scores.
3. **Multi‑Agent Assessment Layer**: academic, behavioral, wellness, and recommendation agents produce structured JSON outputs.
4. **Knowledge Graph Reasoning Layer**: `kg/knowledge_graph.py` uses NetworkX to infer prerequisite gaps and downstream risk topics.
5. **RAG Layer**: `rag/retrieve.py` embeds a local preparation knowledge base using SentenceTransformers and retrieves advice with FAISS.
6. **LLM SOCA Layer**: `llm/soca_generator.py` uses a HuggingFace text‑generation pipeline when available, with a deterministic fallback.
7. **Dashboard Layer**: `app.py` (Streamlit) presents charts, weak‑topic reasoning, downloadable JSON reports, and feedback capture.
8. **Topic Diagnostic Layer**: `assessment/` generates topic‑wise tests, grades attempts, detects confidence gaps, scores readiness, and builds revision roadmaps.

## React Frontend (New UI)

A modern React version of the dashboard has been added under `react-frontend/`. It provides a high‑fidelity, component‑driven UI that mirrors the functionality of the original Streamlit interface while offering richer interactions, smoother animations, and better visual polish.

### Features
- **Dynamic Metrics & Analytics** with live updates from the FastAPI backend.
- **Subject Mastery & Diagnostic Heatmaps** rendered via Material‑UI cards and custom SVG charts.
- **Contextual RAG Recommendations** (optional) displayed in an accordion.
- **Feedback & Rating** component (renamed from "Reinforcement Loop Validation" to "Feedback").
- **State persistence** using `sessionStorage` so refreshes keep your progress.
- **Responsive design** that works on desktop and tablet screens.

### Prerequisites
- The backend API must be running (see **Backend Setup** below).
- Node.js ≥ 18 and npm (or yarn) installed.

### Setup & Run
```bash
# Install dependencies
cd react-frontend
npm install
# Start development server (default http://localhost:5173)
npm run dev
```
The React app proxies API calls to `http://127.0.0.1:8000` (FastAPI backend). Adjust the proxy target in `vite.config.ts` if needed.

### Build for Production
```bash
npm run build
# Output placed in `dist/` – can be served with any static file server.
```

## Why These AI Components

- **RAG** grounds recommendations in a local, inspectable knowledge base instead of relying only on model memory.
- **Knowledge graphs** make topic dependency reasoning explainable, especially for prerequisite repair.
- **Multi‑agent systems** separate academic, behavioral, wellness, and strategy reasoning so outputs are easier to audit.
- **LLMs** convert structured evidence into concise, motivational SOCA reports while preserving personalization.

## Setup (Backend)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
# Start FastAPI backend
uvicorn backend.api:app --host 127.0.0.1 --port 8000
```
If the HuggingFace model is not available locally, the app still runs using deterministic SOCA generation. This keeps the MVP usable on machines without GPU memory for Phi‑3 Mini or Mistral 7B.

To opt into local HuggingFace generation:
```bash
set USE_LOCAL_LLM=true
uvicorn backend.api:app --reload
```

## Project Structure
```
app.py                # Streamlit dashboard (legacy)
react-frontend/       # Modern React UI
agents/
rag/
kg/
scoring/
llm/
prompts/
data/
requirements.txt
README.md
```

## Sample Output

The included sample response produces:
- PCM score chart
- Topic mastery heatmap
- Topic‑wise diagnostic readiness heatmap
- Confidence vs accuracy graph
- Subject‑wise mastery chart
- Weak topic alerts and revision priority list
- Prerequisite gaps for Rotation, Organic Chemistry, and Integration
- Agent JSON outputs
- SOCA report with actionable two‑week plan
- Downloadable report JSON

## Topic‑Wise Diagnostic Pipeline

The enhanced assessment flow asks each student to mark completed, partially completed, and untouched chapters for Physics, Chemistry, and Mathematics. Completed topics unlock a five‑question diagnostic test with 2 easy, 2 medium, and 1 hard MCQ.

For each completed topic, the system calculates:
- Topic accuracy
- Weighted difficulty handling
- Confidence vs accuracy gap
- Revision freshness and urgency
- Conceptual weakness score
- Average time per question
- Readiness score from `0‑100`

Readiness uses:
```
0.40 * Accuracy
+ 0.20 * Confidence Alignment
+ 0.20 * Revision Freshness
+ 0.20 * Difficulty Handling
```

The resulting topic reports feed the SOCA generator, knowledge graph dependency reasoning, RAG retrieval, and personalized roadmap.

## Screenshots

Add screenshots after running locally:
- `docs/screenshots/questionnaire.png`
- `docs/screenshots/soca_report.png`
- `docs/screenshots/agent_outputs.png`

## Human‑in‑the‑Loop Workflow

The dashboard includes a student usefulness rating and teacher‑editable recommendation box. Feedback is saved to `data/feedback.jsonl`. This can later be used for reinforcement learning or active learning pipelines after proper data governance and review.

## Bonus Features Included

- Adaptive weak‑topic selection through questionnaire controls
- Topic mastery heatmap
- Confidence, accuracy, stress, and discipline comparisons
- HuggingFace Spaces deployment‑ready Streamlit structure
- Optional LLM backend with local deterministic fallback

## HuggingFace Spaces Deployment

1. Create a new Streamlit Space.
2. Upload this repository.
3. Keep `requirements.txt` at the repo root.
4. If using a hosted model, set environment variables or modify `SOCAGenerator` to call an inference endpoint.
5. For CPU Spaces, keep the deterministic fallback enabled or use a small model.

## Future Scope

- Real LangGraph orchestration with state transitions and retry policies
- Teacher dashboard for cohort‑level intervention planning
- PDF report export with branded templates
- Downloadable JSON and PDF reports
- Longitudinal learning analytics across multiple mock tests
- Secure authentication and role‑based access
- Formal validation with teachers and student outcomes
- Privacy‑preserving feedback loops for model improvement


Research-oriented MVP for assessing JEE aspirants and generating personalized SOCA analysis: Strengths, Opportunities, Challenges, and Action Plan.

## Architecture

The system follows a modular EdTech AI pipeline:

1. **Questionnaire Layer**: Streamlit collects MCQ-style, scale-based, and short-answer responses.
2. **Feature Extraction Layer**: `scoring/scoring_engine.py` converts responses into normalized academic and behavioral scores.
3. **Multi-Agent Assessment Layer**: academic, behavioral, wellness, and recommendation agents produce structured JSON outputs.
4. **Knowledge Graph Reasoning Layer**: `kg/knowledge_graph.py` uses NetworkX to infer prerequisite gaps and downstream risk topics.
5. **RAG Layer**: `rag/retrieve.py` embeds a local preparation knowledge base using SentenceTransformers and retrieves advice with FAISS.
6. **LLM SOCA Layer**: `llm/soca_generator.py` uses a HuggingFace text-generation pipeline when available, with a deterministic fallback.
7. **Dashboard Layer**: `app.py` presents charts, weak-topic reasoning, downloadable JSON reports, and feedback capture.
8. **Topic Diagnostic Layer**: `assessment/` generates topic-wise tests, grades attempts, detects confidence gaps, scores readiness, and builds revision roadmaps.

## Why These AI Components

- **RAG** grounds recommendations in a local, inspectable knowledge base instead of relying only on model memory.
- **Knowledge graphs** make topic dependency reasoning explainable, especially for prerequisite repair.
- **Multi-agent systems** separate academic, behavioral, wellness, and strategy reasoning so outputs are easier to audit.
- **LLMs** convert structured evidence into concise, motivational SOCA reports while preserving personalization.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

If the HuggingFace model is not available locally, the app still runs using deterministic SOCA generation. This keeps the MVP usable on machines without GPU memory for Phi-3 Mini or Mistral 7B.

To opt into local HuggingFace generation:

```bash
set USE_LOCAL_LLM=true
streamlit run app.py
```

## Project Structure

```text
app.py
agents/
rag/
kg/
scoring/
llm/
prompts/
data/
requirements.txt
README.md
```

## Sample Output

The included sample response produces:

- PCM score chart
- topic mastery heatmap
- topic-wise diagnostic readiness heatmap
- confidence vs accuracy graph
- subject-wise mastery chart
- weak topic alerts and revision priority list
- prerequisite gaps for Rotation, Organic Chemistry, and Integration
- agent JSON outputs
- SOCA report with actionable two-week plan
- downloadable report JSON

## Topic-Wise Diagnostic Pipeline

The enhanced assessment flow asks each student to mark completed, partially completed, and untouched chapters for Physics, Chemistry, and Mathematics. Completed topics unlock a five-question diagnostic test with 2 easy, 2 medium, and 1 hard MCQ.

For each completed topic, the system calculates:

- topic accuracy
- weighted difficulty handling
- confidence vs accuracy gap
- revision freshness and urgency
- conceptual weakness score
- average time per question
- readiness score from `0-100`

Readiness uses:

```text
0.40 * Accuracy
+ 0.20 * Confidence Alignment
+ 0.20 * Revision Freshness
+ 0.20 * Difficulty Handling
```

The resulting topic reports feed the SOCA generator, knowledge graph dependency reasoning, RAG retrieval, and personalized roadmap.

## Screenshots

Add screenshots after running locally:

- `docs/screenshots/questionnaire.png`
- `docs/screenshots/soca_report.png`
- `docs/screenshots/agent_outputs.png`

## Human-in-the-Loop Workflow

The dashboard includes a student usefulness rating and teacher-editable recommendation box. Feedback is saved to `data/feedback.jsonl`. This can later be used for reinforcement learning or active learning pipelines after proper data governance and review.

## Bonus Features Included

- Adaptive weak-topic selection through questionnaire controls
- Topic mastery heatmap
- Confidence, accuracy, stress, and discipline comparisons
- HuggingFace Spaces deployment-ready Streamlit structure
- Optional LLM backend with local deterministic fallback

## HuggingFace Spaces Deployment

1. Create a new Streamlit Space.
2. Upload this repository.
3. Keep `requirements.txt` at the repo root.
4. If using a hosted model, set environment variables or modify `SOCAGenerator` to call an inference endpoint.
5. For CPU Spaces, keep the deterministic fallback enabled or use a small model.

## Future Scope

- Real LangGraph orchestration with state transitions and retry policies
- Teacher dashboard for cohort-level intervention planning
- PDF report export with branded templates
- Downloadable JSON and PDF reports
- Longitudinal learning analytics across multiple mock tests
- Secure authentication and role-based access
- Formal validation with teachers and student outcomes
- Privacy-preserving feedback loops for model improvement
