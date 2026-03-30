import pytest
from app.evaluator.judge import _parse_scores

VALID_JSON = '''
{
  "agent_a": {
    "coherence": 8,
    "persuasiveness": 7,
    "factual_grounding": 6,
    "consistency": 9,
    "argument_diversity": 7
  },
  "agent_b": {
    "coherence": 6,
    "persuasiveness": 8,
    "factual_grounding": 7,
    "consistency": 6,
    "argument_diversity": 8
  },
  "winner": "agent_a",
  "reasoning": "Agent A made stronger structured arguments."
}
'''


def test_parse_valid_json():
    """Valid judge JSON should parse into an EvaluationResult."""
    result = _parse_scores(VALID_JSON, 'test-id-123')
    assert result.winner == 'agent_a'
    assert result.agent_a.coherence == 8
    assert result.agent_b.total == 35
    assert 'Agent A' in result.reasoning


def test_parse_strips_markdown_fences():
    """Parser should handle JSON wrapped in markdown fences."""
    fenced = f'```json\n{VALID_JSON.strip()}\n```'
    result = _parse_scores(fenced, 'test-id-456')
    assert result.winner == 'agent_a'


def test_parse_invalid_json_raises():
    """Invalid JSON should raise ValueError."""
    with pytest.raises(ValueError, match='invalid JSON'):
        _parse_scores('this is not json', 'test-id-789')
