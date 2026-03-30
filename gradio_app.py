import gradio as gr
import httpx
import os

API_BASE = os.getenv('API_BASE', 'http://localhost:8000/api/v1')


def format_turn(turn: dict) -> str:
    """Format a single debate turn for display."""
    agent_label = '🔵 AGENT A (FOR)' if turn['agent'] == 'agent_a' else '🔴 AGENT B (AGAINST)'
    return f'**{agent_label} — Turn {turn["turn_number"]}**\n\n{turn["content"]}'


def format_scores(scores: dict, agent_label: str) -> str:
    """Format score breakdown as a readable string."""
    if not scores:
        return 'No scores available'
    lines = [f'### {agent_label}']
    metrics = ['coherence', 'persuasiveness', 'factual_grounding', 'consistency', 'argument_diversity']
    for m in metrics:
        bar = '█' * scores[m] + '░' * (10 - scores[m])
        lines.append(f'**{m.replace("_", " ").title()}**: {bar} {scores[m]}/10')
    lines.append(f'**Total: {scores["total"]}/50**')
    return '\n'.join(lines)


def run_debate(topic: str, turns: int):
    """Called when the user clicks Run Debate."""
    if not topic.strip():
        yield 'Please enter a debate topic.', '', '', '', ''
        return

    yield 'Running debate... this takes 3-6 minutes. Please wait.', '', '', '', ''

    try:
        with httpx.Client(timeout=600) as client:
            response = client.post(
                f'{API_BASE}/debates',
                json={'topic': topic, 'turns': int(turns)}
            )
            response.raise_for_status()
            data = response.json()

        # Format the transcript
        transcript = '\n\n---\n\n'.join([format_turn(t) for t in data['turns']])

        # Format winner banner
        winner_map = {
            'agent_a': '🔵 Agent A wins!',
            'agent_b': '🔴 Agent B wins!',
            'tie': '🤝 It is a tie!'
        }
        winner_text = winner_map.get(data.get('winner', ''), 'No winner yet')
        verdict = f'## {winner_text}\n\n{data.get("reasoning", "")}'

        scores_a = format_scores(data.get('agent_a_scores'), '🔵 Agent A (FOR)')
        scores_b = format_scores(data.get('agent_b_scores'), '🔴 Agent B (AGAINST)')

        yield transcript, verdict, scores_a, scores_b, data['debate_id']

    except Exception as e:
        yield f'Error: {e}', '', '', '', ''


def load_history():
    """Load past debates for the history tab."""
    try:
        with httpx.Client(timeout=10) as client:
            response = client.get(f'{API_BASE}/debates')
            debates = response.json()
        if not debates:
            return '(No debates yet — run one first!)'
        lines = []
        for d in debates[:10]:
            winner = d.get('winner', 'pending')
            lines.append(f"**{d['topic']}** — Winner: {winner} — {d['created_at'][:10]}")
        return '\n\n'.join(lines)
    except Exception as e:
        return f'Could not load history: {e}'


# ── Build the Gradio interface ───────────────────────────────────────────────
with gr.Blocks(title='AgentEval', theme=gr.themes.Soft()) as demo:
    gr.Markdown('# AgentEval\n### Automated LLM Debate Evaluation Pipeline')
    gr.Markdown('Enter a controversial topic and watch two AI agents debate it. A third AI judge scores both agents.')

    with gr.Tab('Run Debate'):
        with gr.Row():
            topic_input = gr.Textbox(
                label='Debate Topic',
                placeholder='e.g. AI will replace most jobs within 20 years',
                scale=4
            )
            turns_slider = gr.Slider(minimum=1, maximum=5, value=3, step=1, label='Turns per agent', scale=1)

        run_btn = gr.Button('Run Debate', variant='primary', size='lg')

        with gr.Row():
            scores_a_out = gr.Markdown(label='Agent A Scores')
            scores_b_out = gr.Markdown(label='Agent B Scores')

        verdict_out = gr.Markdown(label='Verdict')
        transcript_out = gr.Markdown(label='Full Transcript')
        debate_id_out = gr.Textbox(label='Debate ID', visible=False)

        run_btn.click(
            fn=run_debate,
            inputs=[topic_input, turns_slider],
            outputs=[transcript_out, verdict_out, scores_a_out, scores_b_out, debate_id_out]
        )

    with gr.Tab('History'):
        refresh_btn = gr.Button('Refresh History')
        history_out = gr.Markdown()
        refresh_btn.click(fn=load_history, outputs=history_out)


if __name__ == '__main__':
    demo.launch(server_port=7860)
