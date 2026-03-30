import uuid
from datetime import datetime
from app.agents.agent import DebateAgent
from app.agents.models import Turn, DebateResult
import os
from dotenv import load_dotenv

load_dotenv()


def run_debate(topic: str, turns: int = None) -> DebateResult:
    """
    Run a full debate between Agent A and Agent B.
    Returns a DebateResult with the full transcript.
    """
    if turns is None:
        turns = int(os.getenv('DEBATE_TURNS', 3))

    agent_a_model = os.getenv('AGENT_A_MODEL', 'llama3.2')
    agent_b_model = os.getenv('AGENT_B_MODEL', 'qwen2.5')

    # Create two agents with opposing stances on the same topic
    agent_a = DebateAgent('agent_a', agent_a_model, stance='for', topic=topic)
    agent_b = DebateAgent('agent_b', agent_b_model, stance='against', topic=topic)

    transcript: list[Turn] = []
    last_message = None  # Each agent responds to the other's last message

    for turn_num in range(1, turns + 1):
        # Agent A speaks (responds to B's last message, or opens if turn 1)
        a_reply = agent_a.respond(opponent_message=last_message)
        transcript.append(Turn(
            agent='agent_a',
            model=agent_a_model,
            content=a_reply,
            turn_number=turn_num
        ))
        last_message = a_reply  # B will respond to this

        # Agent B responds to A
        b_reply = agent_b.respond(opponent_message=last_message)
        transcript.append(Turn(
            agent='agent_b',
            model=agent_b_model,
            content=b_reply,
            turn_number=turn_num
        ))
        last_message = b_reply  # A will respond to this next turn

    return DebateResult(
        debate_id=str(uuid.uuid4()),
        topic=topic,
        turns=transcript,
        created_at=datetime.utcnow(),
        agent_a_model=agent_a_model,
        agent_b_model=agent_b_model,
    )
