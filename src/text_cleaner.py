"""
text_cleaner.py
---------------
Cleans and normalizes extracted resume text before processing.
Removes noise, fixes spacing, and prepares text for NLP analysis.
"""

import re
import string


def clean_text(text: str) -> str:
    """
    Full cleaning pipeline for resume text.
    Steps:
      1. Lowercase
      2. Remove emails and phone numbers (for privacy in model input)
      3. Remove URLs
      4. Remove special characters (keep letters, digits, basic punctuation)
      5. Normalize whitespace
    """
    if not text:
        return ""

    # Step 1: Lowercase
    text = text.lower()

    # Step 2: Remove email addresses
    text = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w{2,}\b', ' ', text)

    # Step 3: Remove phone numbers
    text = re.sub(r'[\+\(]?[1-9][0-9\s\-\(\)]{8,}[0-9]', ' ', text)

    # Step 4: Remove URLs
    text = re.sub(r'http[s]?://\S+|www\.\S+', ' ', text)

    # Step 5: Remove special characters, keep letters/digits/basic punctuation
    text = re.sub(r'[^\w\s\+\#\.\,\/\-]', ' ', text)

    # Step 6: Normalize whitespace (collapse multiple spaces/newlines)
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def extract_candidate_name(raw_text: str) -> str:
    """
    Heuristic: The candidate's name is usually the first non-empty line.
    Returns the guessed name or 'Unknown'.
    """
    lines = [l.strip() for l in raw_text.strip().split('\n') if l.strip()]
    if lines:
        # First line is typically the name — stop at any email/phone marker
        first_line = lines[0]
        if '@' not in first_line and len(first_line.split()) <= 4:
            return first_line.title()
    return "Unknown Candidate"


def extract_email(raw_text: str) -> str:
    """Extract email address from raw resume text."""
    match = re.search(r'\b[\w\.-]+@[\w\.-]+\.\w{2,}\b', raw_text)
    return match.group(0) if match else "N/A"


def extract_years_experience(raw_text: str) -> float:
    """
    Heuristic: Find the maximum number of years mentioned near 'experience'.
    Returns float of max years found (0.0 if none found).
    """
    # Look for patterns like "4 years", "3+ years", "2.5 years"
    patterns = [
        r'(\d+(?:\.\d+)?)\s*\+?\s*years?\s+(?:of\s+)?experience',
        r'experience[^.]*?(\d+(?:\.\d+)?)\s*\+?\s*years?',
        r'(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\b',
    ]
    max_years = 0.0
    text_lower = raw_text.lower()
    for pattern in patterns:
        for match in re.finditer(pattern, text_lower):
            try:
                val = float(match.group(1))
                if val < 40:  # sanity check
                    max_years = max(max_years, val)
            except Exception:
                pass
    return max_years
