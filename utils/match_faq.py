from rapidfuzz import fuzz
from typing import List, Optional, Dict

STOCK_PROMPT_FOR_CLARITY = (
    "Thanks! Could you tell me a little more about what you're looking for?"
)

# New in-memory session suppression tracker
session_flags = {}  # e.g., { "session_id": { "suppressed": True } }

def find_best_match(
    question: str,
    faq_list: List[Dict[str, str]],
    threshold: int = 88,
    suppress_short_matches: bool = False,
    session_id: Optional[str] = None
) -> Optional[str]:
    """
    Finds the best-matching FAQ answer for a given question, with short input and false-match protection.

    Args:
        question (str): The user's input question (should be preprocessed).
        faq_list (list[dict]): A list of FAQ entries with keys 'q' and 'a'.
        threshold (int): Minimum fuzzy match score required to accept a match.
        suppress_short_matches (bool): Avoid matching short FAQ entries when input contains risky terms.
        session_id (str | None): Session ID used for tracking repeated suppression.

    Returns:
        str | None: A matched answer, stock clarification prompt, or None.
    """
    question = question.strip().lower()

    # PREVENT matching on extremely short non-numeric input
    if len(question) <= 2 and not question.isnumeric():
        print(f"[DEBUG] Input '{question}' is too short and non-numeric — skipping FAQ match")
        return None

    # Raise threshold for very short queries
    if len(question.split()) <= 2:
        threshold = max(threshold, 90)

    best = {"score": 0, "answer": None, "question_length": None}

    for entry in faq_list:
        score = fuzz.partial_ratio(question, entry["q"].lower())
        if score > best["score"] and score >= threshold:
            best["score"] = score
            best["answer"] = entry["a"]
            best["question_length"] = len(entry["q"].split())

    print(f"[DEBUG] Fuzzy match: '{question}' → score: {best['score']} | matched: {best['answer'] is not None}")

    # --- Suppression logic with session awareness ---
    if best["score"] >= threshold and suppress_short_matches:
        if best["question_length"] is not None and best["question_length"] <= 2:
            if session_id:
                # Check if we've already suppressed this session
                suppressed_once = session_flags.get(session_id, {}).get("suppressed", False)

                if suppressed_once:
                    print("[DEBUG] Suppression already triggered for this session — skipping FAQ match")
                    return None  # Let GPT handle it
                else:
                    # Mark suppression for this session
                    session_flags.setdefault(session_id, {})["suppressed"] = True
                    print("[DEBUG] Suppressing short FAQ match due to sensitive input — returning stock prompt.")
                    return STOCK_PROMPT_FOR_CLARITY
            else:
                # No session tracking — still suppress once
                print("[DEBUG] Suppressing short FAQ match (no session tracking) — returning stock prompt.")
                return STOCK_PROMPT_FOR_CLARITY

    return best["answer"]
