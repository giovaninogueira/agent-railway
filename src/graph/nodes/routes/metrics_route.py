from langgraph.types import Send
from src.state import AgentState

def router_metrics(state: AgentState) -> Send:
    metrics = state.get("metrics", [])
    
    return [
        Send(f"{metric}_metrics", {"metric_name": metric, **state})
        for metric in metrics
    ]