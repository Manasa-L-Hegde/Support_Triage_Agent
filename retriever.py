"""
Retriever Module for Support Triage Agent
===========================================

This module is responsible for finding the most relevant support documentation
for a given support issue. It searches through a knowledge base (corpus) of
documents and returns the best match.

Functions:
    - load_corpus(corpus_path: str) -> list
    - retrieve_document(issue: str, docs: list) -> str or None

Key Concept: CORPUS
    A corpus is a collection of text documents (like a knowledge base or FAQ).
    Example:
        Document 1: "How to reset your password"
        Document 2: "Understanding API authentication"
        Document 3: "Billing and payment methods"
    
    When a customer asks "How do I change my password?", we search the corpus
    to find the most relevant document.

Approach:
    This module uses keyword-based retrieval, which:
    ✓ Is fast and deterministic
    ✓ Doesn't require machine learning
    ✓ Results are explainable
    ✗ Doesn't understand meaning (semantic understanding)
    ✗ Can't handle typos or synonyms
    ✗ May fail with vague queries
"""

import os
from typing import List, Optional


# ============================================================================
# STEP 1: CORPUS LOADING
# ============================================================================

def load_corpus(corpus_path: str) -> List[str]:
    """
    Load all .txt files from a folder to build a document corpus.
    
    Args:
        corpus_path (str): Path to folder containing .txt files
                           Example: "docs/knowledge_base/"
    
    Returns:
        List[str]: List of document contents (strings)
                   Example: ["How to reset password...", "API guide...", ...]
                   Returns empty list if folder doesn't exist or has no .txt files
    
    What it does:
        1. Check if the folder exists
        2. List all .txt files in the folder
        3. Read each .txt file
        4. Store content in a list
        5. Return the list
    
    Why each step matters:
        - Checking folder: Prevents crashes if path is wrong
        - Reading files: .txt files are simple text documents
        - Returning list: Easy to iterate through documents later
    
    Safety Handling:
        - If folder doesn't exist → return empty list (no error)
        - If no .txt files found → return empty list
        - If file can't be read → skip it and continue
    
    Example Usage:
        >>> docs = load_corpus("data/knowledge_base/")
        >>> len(docs)
        15  # Found 15 documents
        
        >>> docs[0]
        "How to reset your password: Click forgot password..."
    """
    
    documents = []
    
    # Safety check: Does the folder exist?
    if not os.path.exists(corpus_path):
        print(f"Warning: Corpus folder not found: {corpus_path}")
        return documents  # Return empty list
    
    # Safety check: Is it actually a folder?
    if not os.path.isdir(corpus_path):
        print(f"Warning: Path is not a folder: {corpus_path}")
        return documents  # Return empty list
    
    try:
        # List all files in the folder
        all_files = os.listdir(corpus_path)
        
        # Filter for .txt files only
        txt_files = [f for f in all_files if f.endswith(".txt")]
        
        if not txt_files:
            print(f"Warning: No .txt files found in {corpus_path}")
            return documents
        
        # Read each .txt file
        for filename in txt_files:
            filepath = os.path.join(corpus_path, filename)
            
            try:
                # Open and read the file
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    documents.append(content)
                    print(f"  Loaded: {filename} ({len(content)} characters)")
            
            except UnicodeDecodeError:
                # File encoding error - skip this file
                print(f"  Skipped: {filename} (encoding error)")
                continue
            
            except IOError as e:
                # File read error - skip this file
                print(f"  Skipped: {filename} ({e})")
                continue
    
    except Exception as e:
        # Unexpected error
        print(f"Error reading corpus folder: {e}")
        return documents
    
    print(f"Total documents loaded: {len(documents)}")
    return documents


# ============================================================================
# STEP 2: STOPWORDS AND TEXT PREPROCESSING
# ============================================================================

def get_stopwords() -> set:
    """
    Get a set of common English words to ignore during matching.
    
    Returns:
        set: Words to ignore when analyzing text
    
    What are stopwords?
        Stopwords are super common words that appear in almost every text.
        They don't add much meaning:
        - Articles: "the", "a", "an"
        - Verbs: "is", "are", "be"
        - Prepositions: "to", "from", "in", "on"
        - Pronouns: "I", "you", "it", "we"
        - Conjunctions: "and", "or", "but"
    
    Why remove them?
        ✓ Reduces noise in keyword matching
        ✓ Focuses on meaningful words ("bug", "password", "crash")
        ✓ Improves relevance scoring
        ✓ Makes retrieval faster
    
    Example:
        Original: "What is the best way to reset my password?"
        After removing stopwords: ["best", "way", "reset", "password"]
        These 4 words are much more meaningful than 10 words!
    """
    
    # Minimal stopword set for retrieval (keeps scoring focused)
    stopwords = {"the", "is", "a", "to", "of", "and", "in", "for", "on", "it", "this", "that"}
    
    return stopwords


