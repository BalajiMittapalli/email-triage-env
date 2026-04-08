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
    _env = EmailTriageEnvironment()

    @app.get("/health")
    def health():
        return {"status": "healthy"}

    @app.post("/reset")
    def reset(data: dict = {}):
        obs = _env.reset(**data)
        return {
            "observation": obs.model_dump(),
            "reward": obs.reward,
            "done": obs.done,
        }

    @app.post("/step")
    def step(data: dict = {}):
        action = EmailTriageAction(**data.get("action", data))
        obs = _env.step(action)
        return {
            "observation": obs.model_dump(),
            "reward": obs.reward,
            "done": obs.done,
        }

    @app.get("/state")
    def state():
        return _env.state.model_dump()


@app.get("/")
def root():
    """Human-friendly landing endpoint for Spaces/App tab."""
    return {
        "name": "email_triage",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "openenv": {
            "reset": "/reset",
            "step": "/step",
            "state": "/state",
            "schema": "/schema",
        },
    }


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
