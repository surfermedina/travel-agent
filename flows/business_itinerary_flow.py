BUSINESS_ITINERARY_FLOW = {
    "name": "business_itinerary",

    "default_state": {
        "destination": "Lisbon"
    },

    "triggers": [
        "business itinerary",
        "business trip itinerary",
        "plan my business trip",
        "corporate trip",
        "work trip",
        "conference trip",
        "conference itinerary",
        "business travel",
        "lisbon business trip"
    ],

    "fallback_message": "Sorry, I lost track of your business itinerary planning session. Let's start again.",

    "steps": {

        1: {
            "type": "collect",
            "field": "days",
            "prompt": "How many days will you be in Lisbon for your business trip?"
        },

        2: {
            "type": "collect",
            "field": "meeting_area",
            "prompt": "What area of Lisbon will your meetings or business activities be centered around?"
        },

        3: {
            "type": "collect",
            "field": "work_schedule",
            "prompt": "Will your schedule be mostly full workdays, or will you have free time during the day?"
        },

        4: {
            "type": "collect",
            "field": "evening_preferences",
            "prompt": "What kinds of dinners, nightlife, or evening activities are you interested in after work?"
        },

        5: {
            "type": "email_capture",
            "prompt": "If you'd like this business itinerary emailed to you, enter your email address now. Otherwise type 'skip'."
        }
    },

    "completion": {

        "type": "gpt_generation",

        "response_source": "gpt-business-itinerary",

        "email_enabled": True,

        "email_handler": "send_itinerary_email",

        "system_prompt": """
    You are a Lisbon business travel expert.

    The user has already completed the business itinerary intake process.

    Do not ask follow-up questions.

    Generate the itinerary immediately using the provided traveler details.

    Focus on:
    - efficient logistics
    - realistic pacing
    - minimizing unnecessary travel time
    - centrally located recommendations
    - practical dining and transportation suggestions
    - balancing work obligations with enjoyable downtime
    """,

        "prompt_template": """
    Create a Lisbon business travel itinerary using the following traveler information.

    Destination: Lisbon
    Trip Length: {days}
    Meeting Area: {meeting_area}
    Work Schedule: {work_schedule}
    Evening Preferences: {evening_preferences}

    Requirements:
    - Create a realistic day-by-day itinerary
    - Prioritize efficient transportation and logistics
    - Recommend business-friendly neighborhoods and restaurants
    - Include coffee shops or casual meeting-friendly locations where appropriate
    - Include practical dinner and evening suggestions
    - Keep the pacing realistic for a working traveler
    - Use a concise, polished, professional travel-assistant tone
    """
    }
}