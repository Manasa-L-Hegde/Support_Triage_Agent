"""
Test script for response.generate_response()
"""
from response import generate_response


def run_tests():
    docs = [
        "Password Reset Guide\n\nIf you've forgotten your password, follow these steps: Click 'Forgot Password'...",
        "API Authentication Documentation\n\nOur API uses token-based authentication. 401 indicates missing token...",
    ]

    cases = [
        ("replied", docs[0], "How do I reset my password?"),
        ("replied", docs[1], "I'm getting 401 from the API"),
        ("replied", None, "My issue is missing doc"),
        ("escalated", docs[0], "Payment dispute"),
        ("unknown", docs[0], "Some issue"),
    ]

    for i, (status, doc, issue) in enumerate(cases, 1):
        print(f"\nCase {i}: status={status}, doc={'Yes' if doc else 'None'}, issue={issue}\n")
        print(generate_response(status, doc, issue))


if __name__ == '__main__':
    run_tests()
