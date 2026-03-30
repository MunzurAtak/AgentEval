import pytest
from unittest.mock import patch, MagicMock
from app.llm_client import chat


def test_chat_returns_stripped_string():
    """chat() should return a plain stripped string."""
    mock_response = {'message': {'content': '  Hello world  '}}
    with patch('ollama.chat', return_value=mock_response):
        result = chat('llama3.2', [{'role': 'user', 'content': 'Hi'}])
    assert result == 'Hello world'


def test_chat_raises_on_failure():
    """chat() should raise RuntimeError if Ollama fails."""
    with patch('ollama.chat', side_effect=Exception('Connection refused')):
        with pytest.raises(RuntimeError, match='Ollama call failed'):
            chat('llama3.2', [{'role': 'user', 'content': 'Hi'}])
