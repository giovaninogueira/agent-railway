from src.services.railway_service import RailwayService


def cpu_node(state):
    svc = RailwayService(
        project_id=state["project"],
        service_id=state["service"],
        environment_id=state["environment_id"],
    )
    data = svc.fetch_cpu()
    print(f">>> cpu_node: {len(data)} pontos")
    return {"cpu_data": data}
