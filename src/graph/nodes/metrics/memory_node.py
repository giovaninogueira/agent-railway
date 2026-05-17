from src.services.railway_service import RailwayService


def memory_node(state):
    svc = RailwayService(
        project_id=state["project"],
        service_id=state["service"],
        environment_id=state["environment_id"],
    )
    data = svc.fetch_memory()
    print(f">>> memory_node: {len(data)} pontos")
    return {"memory_data": data}
