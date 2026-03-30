import pytest
from datetime import datetime
from app.storage.database import init_db, save_debate, save_evaluation, get_all_debates, get_debate_by_id
from app.agents.models import DebateResult, Turn
from app.evaluator.models import EvaluationResult, AgentScores


@pytest.fixture(autouse=True)
def use_test_db(tmp_path, monkeypatch):
    """Use a temporary database for every test — never touches the real DB."""
    test_db = str(tmp_path / 'test.db')
    monkeypatch.setenv('DB_PATH', test_db)
    import app.storage.database as db_module
    monkeypatch.setattr(db_module, 'DB_PATH', test_db)
    init_db()


def make_debate(debate_id='abc-123'):
    return DebateResult(
        debate_id=debate_id,
        topic='Test topic',
        turns=[Turn(agent='agent_a', model='llama3.2', content='Arg A', turn_number=1)],
        created_at=datetime.utcnow(),
        agent_a_model='llama3.2',
        agent_b_model='qwen2.5',
    )


def test_save_and_retrieve_debate():
    debate = make_debate()
    save_debate(debate)
    retrieved = get_debate_by_id('abc-123')
    assert retrieved is not None
    assert retrieved['topic'] == 'Test topic'


def test_get_all_debates_empty():
    assert get_all_debates() == []


def test_get_all_debates_after_save():
    save_debate(make_debate('id-1'))
    save_debate(make_debate('id-2'))
    assert len(get_all_debates()) == 2
