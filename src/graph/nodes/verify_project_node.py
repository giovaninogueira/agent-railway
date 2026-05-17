import os
import requests
from src.services.railway_service import fetch_environments

RAILWAY_API_URL = "https://backboard.railway.com/graphql/v2"

LIST_PROJECTS_QUERY = """
query {
  projects {
    edges {
      node {
        id
        name
      }
    }
  }
}
"""

LIST_SERVICES_QUERY = """
query($projectId: String!) {
  project(id: $projectId) {
    services {
      edges {
        node {
          id
          name
        }
      }
    }
  }
}
"""


def _query(query: str, variables: dict = None) -> dict:
    token = os.getenv("RAILWAY_API_TOKEN")
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    response = requests.post(
        RAILWAY_API_URL,
        json=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    response.raise_for_status()
    data = response.json()
    if data.get("errors"):
        raise RuntimeError(f"Railway API error: {data['errors']}")
    return data


def _fetch_services(project_id: str) -> list:
    data = _query(LIST_SERVICES_QUERY, {"projectId": project_id})
    edges = (data.get("data") or {}).get("project", {}).get("services", {}).get("edges", [])
    return [edge["node"] for edge in edges]


def verify_project_node(state):
    project_name = state.get("project")

    data = _query(LIST_PROJECTS_QUERY)
    projects = [
        edge["node"]
        for edge in (data.get("data") or {}).get("projects", {}).get("edges", [])
    ]

    if project_name:
        matched_project = next(
            (p for p in projects if p["name"].lower() == project_name.lower()),
            None,
        )
        if matched_project:
            project_id = matched_project["id"]
            environments = fetch_environments(project_id)
            environment_id = environments[0]["id"] if environments else None
            return {
                **state,
                "project": project_id,
                "environment_id": environment_id,
                "services": _fetch_services(project_id),
                "service": None,
            }

        # No project match, check service names
        all_services = []
        project_by_service = {}
        for project in projects:
            for svc in _fetch_services(project["id"]):
                all_services.append(svc)
                project_by_service[svc["id"]] = project["id"]

        matched_service = next(
            (s for s in all_services if s["name"].lower() == project_name.lower()),
            None,
        )
        if matched_service:
            project_id = project_by_service[matched_service["id"]]
            environments = fetch_environments(project_id)
            environment_id = environments[0]["id"] if environments else None
            return {
                **state,
                "project": project_id,
                "environment_id": environment_id,
                "services": all_services,
                "service": matched_service["id"],
            }

    all_services = []
    for project in projects:
        environments = fetch_environments(project["id"])
        env_id = environments[0]["id"] if environments else None
        for svc in _fetch_services(project["id"]):
            all_services.append({
                **svc,
                "project_id": project["id"],
                "environment_id": env_id,
            })

    return {
        **state,
        "project": None,
        "environment_id": None,
        "services": all_services,
        "service": None,
    }