def extract_keywords(text: str) -> List[str]:
    """
    Extract meaningful keywords from text by removing stopwords.
    
    Args:
        text (str): Raw text to analyze
    
    Returns:
        List[str]: Filtered keywords (lowercase, no stopwords)
    
    What it does:
        1. Convert text to lowercase (so "Bug" = "bug")
        2. Remove punctuation
        3. Split into words
        4. Remove very short words (< 2 characters)
        5. Remove stopwords
        6. Return remaining keywords
    
    Why this order?
        - Lowercase: "Bug" and "bug" should match
        - Remove punctuation: "hello!" and "hello" are same word
        - Split: Turn "hello world" into ["hello", "world"]
        - Remove short: "a", "I" don't add meaning
        - Remove stopwords: Focus on important words
    
    Example:
        >>> extract_keywords("What is the best way to fix a bug?")
        ["best", "way", "fix", "bug"]
        
        >>> extract_keywords("How do I reset my password?")
        ["reset", "password"]
    """
    
    # Convert to lowercase for case-insensitive matching
    text = text.lower()
    
    # Replace punctuation with spaces (keep text as words)
    # This converts "hello!" and "hello?" both to "hello"
    punctuation = ".,!?;:'\"-()[]{}/"
    for p in punctuation:
        text = text.replace(p, " ")
    
    # Split text into words
    words = text.split()
    
    # Get stopwords
    stopwords = get_stopwords()

    # Normalization mapping - canonicalize related terms
    NORMALIZATION = {
        "fix": "repair",
        "repair": "repair",
        "issue": "problem",
        "problem": "problem",
    }

    # Synonym expansion mapping: expand keywords to related words
    SYNONYMS = {
        "help": ["assist", "support"],
        "password": ["passcode", "credentials"],
        "login": ["signin", "log-in"],
        "error": ["issue", "problem"],
        "payment": ["billing", "charge"],
    }

    keywords: List[str] = []
    for word in words:
        if word in stopwords or len(word) < 2:
            continue

        # Apply normalization
        norm = NORMALIZATION.get(word, word)

        # Add normalized word
        keywords.append(norm)

        # Expand synonyms if available
        if norm in SYNONYMS:
            for s in SYNONYMS[norm]:
                keywords.append(s)

    return keywords


# ============================================================================
# STEP 3: DOCUMENT RETRIEVAL AND SCORING
# ============================================================================

def calculate_relevance_score(issue: str, document: str) -> float:
    """
    Calculate a relevance score between an issue and a document.
    
    Args:
        issue (str): Customer's support issue/question
        document (str): Content of a knowledge base document
    
    Returns:
        float: Relevance score (higher = more relevant)
               Typical range: 0 to 20+
    
    Scoring Logic:
        
        Step 1: Extract keywords from both texts
            Issue keywords: Extract meaningful words from customer's question
            Doc keywords: Extract meaningful words from document
        
        Step 2: Count keyword overlap
            For each issue keyword, check if it appears in document
            Example:
                Issue: "How do I reset my password?"
                Keywords: ["reset", "password"]
                Doc: "Password reset instructions..."
                Doc keywords: ["password", "reset", "instructions"]
                Overlap: ["reset", "password"] = 2 keywords match
                Score += 2
        
        Step 3: Add coverage bonus
            If the document has good keyword coverage:
                Coverage = (keywords_matched / total_issue_keywords) * 100
                If coverage >= 50%, add 1 bonus point
                Why? Documents covering most of the issue are better.
        
        Total Score = Keyword Matches + Coverage Bonus
    
    Why this scoring?
        ✓ Simple and deterministic (same input = same output)
        ✓ Favors documents with relevant keywords
        ✓ Penalizes documents with only 1-2 matches
        ✓ Can't be gamed or manipulated
    
    Limitations:
        ✗ No semantic understanding
          Example: "fix" and "repair" are synonyms but scored separately
        ✗ Doesn't understand word importance
          Example: "the" and "password" get same weight if not stopworded
        ✗ Can't handle typos
          Example: "pasword" won't match "password"
        ✗ Doesn't consider position
          Example: "password" mentioned once = same as mentioned 10 times
    
    Example:
        >>> score = calculate_relevance_score(
        ...     "How do I reset password?",
        ...     "Password reset: Click forgot password button..."
        ... )
        >>> score
        3.5  # 2 keywords matched + 1.5 coverage bonus
    """
    
    # Extract keywords from issue (expanded and normalized)
    issue_keywords = extract_keywords(issue)
    if not issue_keywords:
        return 0.0

    doc_lower = document.lower()

    # Frequency-based scoring: count occurrences of each issue word in document
    score = 0.0
    matched_keywords = 0
    for word in issue_keywords:
        count = doc_lower.count(word)
        if count > 0:
            score += count
            matched_keywords += 1
        else:
            # Simple fuzzy matching: prefix + length check
            pref = word[:4]
            for token in set(doc_lower.split()):
                if token.startswith(pref) and abs(len(token) - len(word)) <= 2:
                    score += 1.0
                    matched_keywords += 1
                    break

    # Add small coverage bonus when many issue keywords are matched
    if matched_keywords > 0:
        coverage = matched_keywords / len(issue_keywords)
        if coverage >= 0.5:
            score += coverage  # fractional bonus

    return float(score)


