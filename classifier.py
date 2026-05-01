"""
Classifier Module for Support Triage Agent
============================================

This module provides rule-based classification functions for support tickets.
It categorizes support requests by type and product area to enable proper
routing and response generation.

Functions:
    - classify_request(issue: str) -> str
    - detect_product_area(issue: str) -> str

Approach:
    This module uses keyword-based classification, which is simple, fast,
    and explainable. It works well for straightforward cases but has
    limitations (see docstrings for details).

    Future improvements could include:
    - Machine learning models for better accuracy
    - Fuzzy matching for typos
    - Multi-word phrase detection
    - Contextual analysis (not just keywords)
"""


def classify_request(issue: str) -> str:
    """
    Classify a support request into one of four categories.
    
    Args:
        issue (str): The combined subject and issue text from the ticket
    
    Returns:
        str: One of: "bug", "feature_request", "product_issue", "invalid"
    
    Classification Logic:
        The function checks for keywords in a priority order:
        
        1. BUG (highest priority)
           Keywords: "error", "not working", "failed", "crash", "bug"
           Example: "App crashes when I upload files" → "bug"
        
        2. FEATURE_REQUEST
           Keywords: "feature", "add", "improve", "enhancement", "request"
           Example: "Can you add dark mode?" → "feature_request"
        
        3. PRODUCT_ISSUE
           Keywords: "help", "issue", "problem", "unable"
           Example: "Unable to access my account" → "product_issue"
        
        4. INVALID (fallback)
           If no keywords match, classify as invalid
           Example: "Hello world" → "invalid"
    
    How Keyword Matching Works:
        - The function converts text to lowercase for case-insensitive matching
        - It checks if any keyword appears anywhere in the issue text
        - Keywords are checked in priority order (bugs first, invalids last)
        - The first matching category is returned
        - This is simple substring matching, not sophisticated NLP
    
    Limitations of Rule-Based Classification:
        ✗ No semantic understanding (only looks at keywords)
        ✗ Can't handle typos ("eror" instead of "error")
        ✗ Can't understand context (word order doesn't matter)
        ✗ May misclassify if keywords appear in wrong context
          Example: "I request that you fix this bug" could match both
                   "request" (feature) and "bug" (bug). Bug has priority.
        ✗ Doesn't handle compound requests well
          Example: "Add a feature to fix the bug" gets "bug" priority
    
    Safety Handling:
        - Empty strings are treated as "invalid"
        - None values would raise an error (caller should validate)
        - Whitespace-only strings are treated as "invalid"
    
    Example Usage:
        >>> classify_request("The app crashes when I click the button")
        "bug"
        
        >>> classify_request("Can you add a dark mode feature?")
        "feature_request"
        
        >>> classify_request("")
        "invalid"
    """
    
    # Safety check: handle empty or whitespace-only input
    if not issue or not issue.strip():
        return "invalid"

    issue_lower = issue.lower()

    # Updated concise keyword lists for classification
    BUG_KEYWORDS = [
        "error",
        "failed",
        "crash",
        "not working",
    ]

    FEATURE_KEYWORDS = [
        "feature",
        "add",
        "improve",
    ]

    # If any bug keywords present, classify as bug
    for kw in BUG_KEYWORDS:
        if kw in issue_lower:
            return "bug"

    # If any feature keywords present, classify as feature_request
    for kw in FEATURE_KEYWORDS:
        if kw in issue_lower:
            return "feature_request"

    # Otherwise, default to product_issue for any non-empty ticket.
    # This keeps the request type useful without overfitting to weak signals.
    return "product_issue"


