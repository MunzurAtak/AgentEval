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
