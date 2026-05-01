"""
Test script for decision.should_escalate()
"""
from decision import should_escalate


def run_tests():
    cases = [
        # High-risk keywords
        ("I think there's fraud on my account, someone charged me", None),
        ("Account was hacked and stolen data", "some doc"),

        # Low-confidence (short)
        ("Help!", "some doc"),
        ("Can't login", "some doc"),

        # Missing documentation
        ("How do I reset my password?", None),

        # Safe case
        ("How do I reset my password? I clicked forgot password and didn't get email", "Password guide doc"),

        # Payment-related
        ("My card was charged twice", "billing doc"),

        # Longer but not risky
        ("I am seeing a UI glitch when opening settings, images not loading properly", "ui doc"),
    ]

    print('\nDecision tests:\n')
    for i, (issue, doc) in enumerate(cases, 1):
        escalate = should_escalate(issue, doc)
        print(f"Case {i}: issue=\"{issue}\" retrieved_doc={'Yes' if doc else 'None'} -> escalate={escalate}")


if __name__ == '__main__':
    run_tests()
