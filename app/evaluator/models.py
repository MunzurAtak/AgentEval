from pydantic import BaseModel, Field
from typing import Literal


class AgentScores(BaseModel):
    """Scores for one agent across all five metrics."""
    coherence: int = Field(ge=1, le=10)
    persuasiveness: int = Field(ge=1, le=10)
    factual_grounding: int = Field(ge=1, le=10)
    consistency: int = Field(ge=1, le=10)
    argument_diversity: int = Field(ge=1, le=10)

    @property
    def total(self) -> int:
        return (
            self.coherence +
            self.persuasiveness +
            self.factual_grounding +
            self.consistency +
            self.argument_diversity
        )


class EvaluationResult(BaseModel):
    """Full evaluation output for one debate."""
    debate_id: str
    agent_a: AgentScores
    agent_b: AgentScores
    winner: Literal['agent_a', 'agent_b', 'tie']
    reasoning: str  # Judge's explanation of the verdict
