"""
Data models for the Email Triage Environment.

These models define the Action and Observation types used by the OpenEnv
integration for email triage tasks. Uses Pydantic for validation.
"""

from typing import Any, Dict, List, Optional

from pydantic import Field

try:
    from openenv.core.env_server.types import Action, Observation
except ImportError:
    from pydantic import BaseModel

    class Action(BaseModel):
        """Fallback Action base class."""
        metadata: Dict[str, Any] = Field(default_factory=dict)

    class Observation(BaseModel):
        """Fallback Observation base class."""
        done: bool = Field(default=False)
        reward: float = Field(default=0.0)
        metadata: Dict[str, Any] = Field(default_factory=dict)


class EmailTriageAction(Action):
    """
    Action for the Email Triage environment — the agent's triage response.

    Fields used depend on task difficulty:
    - Easy (classify): only `category` is required
    - Medium (prioritize): `category`, `priority`, `summary` required
    - Hard (full_triage): all fields required
    """

    category: str = Field(
        ...,
        description=(
            "Email category classification. "
            "Must be one of: spam, work, personal, urgent, newsletter"
        ),
    )
    priority: Optional[str] = Field(
        default=None,
        description=(
            "Email priority level. "
            "Must be one of: low, medium, high, critical. "
            "Required for medium and hard tasks."
        ),
    )
    summary: Optional[str] = Field(
        default=None,
        description=(
            "Brief summary of the email content and sender intent. "
            "Required for medium and hard tasks."
        ),
    )
    action_items: Optional[List[str]] = Field(
        default=None,
        description=(
            "List of action items extracted from the email. "
            "Required for hard tasks."
        ),
    )
    reply_draft: Optional[str] = Field(
        default=None,
        description=(
            "Draft reply to the email. "
            "Required for hard tasks."
        ),
    )


class EmailTriageObservation(Observation):
    """
    Observation returned by the Email Triage environment.

    Contains the email to triage and feedback after the agent acts.
    """

    task_name: str = Field(
        default="email_classify",
        description="Name of the current task",
    )
    task_difficulty: str = Field(
        default="easy",
        description="Difficulty level: easy, medium, or hard",
    )
    email_id: Optional[str] = Field(
        default=None,
        description="Unique identifier for the email",
    )
    email_subject: Optional[str] = Field(
        default=None,
        description="Subject line of the email",
    )
    email_from: Optional[str] = Field(
        default=None,
        description="Sender of the email",
    )
    email_to: Optional[str] = Field(
        default=None,
        description="Recipient of the email",
    )
    email_body: Optional[str] = Field(
        default=None,
        description="Body content of the email",
    )
    email_date: Optional[str] = Field(
        default=None,
        description="Date the email was sent",
    )
    email_thread: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Email thread history for hard tasks",
    )
    score: Optional[float] = Field(
        default=None,
        description="Grader score (0.0 to 1.0) after step",
    )
    feedback: Optional[str] = Field(
        default=None,
        description="Detailed grader feedback after step",
    )
    correct_category: Optional[str] = Field(
        default=None,
        description="Correct category (revealed after step)",
    )
    correct_priority: Optional[str] = Field(
        default=None,
        description="Correct priority (revealed after step)",
    )
    correct_action_items: Optional[List[str]] = Field(
        default=None,
        description="Correct action items (revealed after step for hard tasks)",
    )


__all__ = [
    "EmailTriageAction",
    "EmailTriageObservation",
]