def detect_product_area(issue: str) -> str:
    """
    Detect which product area or team a support ticket relates to.
    
    Args:
        issue (str): The combined subject and issue text from the ticket
    
    Returns:
        str: One of: "authentication", "billing", "fraud", "assessment",
             "api", "account_access", "general"
    
    Product Area Definitions:
        
        AUTHENTICATION
            Scope: Login, password, OTP, 2FA issues
            Keywords: "login", "password", "otp", "2fa", "sign in", "authenticate"
            Example: "Can't log in with my credentials" → "authentication"
        
        BILLING
            Scope: Payment, refund, subscription, charges
            Keywords: "billing", "payment", "refund", "charge", "subscription",
                      "invoice", "cost", "price"
            Example: "I was charged twice" → "billing"
        
        FRAUD
            Scope: Unauthorized access, account compromise, suspicious activity
            Keywords: "fraud", "stolen", "unauthorized", "hacked", "compromised",
                      "suspicious", "breach"
            Example: "Someone accessed my account without permission" → "fraud"
        
        ASSESSMENT
            Scope: Tests, coding challenges, practice problems
            Keywords: "test", "coding", "challenge", "assessment", "exam",
                      "practice", "problem", "solution"
            Example: "I'm stuck on the coding challenge" → "assessment"
        
        API
            Scope: API integration, endpoints, documentation
            Keywords: "api", "endpoint", "integration", "request", "response",
                      "json", "rest", "webhook"
            Example: "Getting 401 errors from the API" → "api"
        
        ACCOUNT_ACCESS
            Scope: Account settings, permissions, profile issues
            Keywords: "account", "access", "permission", "profile", "settings",
                      "my account", "account access"
            Example: "I can't access my account" → "account_access"
        
        GENERAL
            Fallback category when no specific area is detected
            Used for generic inquiries, feedback, or unclassified issues
    
    How Keyword Matching Works:
        - Similar to classify_request(), uses substring matching
        - Checks product areas in priority order
        - Returns first matching category
        - Case-insensitive matching
        - Single keywords are checked, not phrases (except specific ones)
    
    Limitations of Rule-Based Classification:
        ✗ Keywords can appear in wrong context
          Example: "test my API" could match both "assessment" and "api"
                   (API has priority in this implementation)
        ✗ No geographic or service-specific differentiation
        ✗ Ambiguous tickets may be misclassified
          Example: "Problem with payment API" - is it "billing" or "api"?
        ✗ New product areas require code changes
        ✗ Can't understand compound issues
          Example: "Login problem affecting account access" gets first match
    
    Priority Order (checked in this sequence):
        1. authentication (very specific domain)
        2. billing (business-critical)
        3. fraud (security-critical)
        4. assessment (specific to product)
        5. api (technical domain)
        6. account_access (broader than authentication)
        7. general (fallback)
    
    Safety Handling:
        - Empty strings default to "general"
        - None values would raise an error (caller should validate)
        - Whitespace-only strings default to "general"
    
    Example Usage:
        >>> detect_product_area("I can't log in to my account")
        "authentication"
        
        >>> detect_product_area("I was charged twice for my subscription")
        "billing"
        
        >>> detect_product_area("The API returns 500 errors")
        "api"
        
        >>> detect_product_area("")
        "general"
    """
    
    # Safety check: handle empty or whitespace-only input
    if not issue or not issue.strip():
        return "general"
    
    # Convert to lowercase for case-insensitive keyword matching
    issue_lower = issue.lower()
    
    # Define keywords for each product area
    # Checked in priority order
    
    AUTHENTICATION_KEYWORDS = [
        "login",
        "password",
        "otp",
        "2fa",
        "sign in",
        "signin",
        "authenticate",
        "auth",
        "credentials",
    ]
    
    BILLING_KEYWORDS = [
        "billing",
        "payment",
        "refund",
        "charge",
        "charged",
        "subscription",
        "invoice",
        "cost",
        "price",
        "paid",
    ]
    
    FRAUD_KEYWORDS = [
        "fraud",
        "stolen",
        "unauthorized",
        "hacked",
        "compromised",
        "suspicious",
        "breach",
        "security",
        "intrusion",
    ]
    
    ASSESSMENT_KEYWORDS = [
        "test",
        "coding",
        "challenge",
        "assessment",
        "exam",
        "practice",
        "problem",
        "solution",
        "coursework",
    ]
    
    API_KEYWORDS = [
        "api",
        "endpoint",
        "integration",
        "request",
        "response",
        "json",
        "rest",
        "webhook",
        "http",
        "401",
        "403",
        "500",
    ]
    
    ACCOUNT_ACCESS_KEYWORDS = [
        "account",
        "access",
        "permission",
        "profile",
        "settings",
        "account access",
    ]
    
    # Check for AUTHENTICATION keywords (highest priority)
    for keyword in AUTHENTICATION_KEYWORDS:
        if keyword in issue_lower:
            return "authentication"
    
    # Check for BILLING keywords
    for keyword in BILLING_KEYWORDS:
        if keyword in issue_lower:
            return "billing"
    
    # Check for FRAUD keywords
    for keyword in FRAUD_KEYWORDS:
        if keyword in issue_lower:
            return "fraud"
    
    # Check for ASSESSMENT keywords
    for keyword in ASSESSMENT_KEYWORDS:
        if keyword in issue_lower:
            return "assessment"
    
    # Check for API keywords
    for keyword in API_KEYWORDS:
        if keyword in issue_lower:
            return "api"
    
    # Check for ACCOUNT_ACCESS keywords
    for keyword in ACCOUNT_ACCESS_KEYWORDS:
        if keyword in issue_lower:
            return "account_access"
    
    # No keywords matched, default to general
    return "general"
