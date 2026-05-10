ITINERARY_FLOW = {
    "name": "itinerary",

    "default_state": {
        "destination": "Lisbon"
    },

    "triggers": [
        "plan my lisbon trip",
        "lisbon vacation",
        "lisbon getaway",
        "vacation itinerary",
        "short getaway",
        "3-day lisbon trip",
        "visiting lisbon",
        "weekend in lisbon",
        "leisure trip to lisbon",
        "food trip to lisbon"
    ],

    "fallback_message": "Sorry, I lost track of your itinerary planning session. Let's start again.",

    "steps": {

        1: {
            "type": "collect",
            "field": "days",
            "prompt": "How many days will you be in Lisbon?"
        },

        2: {
            "type": "collect",
            "field": "trip_type",
            "prompt": "What type of trip are you planning (e.g., short getaway, business trip, sightseeing, food-focused)?"
        },

        3: {
            "type": "collect",
            "field": "budget",
            "prompt": "What's your approximate budget level (budget, mid-range, or luxury)?"
        },

        4: {
            "type": "collect",
            "field": "interests",
            "prompt": "Are there any specific interests or must-see places you have in mind?"
        },

        5: {
            "type": "email_capture",
            "prompt": "If you'd like this itinerary emailed to you, enter your email address now. Otherwise type 'skip'."
        }
    },

    "completion": {

        "type": "gpt_generation",

        "response_source": "gpt-itinerary",

        "email_enabled": True,

        "email_handler": "send_itinerary_email",

        "system_prompt": """
    You are a Lisbon travel expert.

    The user has already completed the itinerary intake process.

    Do not ask follow-up questions.

    Generate the itinerary immediately using the provided traveler details.
    """,

        "prompt_template": """
    Create a Lisbon travel itinerary using the following traveler information.

    Destination: Lisbon
    Trip Length: {days}
    Trip Type: {trip_type}
    Budget: {budget}
    Interests: {interests}

    Requirements:
    - Create a day-by-day itinerary
    - Include neighborhoods and attractions
    - Include restaurant and food suggestions
    - Include family-friendly recommendations where appropriate
    - Keep the pacing realistic
    - Use a warm, concise travel-assistant tone
    """
    }
}