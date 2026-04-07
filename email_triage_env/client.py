"""Email Triage Environment Client."""

from typing import Dict

try:
    from openenv.core import EnvClient
    from openenv.core.client_types import StepResult
    from openenv.core.env_server.types import State
except ImportError:
    # Fallback for standalone usage
    EnvClient = object
    StepResult = dict
    from pydantic import BaseModel

    class State(BaseModel):
        episode_id: str = None
        step_count: int = 0

from .models import EmailTriageAction, EmailTriageObservation


class EmailTriageEnv:
    """
    Client for the Email Triage Environment.

    Example:
        >>> from email_triage_env import EmailTriageEnv, EmailTriageAction
        >>> env = EmailTriageEnv(base_url="http://localhost:7860")
        >>> result = env.reset(task_name='email_classify', seed=42)
        >>> print(result.observation.email_subject)
        >>> result = env.step(EmailTriageAction(category='work'))
        >>> print(result.observation.score)
    """

    def _step_payload(self, action: EmailTriageAction) -> Dict:
        """Convert action to JSON payload."""
        return {
            "category": action.category,
            "priority": action.priority,
            "summary": action.summary,
            "action_items": action.action_items,
            "reply_draft": action.reply_draft,
        }

    def _parse_result(self, payload: Dict):
        """Parse server response into observation."""
        obs_data = payload.get("observation", {})
        observation = EmailTriageObservation(
            task_name=obs_data.get("task_name", "email_classify"),
            task_difficulty=obs_data.get("task_difficulty", "easy"),
            email_id=obs_data.get("email_id"),
            email_subject=obs_data.get("email_subject"),
            email_from=obs_data.get("email_from"),
            email_to=obs_data.get("email_to"),
            email_body=obs_data.get("email_body"),
            email_date=obs_data.get("email_date"),
            email_thread=obs_data.get("email_thread"),
            score=obs_data.get("score"),
            feedback=obs_data.get("feedback"),
            correct_category=obs_data.get("correct_category"),
            correct_priority=obs_data.get("correct_priority"),
            correct_action_items=obs_data.get("correct_action_items"),
            done=payload.get("done", False),
            reward=payload.get("reward", 0.0),
            metadata=obs_data.get("metadata", {}),
        )
        return observation

    def _parse_state(self, payload: Dict) -> State:
        """Parse server response into State."""
        return State(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
        )


__all__ = ["EmailTriageEnv"]
