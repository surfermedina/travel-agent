# Centralized flow catalog to manage all multi-step interactions in one place

from flows.itinerary_flow import ITINERARY_FLOW
from flows.business_itinerary_flow import BUSINESS_ITINERARY_FLOW

FLOW_REGISTRY = {
    "itinerary": ITINERARY_FLOW,
    "business_itinerary": BUSINESS_ITINERARY_FLOW
}