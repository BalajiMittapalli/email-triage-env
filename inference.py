"""
inference.py — Baseline Inference Script for Email Triage Environment.

This script uses the OpenAI Client to evaluate an LLM agent within the
Email Triage OpenEnv environment. It runs all three tasks (easy, medium, hard)
and outputs results in the required [START]/[STEP]/[END] format.

Environment Variables:
    API_BASE_URL: API endpoint for the LLM (default: HF Inference API)
    MODEL_NAME: Model identifier (default: Qwen/Qwen2.5-72B-Instruct)
    HF_TOKEN: Hugging Face API token (required, no default)
"""

import os
import sys
import json
import traceback
from typing import Any, Dict, List, Optional, Tuple

from openai import OpenAI

# ---------------------------------------------------------------------------
# Environment Variables
# ---------------------------------------------------------------------------
API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "https://router.huggingface.co/v1",
)
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")

if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

# ---------------------------------------------------------------------------
# OpenAI Client
# ---------------------------------------------------------------------------
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN,
)

# ---------------------------------------------------------------------------
# Import environment components
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from email_triage_env.models import EmailTriageAction, EmailTriageObservation
from email_triage_env.server.email_triage_environment import EmailTriageEnvironment
from email_triage_env.tasks import TASKS, get_task_instructions


# ---------------------------------------------------------------------------
# LLM Agent
# ---------------------------------------------------------------------------

def build_prompt(observation: EmailTriageObservation) -> str:
    """Build the LLM prompt from the observation."""
    task_name = observation.task_name
    difficulty = observation.task_difficulty
    instructions = get_task_instructions(task_name)

    prompt_parts = [
        f"TASK: {task_name} (Difficulty: {difficulty})\n",
        f"INSTRUCTIONS:\n{instructions}\n",
        "=" * 60,
        f"\nEMAIL TO TRIAGE:",
        f"From: {observation.email_from}",
        f"To: {observation.email_to}",
        f"Date: {observation.email_date}",
        f"Subject: {observation.email_subject}",
        f"\nBody:\n{observation.email_body}",
    ]

    # Add thread for hard tasks
    if observation.email_thread and difficulty == "hard":
        prompt_parts.append("\n" + "=" * 60)
        prompt_parts.append("EMAIL THREAD (oldest first):")
        for i, msg in enumerate(observation.email_thread):
            prompt_parts.append(f"\n--- Message {i + 1} ---")
            prompt_parts.append(f"From: {msg.get('from', 'unknown')}")
            prompt_parts.append(f"Date: {msg.get('date', 'unknown')}")
            prompt_parts.append(f"Body: {msg.get('body', '')}")

    prompt_parts.append("\n" + "=" * 60)

    # Add response format instructions based on difficulty
    if difficulty == "easy":
        prompt_parts.append(
            "\nRespond with ONLY a JSON object:\n"
            '{"category": "<spam|work|personal|urgent|newsletter>"}'
        )
    elif difficulty == "medium":
        prompt_parts.append(
            "\nRespond with ONLY a JSON object:\n"
            "{\n"
            '  "category": "<spam|work|personal|urgent|newsletter>",\n'
            '  "priority": "<low|medium|high|critical>",\n'
            '  "summary": "<brief summary of email>"\n'
            "}"
        )
    else:  # hard
        prompt_parts.append(
            "\nRespond with ONLY a JSON object:\n"
            "{\n"
            '  "category": "<spam|work|personal|urgent|newsletter>",\n'
            '  "priority": "<low|medium|high|critical>",\n'
            '  "summary": "<brief summary>",\n'
            '  "action_items": ["<item1>", "<item2>", ...],\n'
            '  "reply_draft": "<your drafted reply>"\n'
            "}"
        )

    return "\n".join(prompt_parts)


def call_llm(prompt: str) -> str:
    """Call the LLM and return the response text."""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert email triage assistant. "
                        "Always respond with valid JSON only. "
                        "No explanations, no markdown, no extra text. "
                        "Just output the JSON object."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=1024,
        )
        content = response.choices[0].message.content
        return content.strip() if content else '{}'
    except Exception as e:
        return json.dumps({"category": "work", "error": str(e)})


def _extract_json(text: str) -> Dict[str, Any]:
    """Robustly extract JSON from LLM response text."""
    import re

    text = text.strip()

    # Remove markdown code fences
    if "```" in text:
        lines = text.split("\n")
        cleaned = []
        in_fence = False
        for line in lines:
            if line.strip().startswith("```"):
                in_fence = not in_fence
                continue
            cleaned.append(line)
        text = "\n".join(cleaned).strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON object with balanced braces
    brace_start = text.find("{")
    if brace_start != -1:
        depth = 0
        for i in range(brace_start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[brace_start : i + 1])
                    except json.JSONDecodeError:
                        break

    # Last resort: regex-based field extraction
    data = {}
    for field in ["category", "priority", "summary", "reply_draft"]:
        match = re.search(rf'"{field}"\s*:\s*"([^"]+)"', text)
        if match:
            data[field] = match.group(1)

    # Try to extract action_items array
    items_match = re.search(r'"action_items"\s*:\s*\[([^\]]+)\]', text)
    if items_match:
        items_text = items_match.group(1)
        items = re.findall(r'"([^"]+)"', items_text)
        if items:
            data["action_items"] = items

    return data


