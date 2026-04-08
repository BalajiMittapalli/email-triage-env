"""
Programmatic graders for the Email Triage Environment.

Each task has a deterministic grader that returns a score between 0.0 and 1.0.
Grading criteria are clear, deterministic, and reproducible.
"""

from typing import Any, Dict, List, Optional, Tuple


def _normalize(text: Optional[str]) -> str:
    """Normalize text for comparison."""
    if text is None:
        return ""
    return text.strip().lower()


def _keyword_overlap(text1: str, text2: str) -> float:
    """
    Compute keyword overlap score between two texts.
    Returns a score between 0.0 and 1.0.
    """
    if not text1 or not text2:
        return 0.0

    # Extract meaningful words (length > 2, skip common stopwords)
    stopwords = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "may", "might", "shall", "can",
        "and", "but", "or", "nor", "not", "so", "yet", "for", "at",
        "by", "to", "in", "on", "of", "with", "from", "up", "out",
        "this", "that", "these", "those", "it", "its", "i", "me",
        "my", "we", "our", "you", "your", "he", "she", "they",
        "them", "his", "her", "their", "what", "which", "who",
        "whom", "how", "when", "where", "why", "all", "each",
        "any", "both", "few", "more", "most", "some", "such",
        "no", "if", "then", "than", "too", "very", "just",
        "about", "also", "into", "over", "after", "before",
    }

    words1 = {
        w for w in _normalize(text1).split()
        if len(w) > 2 and w not in stopwords
    }
    words2 = {
        w for w in _normalize(text2).split()
        if len(w) > 2 and w not in stopwords
    }

    if not words1 or not words2:
        return 0.0

    overlap = words1 & words2
    # Jaccard-like but weighted toward recall of reference words
    score = len(overlap) / max(len(words2), 1)
    return min(score, 1.0)


def _action_items_overlap(
    predicted: Optional[List[str]],
    reference: List[str],
) -> float:
    """
    Compute overlap between predicted and reference action items.
    Uses keyword matching for flexibility.
    Returns score between 0.0 and 1.0.
    """
    if not reference:
        # No action items expected - if agent also says none, full score
        if not predicted:
            return 1.0
        return 0.5  # Partial credit for trying

    if not predicted:
        return 0.0

    matched = 0
    for ref_item in reference:
        ref_words = {
            w for w in _normalize(ref_item).split()
            if len(w) > 2
        }
        best_match = 0.0
        for pred_item in predicted:
            pred_words = {
                w for w in _normalize(pred_item).split()
                if len(w) > 2
            }
            if ref_words and pred_words:
                overlap = len(ref_words & pred_words) / max(len(ref_words), 1)
                best_match = max(best_match, overlap)
        if best_match >= 0.3:  # Threshold for considering it a match
            matched += 1

    return matched / len(reference)


def _reply_quality_score(
    reply: Optional[str],
    email_body: str,
    category: str,
    priority: str,
) -> float:
    """
    Score the quality of a drafted reply.
    Returns score between 0.0 and 1.0.
    """
    if not reply or len(reply.strip()) < 10:
        return 0.0

    reply_lower = _normalize(reply)
    score = 0.0

    # 1. Reply is non-empty and reasonable length (0.2)
    if len(reply_lower) > 20:
        score += 0.2

    # 2. Reply is professional in tone (0.2)
    professional_markers = [
        "thank", "regards", "best", "please", "appreciate",
        "hi", "hello", "dear", "sincerely", "looking forward",
    ]
    has_professional = any(m in reply_lower for m in professional_markers)
    if has_professional:
        score += 0.2

    # 3. Reply addresses the email content (0.3)
    content_overlap = _keyword_overlap(reply, email_body)
    score += 0.3 * content_overlap

    # 4. Appropriate response given category (0.3)
    if category == "spam":
        # Should NOT reply to spam, or flag it
        spam_aware = any(
            w in reply_lower
            for w in ["spam", "ignore", "block", "delete", "flag", "report", "scam", "phishing"]
        )
        if spam_aware:
            score += 0.3
    elif category == "urgent" or priority == "critical":
        # Should acknowledge urgency
        urgency_aware = any(
            w in reply_lower
            for w in ["immediately", "urgent", "asap", "right away", "priority", "now", "on it"]
        )
        if urgency_aware:
            score += 0.3
    else:
        # General appropriateness - should feel like a real reply
        if len(reply_lower) > 50:
            score += 0.15
        if "?" in reply or "let me know" in reply_lower or "confirm" in reply_lower:
            score += 0.15

    return min(score, 1.0)


def grade_easy(
    action: Dict[str, Any],
    ground_truth: Dict[str, Any],
) -> Tuple[float, str]:
    """
    Grade easy task: email classification only.

    Scoring:
    - Exact category match: 1.0
    - No match: 0.0

    Returns:
        (score, feedback) tuple
    """
    predicted = _normalize(action.get("category", ""))
    expected = _normalize(ground_truth.get("category", ""))

    if predicted == expected:
        return 1.0, f"Correct! Category is '{expected}'."
    else:
        return 0.0, f"Incorrect. Predicted '{predicted}', correct is '{expected}'."


