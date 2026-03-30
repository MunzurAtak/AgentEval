from pydantic import BaseModel
from typing import List
from datetime import datetime


class Turn(BaseModel):
    """A single turn in the debate — one agent speaking."""
    agent: str        # 'agent_a' or 'agent_b'
    model: str        # e.g. 'llama3.2'
    content: str      # What the agent said
    turn_number: int  # 1-based index


class DebateRequest(BaseModel):
    """Input to start a debate."""
    topic: str
    turns: int = 3  # Number of turns PER agent


class DebateResult(BaseModel):
    """The full result of a completed debate."""
    debate_id: str
    topic: str
    turns: List[Turn]
    created_at: datetime
    agent_a_model: str
    agent_b_model: str
