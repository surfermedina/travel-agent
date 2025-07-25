# utils/preprocess_input.py
# Cleans user input before matching.
# - Strips greetings
# - Detects standalone greetings
# - Flags sensitive keyword combinations (e.g. 'atm machine')

import re

# Greeting patterns to strip from beginning of input
GREETING_PATTERNS = [
    r'^(hi|hello|hey|howdy|hiya|greetings|good (morning|afternoon|evening))\b[\s,!.]*',
]

# Individual words that may indicate sensitive match triggers
SENSITIVE_WORDS = {"machine", "machines", "atm", "coin", "counting"}

# Phrases we want to match exactly for suppression
SENSITIVE_PHRASES = {
    "atm machine",
    "coin machine",
    "cash counting machine",
    "machines that count cash"
}

def strip_greetings(text: str) -> str:
    for pattern in GREETING_PATTERNS:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    return text.strip()

def is_standalone_greeting(text: str) -> bool:
    text = text.strip().lower()
    return text in {
        "hi", "hello", "hey", "howdy", "hiya", "greetings",
        "good morning", "good afternoon", "good evening"
    }

def has_sensitive_keywords(text: str) -> bool:
    lc = text.lower()
    # Match full sensitive phrases
    for phrase in SENSITIVE_PHRASES:
        if phrase in lc:
            return True

    # Match individual sensitive words in tokenized input
    tokens = set(re.findall(r'\b\w+\b', lc))
    if tokens.intersection(SENSITIVE_WORDS):
        return True

    return False

def preprocess_input(text: str) -> dict:
    cleaned = strip_greetings(text)
    return {
        "original": text,
        "cleaned": cleaned,
        "tokens": cleaned.lower().split(),
        "is_greeting_only": is_standalone_greeting(text),
        "contains_sensitive_terms": has_sensitive_keywords(cleaned),
    }
