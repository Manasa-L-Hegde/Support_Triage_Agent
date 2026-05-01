"""
Decision module for Support Triage Agent
========================================

This module implements a safety-first decision function to determine whether a
support ticket should be automatically replied to or escalated to human
support.

Function:
    - should_escalate(issue: str, retrieved_doc: str) -> bool

Design principles:
    - Deterministic: same input always returns same output
    - Safety-first: prefer escalation when in doubt
    - Explainable rules: simple keyword and heuristic-based checks

Why escalation matters:
    Escalation is the act of flagging a ticket for human review. We escalate
    when tickets involve safety, security, legal, or financial risk, or when
    our automated pipeline lacks enough information to confidently respond.

"""

from typing import Optional


def should_escalate(issue: Optional[str], retrieved_doc: Optional[str]) -> bool:
    """
    Determine whether to escalate a support ticket to human support.

    Args:
        issue: The combined subject + issue text (may be None or empty).
        retrieved_doc: The text of the retrieved knowledge document, or None
                       if no suitable document was found.

    Returns:
        True if the ticket should be escalated, False if safe to reply
        automatically.

    Escalation Logic (deterministic rules):
        A) High-risk detection (always escalate):
            If the issue contains any of these keywords:
            - "fraud", "stolen", "unauthorized", "hacked"
            then escalate immediately because these involve security or
            trust-risk scenarios.

        B) Missing documentation:
            If `retrieved_doc` is None (no relevant KB doc found) then
            escalate so a human can provide authoritative guidance.

        C) Otherwise: safe to reply (return False)

    Rationale / Comments:
                - Over-escalation reduces system usefulness because valid tickets get
                    routed away from automation even when the knowledge base can answer
                    them safely.
                - When a document exists, we prefer a safe reply because the response
                    is grounded in trusted content rather than guesswork.
                - Missing documentation means the system cannot ground a response in
                    trusted content; escalate to avoid giving incorrect instructions.
                - This is a conservative, safety-first policy.

    Determinism:
        All checks are simple substring/length checks on normalized text;
        there is no randomness.
    """

    # Normalize inputs and handle None safely
    if issue is None:
        issue_text = ""
    else:
        issue_text = issue.strip().lower()

    # Rule A: High-risk keyword detection (always escalate)
    # We check for keywords as substrings in lowercase issue text.
    high_risk_keywords = [
        # Security and fraud only: these must always go to a human.
        "fraud",
        "stolen",
        "unauthorized",
        "hacked",
    ]

    for kw in high_risk_keywords:
        if kw in issue_text:
            return True

    # Rule B: If a document exists, prefer a safe reply.
    # This avoids over-escalation because grounded answers are more useful
    # than routing a solvable ticket to a human.
    if retrieved_doc is not None:
        return False

    # Rule C: Missing documentation.
    # If we couldn't retrieve a document, we escalate because we lack a reliable
    # source to base an automated reply on.
    if retrieved_doc is None:
        return True

    # If none of the escalation conditions are met, it is safe to reply
    return False
