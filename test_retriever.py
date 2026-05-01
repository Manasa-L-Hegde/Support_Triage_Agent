"""
Retriever Test Script
=====================

This script demonstrates how the retriever module works step-by-step.
It loads a knowledge base and retrieves documents for different issues.
"""

from retriever import load_corpus, retrieve_document, extract_keywords, calculate_relevance_score


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def test_retriever():
    """Run demonstration tests of the retriever module."""
    
    # ========================================================================
    # STEP 1: LOAD THE KNOWLEDGE BASE
    # ========================================================================
    print_section("STEP 1: Loading Knowledge Base (Corpus)")
    
    print("\nLoading documents from 'knowledge_base/' folder...")
    docs = load_corpus("knowledge_base/")
    
    print(f"\n✓ Successfully loaded {len(docs)} documents")
    print("\nDocuments loaded:")
    print("  1. password_reset.txt")
    print("  2. api_auth.txt")
    print("  3. billing_faq.txt")
    print("  4. account_access.txt")
    
    # ========================================================================
    # STEP 2: DEMONSTRATE KEYWORD EXTRACTION
    # ========================================================================
    print_section("STEP 2: How Keyword Extraction Works")
    
    test_issues = [
        "How do I reset my password?",
        "I'm getting 401 errors from the API",
        "I was charged twice for my subscription"
    ]
    
    for issue in test_issues:
        keywords = extract_keywords(issue)
        print(f"\nOriginal: \"{issue}\"")
        print(f"Keywords: {keywords}")
    
    # ========================================================================
    # STEP 3: DEMONSTRATE SCORING
    # ========================================================================
    print_section("STEP 3: How Scoring Works (Detailed Example)")
    
    issue = "How do I reset my password?"
    print(f"\nIssue: \"{issue}\"")
    print(f"Keywords from issue: {extract_keywords(issue)}")
    
    print("\n--- Scoring each document ---\n")
    
    for i, doc in enumerate(docs, 1):
        score = calculate_relevance_score(issue, doc)
        doc_preview = doc[:50].replace("\n", " ") + "..."
        print(f"Document {i}: \"{doc_preview}\"")
        print(f"  Score: {score:.2f}")
        print()
    
    # ========================================================================
    # STEP 4: RETRIEVAL WITH THRESHOLD
    # ========================================================================
    print_section("STEP 4: Document Retrieval (With Threshold)")
    
    test_cases = [
        ("How do I reset my password?", 2.0),
        ("I'm getting 401 errors from the API", 2.0),
        ("I was charged twice", 2.0),
        ("xyz abc 123 random text", 2.0),  # Should return None
    ]
    
    for issue, threshold in test_cases:
        print(f"\nQuery: \"{issue}\"")
        print(f"Threshold: {threshold}")
        
        result = retrieve_document(issue, docs, threshold=threshold)
        
        if result:
            preview = result[:100].replace("\n", " ")
            print(f"✓ FOUND: {preview}...")
        else:
            print(f"✗ NOT FOUND: No document met the threshold")
    
    # ========================================================================
    # STEP 5: SHOWING HOW THRESHOLD MATTERS
    # ========================================================================
    print_section("STEP 5: Why Threshold Matters")
    
    issue = "xyz abc 123"  # Random query with no good matches
    print(f"\nQuery: \"{issue}\" (intentionally vague/random)")
    
    for threshold in [0.5, 1.0, 2.0, 3.0]:
        result = retrieve_document(issue, docs, threshold=threshold)
        status = "FOUND" if result else "NOT FOUND"
        print(f"\nThreshold {threshold}: {status}")
        if result:
            preview = result[:80].replace("\n", " ")
            print(f"  Result: {preview}...")
    
    print(f"\nNotice how with lower thresholds, we get poor matches!")
    print(f"Threshold 2.0 is recommended for balance.")
    
    # ========================================================================
    # STEP 6: INTEGRATION WITH TRIAGE PIPELINE
    # ========================================================================
    print_section("STEP 6: How This Integrates Into Main Pipeline")
    
    print("""
In main.py, the retriever is used like this:

    issue_text = "I can't log in, password reset not working"
    
    # Step 1: Classify the issue (using classifier.py)
    request_type = classify_request(issue_text)  # → "bug"
    
    # Step 2: Detect product area (using classifier.py)
    product_area = detect_product_area(issue_text)  # → "authentication"
    
    # Step 3: Retrieve relevant documentation (using retriever.py)
    docs = load_corpus("knowledge_base/")
    relevant_doc = retrieve_document(issue_text, docs)
    
    # Step 4: Generate response using the retrieved document
    response = generate_response(request_type, product_area, relevant_doc)
    
    # Result:
    # {
    #   "type": "bug",
    #   "area": "authentication",
    #   "documentation": [relevant doc about password reset],
    #   "response": "Based on our documentation, here's how to reset..."
    # }
    """)


if __name__ == "__main__":
    test_retriever()
    print("\n" + "="*70)
    print("Test Complete!")
    print("="*70 + "\n")
