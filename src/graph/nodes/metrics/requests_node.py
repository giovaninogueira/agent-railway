from src.services.railway_service import RailwayService


def requests_node(state):
    svc = RailwayService(
        project_id=state["project"],
        service_id=state["service"],
        environment_id=state["environment_id"],
    )
    data = svc.fetch_requests()
    
    return {"requests_data": data}
