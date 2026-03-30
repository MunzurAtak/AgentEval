import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

# If GROQ_API_KEY is set in .env, use Groq cloud. Otherwise use local Ollama.
USE_GROQ = bool(os.getenv('GROQ_API_KEY'))

# Maps our local Ollama model names to their Groq equivalents
GROQ_MODEL_MAP = {
    'llama3.2': 'llama-3.1-8b-instant',
    'qwen2.5': 'mixtral-8x7b-32768',
    'phi3:mini': 'llama-3.1-8b-instant',
}


def chat(model: str, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
    """Send messages to a model and return the reply as a plain string."""
    if USE_GROQ:
        return _chat_groq(model, messages, temperature)
    return _chat_ollama(model, messages, temperature)


def _chat_ollama(model: str, messages: List[Dict[str, str]], temperature: float) -> str:
    import ollama
    try:
        response = ollama.chat(
            model=model,
            messages=messages,
            options={'temperature': temperature}
        )
        return response['message']['content'].strip()
    except Exception as e:
        raise RuntimeError(f'Ollama call failed for model {model}: {e}') from e


def _chat_groq(model: str, messages: List[Dict[str, str]], temperature: float) -> str:
    from groq import Groq
    client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    groq_model = GROQ_MODEL_MAP.get(model, 'llama-3.1-8b-instant')
    try:
        response = client.chat.completions.create(
            model=groq_model,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(f'Groq call failed: {e}') from e


def is_model_available(model: str) -> bool:
    """Check whether a model is ready to use."""
    if USE_GROQ:
        return model in GROQ_MODEL_MAP
    import ollama
    try:
        models = ollama.list()
        available = [m['name'] for m in models.get('models', [])]
        return model in available or f'{model}:latest' in available
    except Exception:
        return False
