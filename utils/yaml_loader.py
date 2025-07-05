"""
yaml_loader.py

Utility module for loading YAML-based FAQ files for different banking clients, depending on client id.

This module reads a client-specific FAQ YAML file located in the `prompts/` folder.
It returns a list of dictionaries containing question-answer pairs.

Example YAML format:
- q: "What are your hours?"
  a: "Our hours are Monday to Friday, 9am to 5pm."

Usage:
    faq = load_faq("demobank")
"""

import os
import yaml

def load_faq(client_id: str) -> list[dict]:
    """
    Loads the YAML FAQ file for a given client.

    Args:
        client_id (str): The identifier used to locate the client's YAML file 
                         (e.g., 'demobank', 'scissortail').

    Returns:
        list[dict]: A list of dictionaries with keys 'q' and 'a' for question and answer.

    Raises:
        FileNotFoundError: If the FAQ YAML file does not exist.
    """
    # Construct the path to the FAQ file based on client ID
    path = f"clients/{client_id}/documents/faq.yaml"

    if not os.path.exists(path):
        raise FileNotFoundError(f"No FAQ file found at {path}")
    
    with open(path, "r", encoding="utf-8") as file:
        faq_raw = yaml.safe_load(file)

    # Unwrap 'faqs' key if present
    faq_list = faq_raw.get("faqs", []) if isinstance(faq_raw, dict) else faq_raw

    # Normalize keys to 'q' and 'a'
    faq = [{"q": entry.get("question", ""), "a": entry.get("answer", "")} for entry in faq_list]
    return faq
