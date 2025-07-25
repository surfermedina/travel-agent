import re

def filter_pdf_text(text: str) -> str:
    """
    Cleans and filters raw PDF text for embedding.
    Tailored for Regent Bank documents.

    Removes headers, footers, navigation elements, junk characters,
    and normalizes content structure.
    """

    # Patterns to remove – both generic and Regent-specific
    patterns_to_remove = [
        # Generic headers/footers
        r"Regent Bank\s*\|.*",                     # Header with site structure
        r"Page \d+ of \d+",                        # Page numbering
        r"\b(Privacy Policy|Sitemap|Login|Devotions|Newsletter)\b",
        r"https?://[^\s]+",                        # URLs
        r"button\d+_?\(?\d*\)?",                   # Button tags like button1_(1)

        # Known recurring footer junk (from your examples)
        r"Join Our\s+We’ll send you.*?Subscribe",  # Newsletter footer block
        r"CONNECT WITH US!.*?All Rights Reserved", # Footer contact block
        r"Routing Number:.*?All Rights Reserved",  # FDIC/Compliance block
        r"Customer Service.*?Regent Elevate",      # Menu strip
        r"© \d{4} Regent Bank.*?All Rights Reserved",  # Copyright
        r"Daily\s+Online\s+Community Reinvestment.*?(Disclosures and Agreements)?",  # Legal footer

        # Empty/boilerplate phrases (optional cleanup)
        r"^\s*(Contact Us|Search|Locations|About Us|Resources|Leadership Team|Lending Team)\s*$",
    ]

    for pattern in patterns_to_remove:
        text = re.sub(pattern, "", text, flags=re.DOTALL | re.IGNORECASE)

    # Normalize bullet points and dashes
    text = re.sub(r"[\u2022•\*\-]\s+", "\n- ", text)  # Bullet normalization

    # Remove excessive line breaks and whitespace
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r" {2,}", " ", text)

    return text.strip()


# Optional test block
if __name__ == "__main__":
    sample = """
    CONNECT WITH US!
    Equal Housing Lender
    FDIC-Insured 
    - Backed by the full faith and credit of the U.S. Government
    Routing Number: 103101356
    Regent Bank NMLS#: 464417
    © 2025 Regent Bank. All Rights Reserved
    Daily 
    Online 
    Community Reinvestment
    Disclosures and Agreements

    Page 1 of 3

    • Business Checking
    • Business Loans

    Customer Service
    About Us
    Resources
    Leadership Team
    Regent Elevate
    """
    print(filter_pdf_text(sample))
