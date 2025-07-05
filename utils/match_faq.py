"""
match_faq.py

Helper function for matching user questions to predefined FAQ entries
using fuzzy string matching.

This utility module compares a user's input against a list of FAQs and returns
the best-matched answer if the similarity score meets a given threshold.

Uses rapidfuzz for efficient and accurate string comparison.

Example FAQ entry format:
- {"q": "What are your hours?", "a": "We’re open Monday through Friday, 9am to 5pm."}

Usage:
    best_answer = find_best_match("What time do you open?", faq_list)
"""

from rapidfuzz import fuzz

def find_best_match(question: str, faq_list: list[dict], threshold: int = 80) -> str | None:
    """
    Finds the best-matching FAQ answer for a given question.

    Args:
        question (str): The user's input question.
        faq_list (list[dict]): A list of FAQ entries with keys 'q' (question) and 'a' (answer).
        threshold (int): Minimum similarity score (0-100) required to accept a match.

    Returns:
        str | None: The best-matching answer, or None if no match exceeds the threshold.
    """
    best = {"score": 0, "answer": None}

    for entry in faq_list:
        # Compare user input to the FAQ question using partial match
        score = fuzz.partial_ratio(question.lower(), entry["q"].lower())
        
        if score > best["score"] and score >= threshold:
            best["score"] = score
            best["answer"] = entry["a"]

    return best["answer"]