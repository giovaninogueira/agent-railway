from langgraph.graph import StateGraph, START, END
from src.state import AgentState

from src.graph.nodes import (
    intention_node,
    verify_project_node,
    intent_classification_node,
    analysis_final_node,
)
from src.graph.nodes.routes import (
    out_of_scope_route,
    verify_project_route,
    router_metrics,
)
from src.graph.nodes.metrics import (
    logs_node,
    cpu_node,
    memory_node,
    requests_node,
    status_node,
    logs_analysis_node,
    memory_analysis_node,
    cpu_analysis_node,
    requests_analysis_node,
    status_analysis_node,
)


def route_intention(state):
    if state.get("is_out_of_scope"):
        return "out_of_scope"
    return "intent_classification"


def route_classification(state):
    if state.get("is_vague"):
        return "intention"
    return "verify_project"


builder = StateGraph(AgentState)
builder.add_node("intention", intention_node)
builder.add_node("intent_classification", intent_classification_node)
builder.add_node("verify_project", verify_project_node)
builder.add_node("out_of_scope", out_of_scope_route)
builder.add_node("verify_project_route", verify_project_route)
builder.add_node("cpu_metrics", cpu_node)
builder.add_node("memory_metrics", memory_node)
builder.add_node("logs_metrics", logs_node)
builder.add_node("requests_metrics", requests_node)
builder.add_node("status_metrics", status_node)
builder.add_node("logs_analysis", logs_analysis_node)
builder.add_node("memory_analysis", memory_analysis_node)
builder.add_node("cpu_analysis", cpu_analysis_node)
builder.add_node("requests_analysis", requests_analysis_node)
builder.add_node("status_analysis", status_analysis_node)
builder.add_node("final_analysis", analysis_final_node)

builder.add_edge(START, "intention")
builder.add_conditional_edges(
    "intention",
    route_intention,
    {
        "out_of_scope": "out_of_scope",
        "intent_classification": "intent_classification",
    },
)
builder.add_conditional_edges(
    "intent_classification",
    route_classification,
    {
        "intention": "intention",
        "verify_project": "verify_project",
    },
)
builder.add_edge("verify_project", "verify_project_route")
builder.add_conditional_edges("verify_project_route", router_metrics)
builder.add_edge("logs_metrics", "logs_analysis")
builder.add_edge("memory_metrics", "memory_analysis")
builder.add_edge("cpu_metrics", "cpu_analysis")
builder.add_edge("requests_metrics", "requests_analysis")
builder.add_edge("status_metrics", "status_analysis")

# Todos os analysis nodes convergem para o final
builder.add_edge("cpu_analysis", "final_analysis")
builder.add_edge("memory_analysis", "final_analysis")
builder.add_edge("logs_analysis", "final_analysis")
builder.add_edge("requests_analysis", "final_analysis")
builder.add_edge("status_analysis", "final_analysis")

builder.add_edge("final_analysis", END)
builder.add_edge("out_of_scope", END)

graph = builder.compile()
