"""
Task definitions for the Email Triage Environment.

Defines three tasks with increasing difficulty:
- Easy: Email classification
- Medium: Classification + prioritization + summary
- Hard: Full triage with reply drafting and action item extraction
"""

from typing import Any, Dict, List

TASKS: Dict[str, Dict[str, Any]] = {
    "email_classify": {
        "name": "email_classify",
        "difficulty": "easy",
        "description": (
            "Classify the email into one of the following categories: "
            "spam, work, personal, urgent, newsletter. "
            "Only the 'category' field is required in your response."
        ),
        "required_fields": ["category"],
        "max_steps": 1,
        "valid_categories": ["spam", "work", "personal", "urgent", "newsletter"],
        "valid_priorities": [],
        "instructions": (
            "You are an email triage assistant. Read the email carefully and "
            "classify it into exactly one category.\n\n"
            "Categories:\n"
            "- spam: Unsolicited, scam, phishing, or junk emails\n"
            "- work: Professional/business emails related to job tasks\n"
            "- personal: Personal communications, social, family\n"
            "- urgent: Time-critical emails requiring immediate action\n"
            "- newsletter: Subscriptions, digests, promotional content from services\n\n"
            "Respond with ONLY the category name."
        ),
    },
    "email_prioritize": {
        "name": "email_prioritize",
        "difficulty": "medium",
        "description": (
            "Classify the email category AND assign a priority level, "
            "plus provide a brief summary of the sender's intent. "
            "Fields required: category, priority, summary."
        ),
        "required_fields": ["category", "priority", "summary"],
        "max_steps": 1,
        "valid_categories": ["spam", "work", "personal", "urgent", "newsletter"],
        "valid_priorities": ["low", "medium", "high", "critical"],
        "instructions": (
            "You are an email triage assistant. Read the email and provide:\n\n"
            "1. CATEGORY: One of: spam, work, personal, urgent, newsletter\n"
            "2. PRIORITY: One of: low, medium, high, critical\n"
            "3. SUMMARY: A brief 1-2 sentence summary of the email content "
            "and what the sender wants.\n\n"
            "Priority guidelines:\n"
            "- low: Informational, no action needed\n"
            "- medium: Action needed but not time-sensitive\n"
            "- high: Important action needed relatively soon\n"
            "- critical: Immediate action required, time-sensitive crisis\n\n"
            "Respond in this exact format:\n"
            "CATEGORY: <category>\n"
            "PRIORITY: <priority>\n"
            "SUMMARY: <your summary>"
        ),
    },
    "email_full_triage": {
        "name": "email_full_triage",
        "difficulty": "hard",
        "description": (
            "Full email triage: classify, prioritize, summarize, extract "
            "action items, and draft an appropriate reply. "
            "All fields required: category, priority, summary, action_items, reply_draft."
        ),
        "required_fields": ["category", "priority", "summary", "action_items", "reply_draft"],
        "max_steps": 1,
        "valid_categories": ["spam", "work", "personal", "urgent", "newsletter"],
        "valid_priorities": ["low", "medium", "high", "critical"],
        "instructions": (
            "You are an email triage assistant performing full triage. "
            "Read the email (and thread if provided) carefully and provide:\n\n"
            "1. CATEGORY: One of: spam, work, personal, urgent, newsletter\n"
            "2. PRIORITY: One of: low, medium, high, critical\n"
            "3. SUMMARY: A concise summary of the email content and sender intent\n"
            "4. ACTION_ITEMS: List of specific action items extracted from the email\n"
            "5. REPLY_DRAFT: Draft an appropriate reply to the email\n\n"
            "Respond in this exact format:\n"
            "CATEGORY: <category>\n"
            "PRIORITY: <priority>\n"
            "SUMMARY: <your summary>\n"
            "ACTION_ITEMS:\n"
            "- <item 1>\n"
            "- <item 2>\n"
            "REPLY_DRAFT:\n"
            "<your draft reply>"
        ),
    },
}

TASK_NAMES: List[str] = list(TASKS.keys())
DIFFICULTY_ORDER: List[str] = ["easy", "medium", "hard"]


def get_task(task_name: str) -> Dict[str, Any]:
    """Get task definition by name."""
    if task_name not in TASKS:
        raise ValueError(
            f"Unknown task: {task_name}. Available: {TASK_NAMES}"
        )
    return TASKS[task_name]


def get_task_instructions(task_name: str) -> str:
    """Get task-specific instructions for the LLM prompt."""
    return get_task(task_name)["instructions"]
