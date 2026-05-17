from typing import TypedDict

class AgentState(TypedDict):
    """State of an agent in the environment."""
    user_input: str
    answer: str
    mode: str
    messages: list
    reason: str
    intention: str
    project: str | None
    environment_id: str | None
    metrics: list
    logs_data: list
    logs_analysis: dict
    memory_analysis: dict
    cpu_analysis: dict
    requests_analysis: dict
    status_analysis: dict
    cpu_data: list
    memory_data: list
    requests_data: dict
    status_data: dict
    services: list
    service: str | None
    is_out_of_scope: bool
    is_vague: bool
    sufficient_context: bool
    clarification_needed: str | None
    log_level: str | None
    