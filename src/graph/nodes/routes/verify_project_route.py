from langgraph.types import interrupt
from src.state import AgentState


def verify_project_route(state: AgentState) -> AgentState:
    service_id = state.get("service")
    if not service_id:
        service_id = interrupt({
            "mensagem": "Por gentileza, selecione o serviço que deseja analisar.",
            "services": state.get("services", []),
        })

    services = state.get("services", [])
    selected = next((s for s in services if s["id"] == service_id), {})
    project_id = state.get("project") or selected.get("project_id")
    environment_id = state.get("environment_id") or selected.get("environment_id")

    return {
        **state,
        "service": service_id,
        "project": project_id,
        "environment_id": environment_id,
        "answer": f"Analisando o service {service_id}...",
        "messages": state.get("messages", []) + [f"Analisando o service {service_id}..."],
    }
