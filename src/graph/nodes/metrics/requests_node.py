from src.services.railway_service import RailwayService


def requests_node(state):
    svc = RailwayService(
        project_id=state["project"],
        service_id=state["service"],
        environment_id=state["environment_id"],
    )
    data = svc.fetch_requests()
    print(f">>> requests_node: {len(data['tx'])} pontos tx, {len(data['rx'])} pontos rx")
    return {"requests_data": data}
