from src.services.railway_service import RailwayService


def status_node(state):
    svc = RailwayService(
        project_id=state["project"],
        service_id=state["service"],
        environment_id=state["environment_id"],
    )
    cpu = svc.fetch_cpu(minutes_ago=5)
    logs = svc.fetch_logs()
    errors = [l for l in logs if (l.get("severity") or "").lower() == "error"]
    status = {
        "alive": len(cpu) > 0,
        "recent_errors": len(errors),
    }
    print(f">>> status_node: alive={status['alive']} errors={status['recent_errors']}")
    return {"status_data": status}
