# --- Generic Multi-Step Flow Engine Utilities ---
# This module contains reusable helper functions for orchestrating
# multi-step conversational flows (trip planning, business travel,
# onboarding flows, etc.). The goal is to separate flow execution
# logic from API transport logic and individual flow definitions.

# Retrieves the prompt text for the current step in a given flow definition
def get_next_flow_prompt(flow, step):
    """
    Retrieve the prompt text for a given flow step.
    Args:
        flow (dict):
            Flow definition object loaded from the flow registry.
        step (int):
            Current step number in the flow.
    Returns:
        str | None:
            The prompt text for the requested step, or None if the step does not exist.
    """

    step_config = flow["steps"].get(step)

    if not step_config:
        return None

    return step_config.get("prompt")

# Advances the flow state to the next step by incrementing 
# the 'step' key in the state dictionary
def advance_flow_step(state):
    """
    Advance the current flow state to the next step.
    Args:
        state (dict):
            Mutable session state object for the active flow.
    Returns:
        int:
            The updated step number.
    """

    state["step"] += 1

    return state["step"]

# Checks to see if the current step is the final step in the flow definition
def is_flow_complete(flow, step):

    """
    Determine whether the current step is the final
    configured step in the flow.
    Args:
        flow (dict):
            Flow definition object.
        step (int):
            Current flow step.
    Returns:
        bool:
            True if the current step is beyond the
            configured flow steps.
    """

    max_step = max(flow["steps"].keys())

    return step > max_step

# Detects if the user input contains any trigger phrases defined in the flow registry
def detect_triggered_flow(user_input, flow_registry):

    """
    Detect whether the user input matches any registered
    multi-step flow trigger phrases.
    Args:
        user_input (str):
            Lowercased user input string.
        flow_registry (dict):
            Registry of all available flows.
    Returns:
        dict | None:
            Matching flow definition if found,
            otherwise None.
    """

    for flow in flow_registry.values():

        for trigger in flow.get("triggers", []):

            if trigger in user_input:
                return flow

    return None

# Retrieves the state field name associated with the current flow step, if defined
#   For example, in the itinerary flow, step 1 maps to "days", step 2 maps to "trip_type", etc.
def get_flow_field_name(flow, step):

    """
    Retrieve the state field name associated with
    the current flow step.
    Args:
        flow (dict):
            Flow definition object.
        step (int):
            Current flow step.
    Returns:
        str | None:
            State field name for this step,
            or None if not defined.
    """

    step_config = flow["steps"].get(step)

    if not step_config:
        return None

    return step_config.get("field")

# Retrieve the orchestration type for the current flow step using the flow-defined field mapping
def get_step_type(flow, step):

    """
    Retrieve the orchestration type for the current step.

    Args:
        flow (dict):
            Flow definition object.
        step (int):
            Current flow step.
    Returns:
        str | None:
            Step type identifier
            (e.g. collect, email_capture),
            or None if undefined.
    """

    step_config = flow["steps"].get(step)

    if not step_config:
        return None

    return step_config.get("type")

# Retrieve the chat completion configuration for a flow definition, if defined
def get_completion_config(flow):

    """
    Retrieve the completion configuration
    for a flow definition.
    Args:
        flow (dict):
            Flow definition object.
    Returns:
        dict:
            Completion configuration object.
    """

    return flow.get("completion", {})

# Get the response source type for a completed flow, 
# e.g. whether to use a custom GPT response template or a standard response generation approach
def get_completion_response_source(flow):

    """
    Retrieve the response source identifier
    for a flow completion.
    Args:
        flow (dict):
            Flow definition object.
    Returns:
        str:
            Response source identifier.
    """

    completion = get_completion_config(flow)

    return completion.get("response_source", "gpt")

# Check whether email delivery is enabled for a flow completion
def is_completion_email_enabled(flow):

    """
    Determine whether a flow completion
    supports optional email delivery.
    Args:
        flow (dict):
            Flow definition object.
    Returns:
        bool:
            True if email delivery is enabled.
    """

    completion = get_completion_config(flow)

    return completion.get("email_enabled", False)

