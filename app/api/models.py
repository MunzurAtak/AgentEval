from pydantic import BaseModel
from typing import List, Optional


class DebateRequestBody(BaseModel):
    topic: str
    turns: int = 3


class TurnOut(BaseModel):
    agent: str
    model: str
    content: str
    turn_number: int


class ScoresOut(BaseModel):
    coherence: int
    persuasiveness: int
    factual_grounding: int
    consistency: int
    argument_diversity: int
    total: int


class DebateOut(BaseModel):
    debate_id: str
    topic: str
    turns: List[TurnOut]
    agent_a_model: str
    agent_b_model: str
    agent_a_scores: Optional[ScoresOut] = None
    agent_b_scores: Optional[ScoresOut] = None
    winner: Optional[str] = None
    reasoning: Optional[str] = None
    created_at: str
