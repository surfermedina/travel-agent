import os
import requests

from utils.logger import get_logger

logger = get_logger()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL")

# Sends itinerary email using Resend API

def send_itinerary_email(to_email: str, itinerary: str):
    """Send itinerary email using Resend API."""
    
    if not RESEND_API_KEY:
        logger.error("Missing RESEND_API_KEY")
        return False

    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "from": RESEND_FROM_EMAIL,
        "to": [to_email],
        "subject": "Your Lisbon Itinerary",
        "text": itinerary
    }

    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers=headers,
            json=payload,
            timeout=15
        )

        if response.status_code in [200, 201]:
            logger.info(f"Itinerary email sent to {to_email}")
            return True

        logger.error(
            f"Resend failed: {response.status_code} | {response.text}"
        )

        return False

    except Exception as e:
        logger.exception("Error sending itinerary email")
        return False