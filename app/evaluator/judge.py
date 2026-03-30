import json
import os
import re
from dotenv import load_dotenv
from app.llm_client import chat
from app.agents.models import DebateResult
from app.evaluator.models import AgentScores, EvaluationResult

load_dotenv()


def _build_transcript_text(debate: DebateResult) -> str:
    """Format the debate transcript as readable text for the judge."""
    lines = [f'DEBATE TOPIC: {debate.topic}', '']
    for turn in debate.turns:
        label = 'AGENT A (arguing FOR)' if turn.agent == 'agent_a' else 'AGENT B (arguing AGAINST)'
        lines.append(f'--- {label} | Turn {turn.turn_number} ---')
        lines.append(turn.content)
        lines.append('')
    return '\n'.join(lines)


def _build_judge_prompt(transcript: str) -> str:
    """Build the prompt that instructs the judge how to score."""
    return f"""You are an expert debate judge. Evaluate the debate transcript below.

Score each agent on ALL FIVE metrics from 1 (very poor) to 10 (excellent).

METRICS:
- coherence: Is the argument logically structured and internally consistent?
- persuasiveness: How convincing is it to a neutral observer?
- factual_grounding: Are claims specific and plausible (not vague or hallucinated)?
- consistency: Does the agent maintain their assigned stance throughout?
- argument_diversity: Does the agent introduce new points or repeat themselves?

YOU MUST RESPOND WITH ONLY VALID JSON. No explanation before or after.
No markdown code fences. Just the raw JSON object.

Required format:
{{
  "agent_a": {{
    "coherence": <int 1-10>,
    "persuasiveness": <int 1-10>,
    "factual_grounding": <int 1-10>,
    "consistency": <int 1-10>,
    "argument_diversity": <int 1-10>
  }},
  "agent_b": {{
    "coherence": <int 1-10>,
    "persuasiveness": <int 1-10>,
    "factual_grounding": <int 1-10>,
    "consistency": <int 1-10>,
    "argument_diversity": <int 1-10>
  }},
  "winner": "<agent_a|agent_b|tie>",
  "reasoning": "<2-3 sentence explanation of the verdict>"
}}

TRANSCRIPT:
{transcript}
"""


def _parse_scores(raw: str, debate_id: str) -> EvaluationResult:
    """Parse the JSON response from the judge LLM."""
    # Strip any accidental markdown fences the model might add
    clean = re.sub(r'```[a-z]*', '', raw).strip()
    try:
        data = json.loads(clean)
    except json.JSONDecodeError as e:
        raise ValueError(f'Judge returned invalid JSON: {e}\nRaw output:\n{raw}') from e

    return EvaluationResult(
        debate_id=debate_id,
        agent_a=AgentScores(**data['agent_a']),
        agent_b=AgentScores(**data['agent_b']),
        winner=data['winner'],
        reasoning=data['reasoning'],
    )


def evaluate_debate(debate: DebateResult) -> EvaluationResult:
    """Run the judge LLM over a completed debate and return scores."""
    judge_model = os.getenv('JUDGE_MODEL', 'phi3:mini')
    transcript = _build_transcript_text(debate)
    prompt = _build_judge_prompt(transcript)

    raw_response = chat(
        model=judge_model,
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0.1  # Low temp = more consistent JSON output
    )

    return _parse_scores(raw_response, debate.debate_id)
