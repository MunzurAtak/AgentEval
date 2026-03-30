from app.llm_client import chat
from typing import List, Dict


class DebateAgent:
    """
    An LLM-powered debate agent with a fixed persona.
    Maintains conversation history so each turn builds on the last.
    """

    def __init__(self, name: str, model: str, stance: str, topic: str):
        self.name = name      # 'agent_a' or 'agent_b'
        self.model = model    # Ollama model name
        self.stance = stance  # 'for' or 'against'
        self.topic = topic
        self.history: List[Dict[str, str]] = []
        self._init_system_prompt()

    def _init_system_prompt(self):
        """Build the system prompt that defines the agent's persona."""
        direction = 'strongly in favour of' if self.stance == 'for' else 'strongly against'
        self.system_prompt = (
            f'You are a skilled debater who is {direction} the following position: '
            f'"{self.topic}". '
            'You must always argue from this perspective, even if you personally disagree. '
            'Keep each response to 3-5 sentences. Be direct, specific, and persuasive. '
            "Respond to your opponent's last argument directly before making your own point."
        )

    def respond(self, opponent_message: str = None) -> str:
        """
        Generate the agent's next argument.
        If opponent_message is provided, the agent responds to it first.
        """
        # Add opponent's message to history so the agent can respond to it
        if opponent_message:
            self.history.append({'role': 'user', 'content': opponent_message})

        # Build the full message list: system prompt + conversation history
        messages = [{'role': 'system', 'content': self.system_prompt}]
        messages.extend(self.history)

        # If this is the very first turn, give the agent an opening prompt
        if not self.history:
            messages.append({
                'role': 'user',
                'content': f'Open the debate on: "{self.topic}". Make your opening argument.'
            })

        # Call the LLM and get the reply
        reply = chat(self.model, messages, temperature=0.75)

        # Store our own reply in history so future turns remember it
        self.history.append({'role': 'assistant', 'content': reply})

        return reply
