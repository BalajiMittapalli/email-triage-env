"""
FastAPI application for the Email Triage Environment.

Endpoints:
    - POST /reset: Reset the environment
    - POST /step: Execute an action
    - GET /state: Get current environment state
    - GET /schema: Get action/observation schemas
    - GET /health: Health check
    - WS /ws: WebSocket endpoint for persistent sessions

Usage:
    uvicorn email_triage_env.server.app:app --host 0.0.0.0 --port 7860
"""

try:
    from openenv.core.env_server.http_server import create_app
except ImportError:
    # Fallback: create a minimal FastAPI app
    create_app = None

try:
    from models import EmailTriageAction, EmailTriageObservation
except ImportError:
    try:
        from email_triage_env.models import EmailTriageAction, EmailTriageObservation
    except ImportError:
        from ..models import EmailTriageAction, EmailTriageObservation

from .email_triage_environment import EmailTriageEnvironment


_ui_env = EmailTriageEnvironment()


if create_app is not None:
    # Use OpenEnv's create_app for full compatibility
    app = create_app(
        EmailTriageEnvironment,
        EmailTriageAction,
        EmailTriageObservation,
        env_name="email_triage",
        max_concurrent_envs=5,
    )
else:
    # Fallback: create a minimal FastAPI app manually
    from fastapi import FastAPI
    import uvicorn

    app = FastAPI(title="Email Triage Environment", version="0.1.0")

    @app.get("/health")
    def health():
        return {"status": "healthy"}

    @app.post("/reset")
    def reset(data: dict = {}):
        obs = _ui_env.reset(**data)
        return {
            "observation": obs.model_dump(),
            "reward": obs.reward,
            "done": obs.done,
        }

    @app.post("/step")
    def step(data: dict = {}):
        action = EmailTriageAction(**data.get("action", data))
        obs = _ui_env.step(action)
        return {
            "observation": obs.model_dump(),
            "reward": obs.reward,
            "done": obs.done,
        }

    @app.get("/state")
    def state():
        return _ui_env.state.model_dump()


@app.post("/ui/reset")
def ui_reset(data: dict = {}):
    """Persistent reset endpoint used by the browser demo."""
    obs = _ui_env.reset(**data)
    return {
        "observation": obs.model_dump(),
        "reward": obs.reward,
        "done": obs.done,
        "state": _ui_env.state.model_dump(),
    }


@app.post("/ui/step")
def ui_step(data: dict = {}):
    """Persistent step endpoint used by the browser demo."""
    action = EmailTriageAction(**data.get("action", data))
    obs = _ui_env.step(action)
    return {
        "observation": obs.model_dump(),
        "reward": obs.reward,
        "done": obs.done,
        "state": _ui_env.state.model_dump(),
    }


@app.get("/ui/state")
def ui_state():
    """Current browser-demo environment state."""
    return _ui_env.state.model_dump()