# Get the configured email handler for a flow completion
def get_completion_email_handler(flow):

    """
    Get the configured email handler
    for a flow completion.
    Args:
        flow (dict):
            Flow definition object.
    Returns:
        str | None:
            Email handler name.
    """

    completion = get_completion_config(flow)

    return completion.get("email_handler")

# Get the completion execution type for a flow 
# (e.g. GPT generation, webhook, static response)
def get_completion_type(flow):

    """
    Retrieve the completion execution type
    for a flow.
    Args:
        flow (dict):
            Flow definition object.
    Returns:
        str:
            Completion execution type.
    """

    completion = get_completion_config(flow)

    return completion.get("type")

# Get the default session state values for a flow
def get_default_flow_state(flow):

    """
    Get the default session state values
    for a flow.
    Args:
        flow (dict):
            Flow definition object.
    Returns:
        dict:
            Default flow state values.
    """

    return flow.get("default_state", {})

# Create unified flow activation helper
def initialize_flow_state(flow):

    """
    Create the initial session state
    for a newly activated flow.
    Args:
        flow (dict):
            Flow definition object.
    Returns:
        dict:
            Initialized flow session state.
    """

    return {
        "flow": flow["name"],
        "step": 1,
        **get_default_flow_state(flow)
    }

# Get the first prompt shown when a flow starts
def get_initial_flow_prompt(flow):

    """
    Retrieve the starting prompt
    for a newly activated flow.
    Args:
        flow (dict):
            Flow definition object.
    Returns:
        str:
            Initial flow prompt.
    """

    return get_next_flow_prompt(flow, 1)

# Check whether the session is currently inside an active flow
def get_active_flow(session_id, session_state, flow_registry):

    """
    Retrieve the currently active flow
    for a session, if one exists.
    Args:
        session_id (str):
            Current session identifier.
        session_state (dict):
            Global session state store.
        flow_registry (dict):
            Registered flow catalog.
    Returns:
        dict | None:
            Active flow definition object,
            or None if no active flow exists.
    """

    if (
        session_id in session_state
        and session_state[session_id].get("flow")
    ):

        flow_name = session_state[session_id]["flow"]

        return flow_registry.get(flow_name)

    return None

# Standardize flow response objects with a consistent structure 
# for orchestration and response generation
def build_flow_response(source,answer,stream=False):

    """
    Build a standardized response object
    for flow orchestration.
    Args:
        source (str):
            Response source identifier.
        answer (str):
            Response text content.
    Returns:
        dict:
            Standardized flow response object.
    """

    return {
        "source": source,
        "answer": answer,
        "stream": stream
    }

# Get the fallback/reset message for a flow
def get_flow_fallback_message(flow):

    """
    Retrieve the fallback/reset message
    for a flow.
    Args:
        flow (dict):
            Flow definition object.
    Returns:
        str:
            Flow fallback message.
    """

    return flow.get(
        "fallback_message",
        "Sorry, something went wrong with this dialogue."
    )

# Render the completion prompt template using collected flow state values
def render_completion_prompt(flow, state):

    """
    Render the completion prompt template
    using collected flow state values.
    Args:
        flow (dict):
            Flow definition object.
        state (dict):
            Current collected session state.
    Returns:
        str:
            Rendered GPT completion prompt.
    """

    completion = get_completion_config(flow)

    template = completion.get("prompt_template", "")

    return template.format(**state)

# Store user input for the current flow step using the flow-defined field mapping
def collect_step_input(flow, state, step, user_input):

    """
    Store user input for the current flow step
    using the flow-defined field mapping.
    Args:
        flow (dict):
            Flow definition object.
        state (dict):
            Mutable session state.
        step (int):
            Current step number.
        user_input (str):
            User response text.
    """

    field_name = get_flow_field_name(flow, step)

    if field_name:
        state[field_name] = user_input

# Determine whether the current step is a normal input-collection step (not completion step).
def is_standard_flow_step(flow, step):

    """
    Determine whether the current step is a normal
    input-collection step (not completion).
    Args:
        flow (dict):
            Flow definition object.
        step (int):
            Current step number.
    Returns:
        bool:
            True if this is a configured flow step.
    """

    return step in flow.get("steps", {})
