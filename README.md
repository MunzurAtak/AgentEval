---
title: AgentEval
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 5.7.1
app_file: app.py
pinned: false
---

# AgentEval — Automated LLM Debate Evaluation Pipeline

[![CI](https://github.com/MunzurAtak/AgentEval/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/MunzurAtak/AgentEval/actions/workflows/ci.yml)

**Live demo:** https://huggingface.co/spaces/MunzurAtak/agenteval

## Description

AgentEval is a multi-agent pipeline that stages a structured debate between two LLMs, then uses a third LLM as an impartial judge to score both sides. The goal is to explore how well language models can construct, sustain, and rebut arguments — and whether automated evaluation can produce meaningful, reproducible scores.

Each agent is assigned a fixed stance (for / against) and maintains full conversation history, so arguments build naturally across turns rather than being generated in isolation. The judge receives the complete transcript and scores both agents across five independent metrics before declaring a winner.

The system runs entirely on free, locally-hosted models via Ollama for development, and switches automatically to Groq's API for cloud deployment on Hugging Face Spaces — no code changes needed.

## What it does

AgentEval pits two AI agents against each other on any debate topic. One argues **for**, one argues **against**. A third AI acts as a judge and scores both across five quality metrics, then declares a winner.

## How it works

```
User submits topic
      ↓
Agent A (FOR) ←→ Agent B (AGAINST)   ← debate for N turns
      ↓
Judge LLM evaluates the full transcript
      ↓
Scores stored in SQLite
      ↓
Results displayed in Gradio dashboard
```

## Evaluation Metrics

| Metric | What it measures |
|---|---|
| Coherence | Is the argument logically structured? |
| Persuasiveness | How convincing is it to a neutral observer? |
| Factual Grounding | Are claims specific and plausible? |
| Consistency | Does the agent maintain their stance throughout? |
| Argument Diversity | Does the agent introduce new points each turn? |

Each metric is scored 1–10. Maximum score: **50/50**.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Python 3.11 |
| LLMs (local) | Ollama — llama3.2, qwen2.5, phi3:mini |
| LLMs (deployed) | Groq API — llama-3.1-8b-instant, llama-3.3-70b-versatile |
| Storage | SQLite |
| Frontend | Gradio 5 |
| Deployment | Hugging Face Spaces |
| Containerisation | Docker + docker-compose |
| CI/CD | GitHub Actions |
| Testing | Pytest with mocking |

## Design Choices

**Stateful agents over stateless calls** — Each `DebateAgent` maintains its own conversation history. Rather than reconstructing context from the transcript on every turn, the agent accumulates a `history` list that grows with each exchange. This keeps arguments coherent and makes the agent respond to its opponent directly rather than making generic points.

**Single LLM client with environment-driven routing** — `llm_client.py` is the only place that knows whether to call Ollama or Groq. The rest of the codebase calls `chat(model, messages)` and never thinks about deployment. Swapping backends is a one-line env var change (`GROQ_API_KEY`), which is what makes local development and cloud deployment share the same code.

**Separate models for each role** — Agent A, Agent B, and the judge each use a different model by default (llama3.2, qwen2.5, phi3:mini). Using the same model for both sides produces near-identical argument styles; different models create more varied, realistic debates and stress-test the judge against heterogeneous outputs.

**JSON-only judge output with retry logic** — The judge is prompted to return raw JSON with no explanation text. If the model adds markdown fences or extra prose, the parser strips them and retries up to 3 times before raising. This keeps evaluation deterministic and avoids brittle string parsing of natural language verdicts.

**FastAPI + Gradio as two separate processes** — The API and UI are decoupled so the backend can be used headlessly (e.g. via the REST API or tests) without running Gradio. On Hugging Face Spaces, `app.py` wires them together into a single process since Spaces only exposes one port.

**SQLite for storage** — Debates and scores are small, structured, and written once. SQLite requires no infrastructure and works identically in development, Docker, and Spaces. The database path is overridable via `DB_PATH` env var, which is how tests use a temporary file without touching the real database.

## Run Locally

```bash
git clone https://github.com/MunzurAtak/AgentEval
cd AgentEval

python -m venv venv
.\venv\Scripts\Activate.ps1      # Windows
# source venv/bin/activate       # macOS/Linux

pip install -r requirements.txt

ollama pull llama3.2
ollama pull qwen2.5
ollama pull phi3:mini

# Terminal 1 — start the API
uvicorn app.main:app --reload --port 8000

# Terminal 2 — start the frontend
python gradio_app.py
```

Open [http://localhost:7860](http://localhost:7860)

## Run Tests

```bash
pytest tests/ -v
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/debates` | Run a full debate and return scores |
| GET | `/api/v1/debates` | List all past debates |
| GET | `/api/v1/health` | Health check |

Interactive API docs available at [http://localhost:8000/docs](http://localhost:8000/docs)

## Project Structure

```
agenteval/
├── app/
│   ├── agents/        # Debate agent logic and runner
│   ├── evaluator/     # LLM judge and scoring
│   ├── storage/       # SQLite database layer
│   ├── api/           # FastAPI routes and models
│   ├── llm_client.py  # Unified Ollama/Groq wrapper
│   └── main.py        # FastAPI entry point
├── tests/             # Pytest test suite
├── gradio_app.py      # Gradio frontend
├── app.py             # Hugging Face Spaces entry point
├── Dockerfile
└── docker-compose.yml
```