def retrieve_document(
    issue: str,
    docs: List[str],
    threshold: float = 2.0
) -> Optional[str]:
    """
    Find and return the most relevant document for an issue.
    
    Args:
        issue (str): Customer's support issue/question
        docs (List[str]): List of documents to search through
        threshold (float): Minimum score to consider a document relevant
                          Default: 2.0
    
    Returns:
        str: Best matching document, or None if no good match found
    
    What it does:
        1. Calculate relevance score for each document
        2. Find the document with highest score
        3. Check if best score meets threshold
        4. Return document if good enough, else None
    
    Why threshold matters:
        PROBLEM: Without threshold, we always return something, even bad matches
        Example without threshold:
            Query: "xyz abc 123"
            Doc 1: No matches (score: 0)
            Doc 2: 1 match (score: 1)
            Result: Return Doc 2 (bad!)
        
        SOLUTION: Set threshold = 2.0
        Example with threshold = 2.0:
            Query: "xyz abc 123"
            Doc 1: No matches (score: 0) < threshold
            Doc 2: 1 match (score: 1) < threshold
            Result: Return None (good!)
        
        Threshold values:
            - threshold = 1.0: Very lenient, almost always returns a match
            - threshold = 2.0: Moderate
            - threshold = 3.0: Strict, only returns high-confidence matches
            - threshold = 5.0: Very strict, only perfect matches
    
    Why returning None is better than a bad match:
        ✓ If no good document, it's better to tell user "Not found"
        ✓ Fallback to human expert
        ✓ Prevents giving wrong information
        ✓ Maintains trust
    
    Safety Handling:
        - If docs list is empty → return None
        - If issue is empty → return None
        - If all scores < threshold → return None
    
    Example Usage:
        >>> docs = load_corpus("data/kb/")
        >>> best_doc = retrieve_document("How reset password?", docs)
        >>> if best_doc:
        ...     print("Found documentation!")
        ...     print(best_doc)
        ... else:
        ...     print("No relevant documentation found")
    """
    
    # Safety check: empty inputs
    if not docs or not issue or not issue.strip():
        return None

    scores: List[float] = []
    for doc in docs:
        scores.append(calculate_relevance_score(issue, doc))

    # Select best document
    best_score = max(scores)
    # Higher threshold avoids weak matches and reduces false positives.
    # This prefers precision over recall: we only return a document when
    # the relevance score is confidently high, reducing incorrect replies.
    if best_score < threshold:
        return None

    best_idx = scores.index(best_score)
    return docs[best_idx]
# Synonym mapping (manual but powerful)
SYNONYMS = {
    "help": ["assist", "support"],
    "password": ["passcode", "credentials"],
    "login": ["signin", "log-in"],
    "error": ["issue", "problem", "failure"],
    "payment": ["charge", "billing", "transaction"],
}
def expand_words(words):
    expanded = set(words)

    for word in words:
        if word in SYNONYMS:
            expanded.update(SYNONYMS[word])

    return list(expanded)
