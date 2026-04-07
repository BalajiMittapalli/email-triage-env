"""
Email Triage Environment Server Implementation.

Implements the OpenEnv Environment ABC for email triage tasks.
Supports three difficulty levels with deterministic grading.
"""

from typing import Any, Optional
from uuid import uuid4

try:
    from openenv.core.env_server.interfaces import Environment
    from openenv.core.env_server.types import State
except ImportError:
    from pydantic import BaseModel

    class State(BaseModel):
        episode_id: Optional[str] = None
        step_count: int = 0

    class Environment:
        SUPPORTS_CONCURRENT_SESSIONS = False
        def __init__(self, *args, **kwargs):
            pass

try:
    from models import EmailTriageAction, EmailTriageObservation
except ImportError:
    try:
        from email_triage_env.models import EmailTriageAction, EmailTriageObservation
    except ImportError:
        from ..models import EmailTriageAction, EmailTriageObservation

try:
    from email_generator import generate_email_dataset
except ImportError:
    try:
        from email_triage_env.email_generator import generate_email_dataset
    except ImportError:
        from ..email_generator import generate_email_dataset

try:
    from graders import grade
except ImportError:
    try:
        from email_triage_env.graders import grade
    except ImportError:
        from ..graders import grade

try:
    from tasks import get_task, TASK_NAMES
except ImportError:
    try:
        from email_triage_env.tasks import get_task, TASK_NAMES
    except ImportError:
        from ..tasks import get_task, TASK_NAMES


DEFAULT_TASK = "email_classify"
DEFAULT_SEED = 42


class EmailTriageEnvironment(Environment):
    """
    Email Triage environment for OpenEnv.

    Each episode presents one email. The agent analyzes it and provides
    a triage response. The environment grades the response and returns
    a score between 0.0 and 1.0.

    Supports three task types of increasing difficulty:
    - email_classify (easy): Classify email category
    - email_prioritize (medium): Classify + prioritize + summarize
    - email_full_triage (hard): Full triage with reply drafting

    Example:
        >>> env = EmailTriageEnvironment()
        >>> obs = env.reset(task_name='email_classify', seed=42)
        >>> print(obs.email_subject)
        >>> obs = env.step(EmailTriageAction(category='work'))
        >>> print(obs.score)  # 0.0 or 1.0
    """

    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self, **kwargs):
        """Initialize the email triage environment."""
        super().__init__(**kwargs) if hasattr(super(), '__init__') else None
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._dataset = None
        self._dataset_index = 0
        self._current_email = None
        self._current_task = None
        self._task_name = DEFAULT_TASK
        self._seed = DEFAULT_SEED
        self._done = False

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        task_name: Optional[str] = None,
        **kwargs: Any,
    ) -> EmailTriageObservation:
        """
        Reset the environment and present a new email.

        Args:
            seed: Random seed for reproducibility
            episode_id: Optional episode ID
            task_name: Task type (email_classify, email_prioritize, email_full_triage)
            **kwargs: Additional parameters

        Returns:
            EmailTriageObservation with the email to triage
        """
        # Update configuration
        if task_name is not None:
            if task_name not in TASK_NAMES:
                raise ValueError(f"Unknown task: {task_name}. Available: {TASK_NAMES}")
            self._task_name = task_name

        if seed is not None:
            self._seed = seed

        self._current_task = get_task(self._task_name)
        difficulty = self._current_task["difficulty"]

        # Generate or regenerate dataset
        include_threads = difficulty == "hard"
        self._dataset = generate_email_dataset(
            seed=self._seed,
            num_per_category=5,
            include_threads=include_threads,
        )

        # Get next email
        self._current_email = self._dataset[self._dataset_index % len(self._dataset)]
        self._dataset_index += 1
        self._done = False

        # Update state
        self._state = State(
            episode_id=episode_id or str(uuid4()),
            step_count=0,
        )

        # Build observation
        thread_data = None
        if difficulty == "hard" and self._current_email.get("thread"):
            thread_data = self._current_email["thread"]

        return EmailTriageObservation(
            task_name=self._task_name,
            task_difficulty=difficulty,
            email_id=self._current_email["id"],
            email_subject=self._current_email["subject"],
            email_from=self._current_email["from"],
            email_to=self._current_email.get("to", "user@company.com"),
            email_body=self._current_email["body"],
            email_date=self._current_email.get("date", ""),
            email_thread=thread_data,
            score=None,
            feedback=None,
            correct_category=None,
            correct_priority=None,
            correct_action_items=None,
            done=False,
            reward=0.0,
            metadata={
                "task_description": self._current_task.get("description", ""),
                "instructions": self._current_task.get("instructions", ""),
            },
        )

    def step(self, action: EmailTriageAction, **kwargs: Any) -> EmailTriageObservation:
        """
        Process the agent's triage action and return graded result.

        Args:
            action: EmailTriageAction with the agent's triage response

        Returns:
            EmailTriageObservation with score and feedback, done=True
        """
        self._state.step_count += 1

        # Validate current state
        if self._current_email is None or self._done:
            return EmailTriageObservation(
                task_name=self._task_name,
                task_difficulty=self._current_task["difficulty"] if self._current_task else "easy",
                done=True,
                reward=0.0,
                score=0.0,
                feedback="No active email to triage. Call reset() first.",
            )

        difficulty = self._current_task["difficulty"]

        # Build action dict for grader
        action_dict = {
            "category": action.category,
            "priority": action.priority,
            "summary": action.summary,
            "action_items": action.action_items,
            "reply_draft": action.reply_draft,
        }

        # Penalize empty/null required fields
        required = self._current_task.get("required_fields", [])
        for field in required:
            if not action_dict.get(field):
                # Zero score for missing required field
                self._done = True
                return EmailTriageObservation(
                    task_name=self._task_name,
                    task_difficulty=difficulty,
                    score=0.0,
                    feedback=f"Missing required field: '{field}'",
                    correct_category=self._current_email["category"],
                    correct_priority=self._current_email.get("priority"),
                    correct_action_items=self._current_email.get("action_items"),
                    done=True,
                    reward=0.0,
                )

        # Grade the action
        score, feedback = grade(difficulty, action_dict, self._current_email)
        self._done = True

        return EmailTriageObservation(
            task_name=self._task_name,
            task_difficulty=difficulty,
            email_id=self._current_email["id"],
            score=score,
            feedback=feedback,
            correct_category=self._current_email["category"],
            correct_priority=self._current_email.get("priority"),
            correct_action_items=self._current_email.get("action_items"),
            done=True,
            reward=score,
        )

    @property
    def state(self) -> State:
        """Get the current environment state."""
        return self._state


__all__ = ["EmailTriageEnvironment"]
