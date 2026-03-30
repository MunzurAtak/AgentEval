---
title: AgentEval
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.44.1
app_file: app.py
pinned: false
---

# AgentEval — Automated LLM Debate Evaluation Pipeline

AgentEval runs two LLM agents with opposing stances on a topic, lets them debate for N turns, then uses a third LLM as a judge to score both agents across 5 quality metrics and declare a winner.

## Architecture

User submits topic → Agent Runner (2 x LLMs debate) → Judge LLM evaluates transcript → Scores stored in SQLite → Results displayed in Gradio dashboard

## Tech Stack

- **Backend:** FastAPI, Python 3.11
- **LLMs (local):** Ollama (llama3.2, qwen2.5, phi3:mini)
- **LLMs (deployed):** Groq API (free tier)
- **Storage:** SQLite
- **Frontend:** Gradio
- **Deploy:** Hugging Face Spaces
- **Container:** Docker + docker-compose
- **CI/CD:** GitHub Actions

## Evaluation Metrics

Each agent is scored 1-10 on: Coherence, Persuasiveness, Factual Grounding, Consistency, Argument Diversity.

## Run Locally

```bash
git clone https://github.com/MunzurAtak/AgentEval
cd AgentEval
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
ollama pull llama3.2 && ollama pull qwen2.5 && ollama pull phi3:mini
uvicorn app.main:app --port 8000 &
python gradio_app.py
```

Open http://localhost:7860

## API

- `POST /api/v1/debates` — Run a debate
- `GET /api/v1/debates` — List all debates
- `GET /api/v1/health` — Health check
