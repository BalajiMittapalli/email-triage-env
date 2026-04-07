# Email Triage Environment — OpenEnv RL Challenge

A real-world email triage environment built on the [OpenEnv](https://github.com/meta-pytorch/OpenEnv) specification for the Meta PyTorch Hackathon.

## 🎯 Environment Overview

The Email Triage Environment simulates a real-world task that knowledge workers perform daily: reading, classifying, prioritizing, and responding to emails. An AI agent must analyze incoming emails and perform triage operations with increasing complexity.

### Motivation

Email triage is one of the most common and time-consuming tasks in modern workplaces. Workers spend an average of 2.5 hours per day on email. An effective AI triage agent could dramatically improve productivity by:
- Automatically filtering spam and low-priority messages
- Highlighting urgent items that need immediate attention
- Drafting responses to routine emails
- Extracting action items from complex threads

## 📋 Action Space

```python
class EmailTriageAction(Action):
    category: str       # spam | work | personal | urgent | newsletter
    priority: str       # low | medium | high | critical (medium/hard tasks)
    summary: str        # Brief summary (medium/hard tasks)
    action_items: List   # Extracted action items (hard tasks)
    reply_draft: str    # Drafted reply (hard tasks)
```

## 👁️ Observation Space

```python
class EmailTriageObservation(Observation):
    task_name: str          # Current task identifier
    task_difficulty: str    # easy | medium | hard
    email_subject: str      # Email subject line
    email_from: str         # Sender address
    email_body: str         # Email body content
    email_thread: List      # Thread history (hard tasks)
    score: float            # Grader score 0.0-1.0 (after step)
    feedback: str           # Grader feedback (after step)
```

## 🎮 Tasks

| # | Task Name | Difficulty | Description | Grading |
|---|-----------|-----------|-------------|---------|
| 1 | `email_classify` | Easy | Classify email category | Exact match: 1.0 or 0.0 |
| 2 | `email_prioritize` | Medium | Classify + prioritize + summarize | Weighted: category(0.4) + priority(0.3) + summary(0.3) |
| 3 | `email_full_triage` | Hard | Full triage with reply drafting | Weighted: 5 components × 0.2 each |

### Difficulty Progression
- **Easy**: Binary classification — is the agent able to correctly identify email types?
- **Medium**: Multi-dimensional analysis — can the agent assess urgency and extract meaning?
- **Hard**: Full cognitive task — can the agent understand context, extract action items, and compose appropriate replies?

## 🏆 Reward Function

The reward function provides **incremental feedback** throughout the trajectory:

- **Partial credit**: Correct category but wrong priority still earns points
- **Quality scoring**: Summary and reply quality assessed via keyword overlap
- **Penalization**: Empty or missing required fields receive 0.0
- **Adjacent credit**: Priority off by one level receives partial points (e.g., "medium" when "high" was correct)

## 🚀 Setup & Usage

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the environment server
python -m uvicorn email_triage_env.server.app:app --host 0.0.0.0 --port 7860

# Run inference
export HF_TOKEN="your_token_here"
python inference.py
```

### Docker

```bash
# Build
docker build -t email-triage-env .

# Run
docker run -p 7860:7860 email-triage-env
```

### Hugging Face Spaces

The environment is deployed at: https://huggingface.co/spaces/BalajiMittapalli/email-triage-env

## 📊 Baseline Performance

Using `Qwen/Qwen2.5-72B-Instruct` via HF Inference API:

| Task | Difficulty | Scores | Avg Score |
|------|-----------|--------|-----------|
| email_classify | Easy | 1.00, 1.00, 1.00 | **1.00** |
| email_prioritize | Medium | 0.71, 0.33, 0.75 | **0.60** |
| email_full_triage | Hard | 0.70, 0.69, 0.63 | **0.67** |

## 📁 Project Structure

```
├── inference.py                          # Root inference script
├── Dockerfile                            # Container definition
├── openenv.yaml                          # OpenEnv manifest
├── pyproject.toml                        # Dependencies
├── requirements.txt                      # Pip requirements
├── README.md                             # This file
│
└── email_triage_env/                     # Environment package
    ├── __init__.py                       # Exports
    ├── models.py                         # Pydantic Action/Observation models
    ├── client.py                         # EnvClient implementation
    ├── tasks.py                          # Task definitions (easy/medium/hard)
    ├── graders.py                        # Programmatic graders (0.0–1.0)
    ├── email_generator.py               # Deterministic email dataset
    │
    └── server/
        ├── __init__.py
        ├── email_triage_environment.py   # Environment(ABC) implementation
        └── app.py                        # FastAPI server
```

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_BASE_URL` | LLM API endpoint | `https://router.huggingface.co/v1` |
| `MODEL_NAME` | Model identifier | `Qwen/Qwen2.5-72B-Instruct` |
| `HF_TOKEN` | Hugging Face token | *(required)* |

## 📜 License

BSD-3-Clause — Compatible with OpenEnv.
