"""
sanitize.py

Provides basic input sanitization to strip whitespace and remove dangerous characters
before using user input in LLM prompts or logs.
"""

import re

def sanitize_input(text: str) -> str:
    """
    Sanitize user input by:
    - Stripping leading/trailing whitespace
    - Removing potentially harmful characters
    - Replacing multiple spaces with a single space
    """
    text = text.strip()
    
    # Remove characters that can be problematic in logs or web (basic XSS safety)
    text = re.sub(r'[<>`$;]', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text
