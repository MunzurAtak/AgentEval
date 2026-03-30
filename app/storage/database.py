import sqlite3
import json
import os
from typing import List, Optional
from dotenv import load_dotenv
from app.agents.models import DebateResult
from app.evaluator.models import EvaluationResult

load_dotenv()

DB_PATH = os.getenv('DB_PATH', 'agenteval.db')


def get_connection() -> sqlite3.Connection:
    """Open a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Allows dict-style access to rows
    return conn


def init_db() -> None:
    """Create tables if they do not exist. Safe to call multiple times."""
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS debates (
                debate_id   TEXT PRIMARY KEY,
                topic       TEXT NOT NULL,
                turns_json  TEXT NOT NULL,
                agent_a_model TEXT NOT NULL,
                agent_b_model TEXT NOT NULL,
                created_at  TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS evaluations (
                debate_id    TEXT PRIMARY KEY,
                agent_a_json TEXT NOT NULL,
                agent_b_json TEXT NOT NULL,
                winner       TEXT NOT NULL,
                reasoning    TEXT NOT NULL,
                FOREIGN KEY (debate_id) REFERENCES debates(debate_id)
            );
        """)


def save_debate(debate: DebateResult) -> None:
    """Persist a DebateResult to the database."""
    with get_connection() as conn:
        conn.execute(
            'INSERT OR REPLACE INTO debates VALUES (?,?,?,?,?,?)',
            (
                debate.debate_id,
                debate.topic,
                json.dumps([t.model_dump() for t in debate.turns], default=str),
                debate.agent_a_model,
                debate.agent_b_model,
                debate.created_at.isoformat(),
            )
        )


def save_evaluation(result: EvaluationResult) -> None:
    """Persist an EvaluationResult to the database."""
    with get_connection() as conn:
        conn.execute(
            'INSERT OR REPLACE INTO evaluations VALUES (?,?,?,?,?)',
            (
                result.debate_id,
                json.dumps(result.agent_a.model_dump()),
                json.dumps(result.agent_b.model_dump()),
                result.winner,
                result.reasoning,
            )
        )


def get_all_debates() -> List[dict]:
    """Return all debates with their evaluations joined, newest first."""
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT d.debate_id, d.topic, d.created_at,
                   d.agent_a_model, d.agent_b_model,
                   e.winner, e.reasoning,
                   e.agent_a_json, e.agent_b_json
            FROM debates d
            LEFT JOIN evaluations e ON d.debate_id = e.debate_id
            ORDER BY d.created_at DESC
        """).fetchall()
        return [dict(r) for r in rows]


def get_debate_by_id(debate_id: str) -> Optional[dict]:
    """Return a single debate with its full turn transcript."""
    with get_connection() as conn:
        row = conn.execute(
            'SELECT * FROM debates WHERE debate_id = ?', (debate_id,)
        ).fetchone()
        return dict(row) if row else None
