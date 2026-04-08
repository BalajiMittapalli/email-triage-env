# Project Guidelines

## Code Style
- Keep Python code compatible with Python 3.11 and follow the existing type-hinted, small-function style used in `inference.py` and `email_triage_env/`.
- Prefer explicit defaults and defensive parsing around network calls, environment variables, and model output.

## Architecture
- `inference.py` is the root inference entrypoint.
- `email_triage_env/server/app.py` exposes the FastAPI environment server.
- `email_triage_env/server/email_triage_environment.py` contains the environment reset/step logic and is the source of truth for runtime behavior.
- `email_triage_env/tasks.py` defines task names, requirements, and prompt instructions.

## Build and Test
- Install dependencies with `pip install -r requirements.txt`.
- Run the environment server with `python -m uvicorn email_triage_env.server.app:app --host 0.0.0.0 --port 7860`.
- Run inference locally with `python inference.py`.

## Conventions
- Keep inference resilient: API failures, parsing issues, and missing optional fields should not crash the script.
- Preserve the required stdout markers emitted by `inference.py`.
- Prefer linking to `README.md` for general setup details instead of duplicating them here.
