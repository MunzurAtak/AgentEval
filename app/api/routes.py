import json
from fastapi import APIRouter, HTTPException
from app.api.models import DebateRequestBody, DebateOut, ScoresOut, TurnOut
from app.agents.runner import run_debate
from app.evaluator.judge import evaluate_debate
from app.storage.database import save_debate, save_evaluation, get_all_debates, get_debate_by_id

router = APIRouter()


@router.post('/debates', response_model=DebateOut)
def create_debate(body: DebateRequestBody):
    """Run a full debate and return the result with scores."""
    if not body.topic.strip():
        raise HTTPException(status_code=400, detail='Topic cannot be empty')
    if not 1 <= body.turns <= 5:
        raise HTTPException(status_code=400, detail='Turns must be between 1 and 5')

    # Step 1: Run the debate
    debate = run_debate(body.topic, turns=body.turns)

    # Step 2: Evaluate it
    evaluation = evaluate_debate(debate)

    # Step 3: Save both to DB
    save_debate(debate)
    save_evaluation(evaluation)

    # Step 4: Build and return response
    return DebateOut(
        debate_id=debate.debate_id,
        topic=debate.topic,
        turns=[TurnOut(**t.model_dump()) for t in debate.turns],
        agent_a_model=debate.agent_a_model,
        agent_b_model=debate.agent_b_model,
        agent_a_scores=ScoresOut(**evaluation.agent_a.model_dump(), total=evaluation.agent_a.total),
        agent_b_scores=ScoresOut(**evaluation.agent_b.model_dump(), total=evaluation.agent_b.total),
        winner=evaluation.winner,
        reasoning=evaluation.reasoning,
        created_at=debate.created_at.isoformat(),
    )


@router.get('/debates', response_model=list[DebateOut])
def list_debates():
    """Return all past debates ordered by newest first."""
    rows = get_all_debates()
    results = []
    for r in rows:
        scores_a = json.loads(r['agent_a_json']) if r.get('agent_a_json') else None
        scores_b = json.loads(r['agent_b_json']) if r.get('agent_b_json') else None
        results.append(DebateOut(
            debate_id=r['debate_id'],
            topic=r['topic'],
            turns=[],  # Omit full transcript from list view for performance
            agent_a_model=r['agent_a_model'],
            agent_b_model=r['agent_b_model'],
            agent_a_scores=ScoresOut(**scores_a, total=sum(scores_a.values())) if scores_a else None,
            agent_b_scores=ScoresOut(**scores_b, total=sum(scores_b.values())) if scores_b else None,
            winner=r.get('winner'),
            reasoning=r.get('reasoning'),
            created_at=r['created_at'],
        ))
    return results


@router.get('/health')
def health_check():
    """Simple health check endpoint."""
    return {'status': 'ok', 'service': 'AgentEval'}
