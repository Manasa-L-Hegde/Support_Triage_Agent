"""
Response generator for Support Triage Agent
===========================================

This module creates short, safe, and user-friendly responses based only on
retrieved knowledge base documents. It avoids hallucination by never adding
external or invented facts — the response is derived solely from the provided
`doc` content.

Function:
    - generate_response(status: str, doc: str, issue: str) -> str

Design rules:
    - If `status` is "escalated", always return a polite escalation message.
    - If `status` is "replied", construct a short reply strictly using text
      extracted from `doc` (no added claims).
    - Keep replies short (150-200 chars of doc excerpt) and formatted for
      clarity. Add a single guidance line for next steps.

Why this matters:
    - Hallucination (adding facts not in source) can mislead customers and
      cause wrong actions. We avoid it by only quoting or summarizing the
      retrieved document material.
    - Short responses are easier to read and less likely to contain errors.

"""

from typing import Optional


def _clean_excerpt(text: str, max_chars: int = 180) -> str:
    """
    Produce a clean excerpt of up to `max_chars` characters from `text`.

    Behavior:
        - Strips leading/trailing whitespace
        - Replaces multiple whitespace/newlines with single spaces
        - Truncates at nearest sentence boundary before `max_chars` when possible
        - Falls back to a hard truncation with ellipsis
    """
    if not text:
        return ""

    # Normalize whitespace
    normalized = " ".join(text.split())

    if len(normalized) <= max_chars:
        return normalized

    # Try to cut at sentence boundaries before max_chars
    # Look for period, question mark, or exclamation point
    end_punct = ['. ', '? ', '! ']
    cut_pos = None
    for punct in end_punct:
        pos = normalized.rfind(punct, 0, max_chars)
        if pos != -1:
            cut_pos = pos + 1  # keep punctuation
            break

    if cut_pos is None:
        # No sentence boundary found; hard cut
        excerpt = normalized[:max_chars].rstrip()
        # Avoid chopping mid-word: remove trailing fragment after last space
        last_space = excerpt.rfind(' ')
        if last_space > int(max_chars * 0.6):
            excerpt = excerpt[:last_space]
        return excerpt + '...'

    return normalized[:cut_pos].rstrip()


def generate_response(status: str, doc: Optional[str], issue: Optional[str]) -> str:
    """
    Generate a concise, safe response for a support ticket.

    Args:
        status: "escalated" or "replied"
        doc: Retrieved document content (may be None)
        issue: Original issue text (may be None or empty)

    Returns:
        A formatted response string suitable for sending to the customer.

    Rules:
        - If `status == 'escalated'`: return polite escalation message and avoid
          making claims about fixes.
        - If `status == 'replied'`: return an excerpt from `doc` only. Do not
          add or invent information beyond what the document contains.

    Edge cases:
        - If `doc` is None and status is 'replied', fall back to a safe message
          requesting more information and/or escalation.
        - If `issue` is empty, still follow the same rules; include a generic
          guidance line.
    """
    # Normalize inputs
    status_norm = (status or "").strip().lower()
    doc_text = doc or ""
    issue_text = (issue or "").strip()

    # Context-aware prefix: add a short contextual hint based on detected
    # keywords in the user's issue. This improves the user experience by
    # acknowledging the likely area of the problem before providing the
    # grounded excerpt. It provides lightweight contextual understanding
    # without any machine learning — just deterministic substring checks.
    prefix = ""
    issue_lower = issue_text.lower()
    if "password" in issue_lower:
        prefix = "It looks like you're having a login issue.\n\n"
    elif "api" in issue_lower:
        prefix = "It seems you're facing an API issue.\n\n"
    elif "payment" in issue_lower or "charged" in issue_lower:
        prefix = "It appears to be a billing-related issue.\n\n"

    # Escalation message: concise and clear
    if status_norm == "escalated":
        return prefix + "This issue requires further assistance and has been escalated to the support team."

    # Replied case: only use the document; do not hallucinate or add facts
    if status_norm == "replied":
        if not doc_text:
            # Defensive fallback: if no doc provided, escalate wording
            return prefix + "This issue requires further assistance and has been escalated to the support team."

        # Truncate doc for safety and brevity (do not dump full document)
        excerpt = _clean_excerpt(doc_text, max_chars=160)
        return prefix + f"Here’s what you can do:\n{excerpt}...\n\nRefer to the support documentation for more details."

    # Unknown status: conservative fallback
    return "This issue requires further assistance and has been escalated to the support team."