def grade_medium(
    action: Dict[str, Any],
    ground_truth: Dict[str, Any],
) -> Tuple[float, str]:
    """
    Grade medium task: classification + prioritization + summary.

    Scoring (weighted):
    - Category match: 0.40
    - Priority match: 0.30
    - Summary quality (keyword overlap with email body): 0.30

    Returns:
        (score, feedback) tuple
    """
    feedback_parts = []
    total_score = 0.0

    # 1. Category (0.40)
    pred_cat = _normalize(action.get("category", ""))
    true_cat = _normalize(ground_truth.get("category", ""))
    if pred_cat == true_cat:
        total_score += 0.40
        feedback_parts.append(f"Category: ✅ Correct ({true_cat})")
    else:
        feedback_parts.append(
            f"Category: ❌ Predicted '{pred_cat}', correct is '{true_cat}' (0/0.40)"
        )

    # 2. Priority (0.30)
    pred_pri = _normalize(action.get("priority", ""))
    true_pri = _normalize(ground_truth.get("priority", ""))
    if pred_pri == true_pri:
        total_score += 0.30
        feedback_parts.append(f"Priority: ✅ Correct ({true_pri})")
    else:
        # Partial credit for adjacent priority
        priority_levels = ["low", "medium", "high", "critical"]
        if pred_pri in priority_levels and true_pri in priority_levels:
            diff = abs(
                priority_levels.index(pred_pri) - priority_levels.index(true_pri)
            )
            if diff == 1:
                total_score += 0.15
                feedback_parts.append(
                    f"Priority: ⚠️ Close - predicted '{pred_pri}', "
                    f"correct is '{true_pri}' (0.15/0.30)"
                )
            else:
                feedback_parts.append(
                    f"Priority: ❌ Predicted '{pred_pri}', correct is '{true_pri}' (0/0.30)"
                )
        else:
            feedback_parts.append(
                f"Priority: ❌ Invalid value '{pred_pri}', correct is '{true_pri}' (0/0.30)"
            )

    # 3. Summary quality (0.30)
    summary = action.get("summary", "")
    email_body = ground_truth.get("body", "")
    summary_score = _keyword_overlap(summary or "", email_body)
    summary_points = 0.30 * summary_score
    total_score += summary_points
    feedback_parts.append(
        f"Summary: {'✅' if summary_score > 0.3 else '⚠️'} "
        f"Quality score: {summary_score:.2f} ({summary_points:.2f}/0.30)"
    )

    total_score = round(total_score, 4)
    feedback = " | ".join(feedback_parts)
    return total_score, feedback


def grade_hard(
    action: Dict[str, Any],
    ground_truth: Dict[str, Any],
) -> Tuple[float, str]:
    """
    Grade hard task: full triage.

    Scoring (weighted):
    - Category match: 0.20
    - Priority match: 0.20
    - Summary quality: 0.20
    - Action items extraction: 0.20
    - Reply quality: 0.20

    Returns:
        (score, feedback) tuple
    """
    feedback_parts = []
    total_score = 0.0

    # 1. Category (0.20)
    pred_cat = _normalize(action.get("category", ""))
    true_cat = _normalize(ground_truth.get("category", ""))
    if pred_cat == true_cat:
        total_score += 0.20
        feedback_parts.append(f"Category: ✅ ({true_cat})")
    else:
        feedback_parts.append(f"Category: ❌ ({pred_cat}→{true_cat})")

    # 2. Priority (0.20)
    pred_pri = _normalize(action.get("priority", ""))
    true_pri = _normalize(ground_truth.get("priority", ""))
    if pred_pri == true_pri:
        total_score += 0.20
        feedback_parts.append(f"Priority: ✅ ({true_pri})")
    else:
        priority_levels = ["low", "medium", "high", "critical"]
        if pred_pri in priority_levels and true_pri in priority_levels:
            diff = abs(
                priority_levels.index(pred_pri) - priority_levels.index(true_pri)
            )
            if diff == 1:
                total_score += 0.10
                feedback_parts.append(f"Priority: ⚠️ ({pred_pri}→{true_pri})")
            else:
                feedback_parts.append(f"Priority: ❌ ({pred_pri}→{true_pri})")
        else:
            feedback_parts.append(f"Priority: ❌ invalid")

    # 3. Summary quality (0.20)
    summary = action.get("summary", "")
    email_body = ground_truth.get("body", "")
    summary_score = _keyword_overlap(summary or "", email_body)
    total_score += 0.20 * summary_score
    feedback_parts.append(f"Summary: {summary_score:.2f}")

    # 4. Action items (0.20)
    pred_items = action.get("action_items") or []
    true_items = ground_truth.get("action_items", [])
    items_score = _action_items_overlap(pred_items, true_items)
    total_score += 0.20 * items_score
    feedback_parts.append(f"Actions: {items_score:.2f}")

    # 5. Reply quality (0.20)
    reply = action.get("reply_draft", "")
    reply_score = _reply_quality_score(
        reply, email_body, true_cat, true_pri
    )
    total_score += 0.20 * reply_score
    feedback_parts.append(f"Reply: {reply_score:.2f}")

    total_score = round(total_score, 4)
    feedback = " | ".join(feedback_parts)
    return total_score, feedback


# Maps difficulty to grader function
GRADERS = {
    "easy": grade_easy,
    "medium": grade_medium,
    "hard": grade_hard,
}


def grade(
    difficulty: str,
    action: Dict[str, Any],
    ground_truth: Dict[str, Any],
) -> Tuple[float, str]:
    """
    Grade an action using the appropriate grader for the difficulty level.

    Args:
        difficulty: Task difficulty (easy, medium, hard)
        action: Agent's action dict
        ground_truth: Ground truth email data

    Returns:
        (score, feedback) tuple where score is 0.0–1.0
    """
    grader = GRADERS.get(difficulty)
    if grader is None:
        raise ValueError(f"Unknown difficulty: {difficulty}. Use: easy, medium, hard")
    return grader(action, ground_truth)
