from src.services.railway_service import RailwayService


def logs_node(state):
    svc = RailwayService(
        project_id=state["project"],
        service_id=state["service"],
        environment_id=state["environment_id"],
    )
    logs = svc.fetch_logs(severity=state.get("log_level"))
    
    return {"logs_data": logs}