def parse_llm_response(
    response_text: str,
    difficulty: str,
) -> Dict[str, Any]:
    """Parse LLM response into action fields."""
    data = _extract_json(response_text)

    # Build result with sensible defaults per difficulty
    category = data.get("category", "work")

    # Normalize category
    valid_categories = ["spam", "work", "personal", "urgent", "newsletter"]
    if isinstance(category, str) and category.lower() in valid_categories:
        category = category.lower()
    else:
        category = "work"

    result: Dict[str, Any] = {"category": category}

    if difficulty == "easy":
        result["priority"] = None
        result["summary"] = None
        result["action_items"] = None
        result["reply_draft"] = None
    elif difficulty == "medium":
        priority = data.get("priority", "medium")
        valid_priorities = ["low", "medium", "high", "critical"]
        if isinstance(priority, str) and priority.lower() in valid_priorities:
            priority = priority.lower()
        else:
            priority = "medium"
        result["priority"] = priority
        result["summary"] = data.get("summary") or "Email requires attention."
        result["action_items"] = None
        result["reply_draft"] = None
    else:  # hard
        priority = data.get("priority", "medium")
        valid_priorities = ["low", "medium", "high", "critical"]
        if isinstance(priority, str) and priority.lower() in valid_priorities:
            priority = priority.lower()
        else:
            priority = "medium"
        result["priority"] = priority
        result["summary"] = data.get("summary") or "Email requires review and response."
        result["action_items"] = data.get("action_items") or ["Review and respond to email"]
        result["reply_draft"] = data.get("reply_draft") or (
            "Thank you for your email. I have reviewed the contents and "
            "will take the necessary action. Please let me know if you "
            "need any further information. Best regards."
        )

    return result


# ---------------------------------------------------------------------------
# Run Inference
# ---------------------------------------------------------------------------

def run_task(
    env: EmailTriageEnvironment,
    task_name: str,
    num_episodes: int = 3,
    seed: int = 42,
) -> Tuple[bool, int, List[float]]:
    """
    Run a task for multiple episodes and emit output in the required format.

    Args:
        env: Environment instance
        task_name: Task name
        num_episodes: Number of episodes to run
        seed: Random seed

    Returns:
        (overall_success, total_steps, all_rewards)
    """
    task = TASKS[task_name]
    difficulty = task["difficulty"]
    benchmark = "email_triage"

    all_rewards = []
    total_steps = 0
    overall_success = True
    last_error = None

    # Emit [START]
    print(
        f"[START] task={task_name} env={benchmark} model={MODEL_NAME}",
        flush=True,
    )

    try:
        for episode in range(num_episodes):
            # Reset environment
            obs = env.reset(task_name=task_name, seed=seed + episode)

            # Build prompt and call LLM
            prompt = build_prompt(obs)
            llm_response = call_llm(prompt)

            # Parse response
            action_dict = parse_llm_response(llm_response, difficulty)

            # Create action
            action = EmailTriageAction(**action_dict)

            # Step
            result = env.step(action)

            total_steps += 1
            reward = float(result.reward or 0.0)
            all_rewards.append(reward)
            done = result.done

            # Check for error
            error_msg = "null"
            if result.feedback and "Missing required" in result.feedback:
                error_msg = result.feedback
                last_error = error_msg

            # Emit [STEP]
            action_str = f"triage(category='{action.category}'"
            if action.priority:
                action_str += f",priority='{action.priority}'"
            action_str += ")"

            print(
                f"[STEP] step={total_steps} "
                f"action={action_str} "
                f"reward={reward:.2f} "
                f"done={'true' if done else 'false'} "
                f"error={error_msg}",
                flush=True,
            )

            if reward < 0.5:
                overall_success = False

    except Exception as e:
        total_steps += 1
        all_rewards.append(0.0)
        overall_success = False
        last_error = str(e)

        print(
            f"[STEP] step={total_steps} "
            f"action=error() "
            f"reward=0.00 "
            f"done=true "
            f"error={last_error}",
            flush=True,
        )

    # Emit [END]
    rewards_str = ",".join(f"{r:.2f}" for r in all_rewards)
    print(
        f"[END] success={'true' if overall_success else 'false'} "
        f"steps={total_steps} "
        f"rewards={rewards_str}",
        flush=True,
    )

    return overall_success, total_steps, all_rewards


def main():
    """Main entry point — run all three tasks."""
    env = EmailTriageEnvironment()

    all_success = True

    for task_name in ["email_classify", "email_prioritize", "email_full_triage"]:
        success, steps, rewards = run_task(
            env=env,
            task_name=task_name,
            num_episodes=3,
            seed=42,
        )
        if not success:
            all_success = False

    return 0 if all_success else 1


if __name__ == "__main__":
    sys.exit(main())
