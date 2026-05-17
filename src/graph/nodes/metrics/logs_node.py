from src.services.railway_service import RailwayService


def logs_node(state):
    print(f">>> logs_node state: project={state.get('project')} service={state.get('service')} environment_id={state.get('environment_id')}")
    svc = RailwayService(
        project_id=state["project"],
        service_id=state["service"],
        environment_id=state["environment_id"],
    )
    logs = svc.fetch_logs()
    print(f">>> logs_node: {len(logs)} logs")
    return {"logs_data": logs}