@app.get("/")
def root():
        """Interactive demo UI for judges on Hugging Face Spaces."""
        from fastapi.responses import HTMLResponse

        html = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Email Triage Environment Demo</title>
    <style>
        :root {
            --bg: #f8f6f2;
            --panel: #ffffff;
            --ink: #1f1b16;
            --muted: #6f665b;
            --brand: #0f766e;
            --accent: #f59e0b;
            --border: #e8dfd3;
            --ok: #166534;
            --warn: #9a3412;
        }
        * { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: "Segoe UI", "Trebuchet MS", sans-serif;
            color: var(--ink);
            background:
                radial-gradient(circle at 15% 10%, #fde68a 0%, rgba(253, 230, 138, 0) 30%),
                radial-gradient(circle at 85% 85%, #99f6e4 0%, rgba(153, 246, 228, 0) 35%),
                var(--bg);
            min-height: 100vh;
        }
        .wrap {
            max-width: 1080px;
            margin: 0 auto;
            padding: 24px;
        }
        .hero {
            background: linear-gradient(135deg, #0f766e 0%, #155e75 100%);
            color: #f7fffe;
            border-radius: 18px;
            padding: 20px 22px;
            box-shadow: 0 14px 40px rgba(15, 118, 110, 0.28);
            margin-bottom: 16px;
        }
        .hero h1 {
            margin: 0 0 8px;
            font-size: 1.65rem;
            letter-spacing: 0.2px;
        }
        .hero p { margin: 0; opacity: 0.92; }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 14px;
        }
        .card {
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 14px;
            box-shadow: 0 5px 18px rgba(31, 27, 22, 0.06);
        }
        .card h2 {
            margin: 0 0 10px;
            font-size: 1.05rem;
        }
        .row { display: flex; gap: 10px; flex-wrap: wrap; }
        label { font-weight: 600; font-size: 0.9rem; }
        input, select, textarea {
            width: 100%;
            padding: 9px 10px;
            border: 1px solid #d8cfc3;
            border-radius: 10px;
            font: inherit;
            color: var(--ink);
            background: #fffdfa;
        }
        textarea { min-height: 90px; resize: vertical; }
        .btn {
            border: 0;
            border-radius: 999px;
            padding: 10px 16px;
            font-weight: 700;
            cursor: pointer;
            transition: transform 120ms ease, opacity 120ms ease;
        }
        .btn:hover { transform: translateY(-1px); }
        .btn:disabled { opacity: 0.65; cursor: not-allowed; }
        .btn-brand { background: var(--brand); color: white; }
        .btn-accent { background: var(--accent); color: #2e1800; }
        .mono {
            font-family: Consolas, "Cascadia Mono", "Courier New", monospace;
            font-size: 0.86rem;
            background: #fffef9;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 10px;
            max-height: 280px;
            overflow: auto;
            white-space: pre-wrap;
            word-break: break-word;
        }
        .status { font-weight: 700; }
        .ok { color: var(--ok); }
        .warn { color: var(--warn); }
        .full { grid-column: 1 / -1; }
        .muted { color: var(--muted); font-size: 0.92rem; }
        .kv {
            display: grid;
            grid-template-columns: 150px 1fr;
            gap: 8px 12px;
            font-size: 0.92rem;
            margin-bottom: 10px;
        }
        .k { color: var(--muted); font-weight: 600; }
        .v { color: var(--ink); }
        .email-box {
            border: 1px solid var(--border);
            border-radius: 10px;
            background: #fffef9;
            padding: 10px;
        }
        .email-box h3 {
            margin: 0 0 8px;
            font-size: 1rem;
            line-height: 1.3;
        }
        .email-body {
            white-space: pre-wrap;
            line-height: 1.4;
            margin: 0;
        }
        .chips {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-bottom: 10px;
        }
        .chip {
            border-radius: 999px;
            padding: 6px 10px;
            font-size: 0.85rem;
            font-weight: 700;
            border: 1px solid var(--border);
            background: #fffef9;
        }
        .chip-ok { background: #ecfdf3; color: #166534; border-color: #86efac; }
        .chip-mid { background: #fffbeb; color: #9a3412; border-color: #fcd34d; }
        .chip-bad { background: #fef2f2; color: #991b1b; border-color: #fca5a5; }
        @media (max-width: 840px) {
            .grid { grid-template-columns: 1fr; }
            .wrap { padding: 14px; }
            .kv { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="wrap">
        <section class="hero">
            <h1>Email Triage Environment</h1>
            <p>Judge-facing interactive demo for OpenEnv tasks: easy, medium, hard.</p>
        </section>

        <section class="grid">
            <article class="card">
                <h2>1) Start Episode</h2>
                <div class="row">
                    <div style="flex: 1 1 220px;">
                        <label for="task">Task</label>
                        <select id="task">
                            <option value="email_classify">email_classify (easy)</option>
                            <option value="email_prioritize">email_prioritize (medium)</option>
                            <option value="email_full_triage">email_full_triage (hard)</option>
                        </select>
                    </div>
                    <div style="flex: 1 1 120px;">
                        <label for="seed">Seed</label>
                        <input id="seed" type="number" value="42" />
                    </div>
                </div>
                <div class="row" style="margin-top: 10px;">
                    <button id="resetBtn" class="btn btn-brand">Reset Task</button>
                    <span id="resetStatus" class="status muted">Idle</span>
                </div>
            </article>

            <article class="card">
                <h2>2) Agent Action</h2>
                <label>Category</label>
                <select id="category">
                    <option value="spam">spam</option>
                    <option value="work" selected>work</option>
                    <option value="personal">personal</option>
                    <option value="urgent">urgent</option>
                    <option value="newsletter">newsletter</option>
                </select>

                <div id="priorityWrap" style="margin-top: 8px; display: none;">
                    <label>Priority</label>
                    <select id="priority">
                        <option value="low">low</option>
                        <option value="medium" selected>medium</option>
                        <option value="high">high</option>
                        <option value="critical">critical</option>
                    </select>
                </div>

                <div id="summaryWrap" style="margin-top: 8px; display: none;">
                    <label>Summary</label>
                    <textarea id="summary" placeholder="Brief email summary..."></textarea>
                </div>

                <div id="actionsWrap" style="margin-top: 8px; display: none;">
                    <label>Action Items (one per line)</label>
                    <textarea id="actionItems" placeholder="Investigate issue\nReply to sender"></textarea>
                </div>

                <div id="replyWrap" style="margin-top: 8px; display: none;">
                    <label>Reply Draft</label>
                    <textarea id="replyDraft" placeholder="Draft a reply..."></textarea>
                </div>

                <div class="row" style="margin-top: 10px;">
                    <button id="stepBtn" class="btn btn-accent" disabled>Submit Step</button>
                    <span id="stepStatus" class="status muted">Waiting for reset</span>
                </div>
            </article>

            <article class="card full">
                <h2>Current Observation</h2>
                <div id="observationPretty" class="email-box muted">Run reset to load an email.</div>
                <details style="margin-top: 10px;">
                    <summary class="muted">Show raw observation JSON</summary>
                    <div id="observation" class="mono" style="margin-top: 8px;">Run reset to load an email.</div>
                </details>
            </article>

            <article class="card full">
                <h2>Step Result</h2>
                <div id="resultSummary" class="chips muted">No step submitted yet.</div>
                <div id="resultPretty" class="email-box muted">Submit an action to see score and feedback.</div>
                <details style="margin-top: 10px;">
                    <summary class="muted">Show raw step result JSON</summary>
                    <div id="result" class="mono" style="margin-top: 8px;">No step submitted yet.</div>
                </details>
                <p class="muted" style="margin-top: 8px;">
                    API Links: <a href="/docs" target="_blank">/docs</a> | <a href="/health" target="_blank">/health</a> | <a href="/schema" target="_blank">/schema</a>
                </p>
            </article>
        </section>
    </div>

    <script>
        const taskEl = document.getElementById('task');
        const seedEl = document.getElementById('seed');
        const resetBtn = document.getElementById('resetBtn');
        const stepBtn = document.getElementById('stepBtn');
        const resetStatus = document.getElementById('resetStatus');
        const stepStatus = document.getElementById('stepStatus');
        const observationEl = document.getElementById('observation');
        const observationPrettyEl = document.getElementById('observationPretty');
        const resultEl = document.getElementById('result');
        const resultSummaryEl = document.getElementById('resultSummary');
        const resultPrettyEl = document.getElementById('resultPretty');

        const categoryEl = document.getElementById('category');
        const priorityEl = document.getElementById('priority');
        const summaryEl = document.getElementById('summary');
        const actionItemsEl = document.getElementById('actionItems');
        const replyDraftEl = document.getElementById('replyDraft');

        const priorityWrap = document.getElementById('priorityWrap');
        const summaryWrap = document.getElementById('summaryWrap');
        const actionsWrap = document.getElementById('actionsWrap');
        const replyWrap = document.getElementById('replyWrap');

        let lastDifficulty = 'easy';

        function updateFormByTask() {
            const task = taskEl.value;
            if (task === 'email_classify') {
                lastDifficulty = 'easy';
                priorityWrap.style.display = 'none';
                summaryWrap.style.display = 'none';
                actionsWrap.style.display = 'none';
                replyWrap.style.display = 'none';
            } else if (task === 'email_prioritize') {
                lastDifficulty = 'medium';
                priorityWrap.style.display = 'block';
                summaryWrap.style.display = 'block';
                actionsWrap.style.display = 'none';
                replyWrap.style.display = 'none';
            } else {
                lastDifficulty = 'hard';
                priorityWrap.style.display = 'block';
                summaryWrap.style.display = 'block';
                actionsWrap.style.display = 'block';
                replyWrap.style.display = 'block';
            }
        }

        function pretty(obj) {
            return JSON.stringify(obj, null, 2);
        }

        function esc(value) {
            return String(value ?? '')
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#39;');
        }

        function text(value) {
            if (value === null || value === undefined || value === '') return '—';
            return String(value);
        }

        function chipClass(score) {
            if (score >= 0.75) return 'chip chip-ok';
            if (score >= 0.4) return 'chip chip-mid';
            return 'chip chip-bad';
        }

        function renderObservation(obs) {
            if (!obs) {
                observationPrettyEl.innerHTML = '<span class="muted">No observation.</span>';
                observationEl.textContent = 'No observation.';
                return;
            }

            observationPrettyEl.innerHTML = `
                <div class="kv">
                    <div class="k">Task</div><div class="v">${esc(text(obs.task_name))} (${esc(text(obs.task_difficulty))})</div>
                    <div class="k">From</div><div class="v">${esc(text(obs.email_from))}</div>
                    <div class="k">To</div><div class="v">${esc(text(obs.email_to))}</div>
                    <div class="k">Date</div><div class="v">${esc(text(obs.email_date))}</div>
                </div>
                <h3>${esc(text(obs.email_subject))}</h3>
                <p class="email-body">${esc(text(obs.email_body))}</p>
            `;
            observationEl.textContent = pretty(obs);
        }

        function renderResult(data) {
            const obs = data?.observation || {};
            const score = Number(obs.score ?? data?.reward ?? 0);
            const done = Boolean(data?.done ?? obs.done);
            const feedback = text(obs.feedback);
            const expectedCategory = text(obs.correct_category);
            const expectedPriority = text(obs.correct_priority);

            resultSummaryEl.className = 'chips';
            resultSummaryEl.innerHTML = `
                <span class="${chipClass(score)}">Score: ${score.toFixed(2)}</span>
                <span class="chip ${done ? 'chip-ok' : 'chip-mid'}">Done: ${done}</span>
                <span class="chip">Task: ${esc(text(obs.task_name))}</span>
            `;

            resultPrettyEl.className = 'email-box';
            resultPrettyEl.innerHTML = `
                <div class="kv">
                    <div class="k">Feedback</div><div class="v">${esc(feedback)}</div>
                    <div class="k">Expected Category</div><div class="v">${esc(expectedCategory)}</div>
                    <div class="k">Expected Priority</div><div class="v">${esc(expectedPriority)}</div>
                </div>
            `;

            resultEl.textContent = pretty(data);
        }

        async function resetTask() {
            resetStatus.textContent = 'Resetting...';
            resetStatus.className = 'status';
            const payload = {
                task_name: taskEl.value,
                seed: Number(seedEl.value || 42),
            };
            try {
                const res = await fetch('/ui/reset', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                });
                const data = await res.json();
                renderObservation(data.observation || data);
                resultSummaryEl.className = 'chips muted';
                resultSummaryEl.textContent = 'Episode reset. Submit an action to grade.';
                resultPrettyEl.className = 'email-box muted';
                resultPrettyEl.textContent = 'Waiting for step submission.';
                resultEl.textContent = 'Episode reset. Submit an action to grade.';
                stepBtn.disabled = false;
                stepStatus.textContent = 'Ready to submit';
                stepStatus.className = 'status ok';
                resetStatus.textContent = 'Ready';
                resetStatus.className = 'status ok';
            } catch (err) {
                resetStatus.textContent = 'Reset failed';
                resetStatus.className = 'status warn';
                resultEl.textContent = String(err);
            }
        }

        async function submitStep() {
            stepStatus.textContent = 'Submitting...';
            stepStatus.className = 'status';
            const action = { category: categoryEl.value };

            if (lastDifficulty !== 'easy') {
                action.priority = priorityEl.value;
                action.summary = summaryEl.value;
                if (!action.summary.trim()) {
                    stepStatus.textContent = 'Summary is required for this task';
                    stepStatus.className = 'status warn';
                    return;
                }
            }
            if (lastDifficulty === 'hard') {
                action.action_items = actionItemsEl.value
                    .split('\\n')
                    .map((s) => s.trim())
                    .filter(Boolean);
                action.reply_draft = replyDraftEl.value;
                if (action.action_items.length === 0) {
                    stepStatus.textContent = 'Add at least one action item for hard task';
                    stepStatus.className = 'status warn';
                    return;
                }
                if (!action.reply_draft.trim()) {
                    stepStatus.textContent = 'Reply draft is required for hard task';
                    stepStatus.className = 'status warn';
                    return;
                }
            }

            try {
                const res = await fetch('/ui/step', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action }),
                });
                const data = await res.json();
                renderResult(data);
                stepStatus.textContent = data.done ? 'Episode completed' : 'Step accepted';
                stepStatus.className = 'status ok';
            } catch (err) {
                stepStatus.textContent = 'Step failed';
                stepStatus.className = 'status warn';
                resultEl.textContent = String(err);
                resultSummaryEl.className = 'chips warn';
                resultSummaryEl.textContent = 'Step failed';
                resultPrettyEl.className = 'email-box warn';
                resultPrettyEl.textContent = String(err);
            }
        }

        taskEl.addEventListener('change', updateFormByTask);
        resetBtn.addEventListener('click', resetTask);
        stepBtn.addEventListener('click', submitStep);

        updateFormByTask();
    </script>
</body>
</html>
"""

        return HTMLResponse(content=html)


def main(host: str = "0.0.0.0", port: int = 7860):
    """Entry point for direct execution."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=7860)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    args = parser.parse_args()
    main(host=args.host, port=args.port)
