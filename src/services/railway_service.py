import os
import requests
from datetime import datetime, timedelta, timezone

RAILWAY_API_URL = "https://backboard.railway.com/graphql/v2"

METRICS_QUERY = """
query metrics(
  $projectId: String!,
  $serviceId: String!,
  $environmentId: String!,
  $startDate: DateTime!,
  $endDate: DateTime!,
  $measurements: [MetricMeasurement!]!
) {
  metrics(
    projectId: $projectId
    serviceId: $serviceId
    environmentId: $environmentId
    startDate: $startDate
    endDate: $endDate
    measurements: $measurements
  ) {
    measurement
    values {
      ts
      value
    }
  }
}
"""

LOGS_QUERY = """
query environmentLogs($environmentId: String!) {
  environmentLogs(environmentId: $environmentId) {
    timestamp
    message
    severity
  }
}
"""

LOGS_QUERY_WITH_FILTER = """
query environmentLogs($environmentId: String!, $filter: String!) {
  environmentLogs(environmentId: $environmentId, filter: $filter) {
    timestamp
    message
    severity
  }
}
"""

LIST_ENVIRONMENTS_QUERY = """
query project($id: String!) {
  project(id: $id) {
    environments {
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


class RailwayService:
    def __init__(self, project_id: str, service_id: str, environment_id: str):
        if not project_id or not environment_id:
            raise ValueError(f"project_id e environment_id são obrigatórios (project={project_id}, environment={environment_id})")
        self.project_id = project_id
        self.service_id = service_id
        self.environment_id = environment_id
        self._token = os.getenv("RAILWAY_API_TOKEN")

    def _query(self, query: str, variables: dict = None) -> dict:
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        response = requests.post(
            RAILWAY_API_URL,
            json=payload,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json",
            },
        )
        if not response.ok:
            raise RuntimeError(f"Railway API HTTP {response.status_code}: {response.text}")
        data = response.json()
        if data.get("errors"):
            raise RuntimeError(f"Railway API error: {data['errors']}")
        return data

    def _fetch_metrics(self, measurements: list, minutes_ago: int = 30) -> dict:
        now = datetime.now(timezone.utc)
        start = now - timedelta(minutes=minutes_ago)
        data = self._query(METRICS_QUERY, {
            "projectId": self.project_id,
            "serviceId": self.service_id,
            "environmentId": self.environment_id,
            "startDate": start.isoformat(),
            "endDate": now.isoformat(),
            "measurements": measurements,
        })
        results = (data.get("data") or {}).get("metrics", [])
        return {item["measurement"]: item["values"] for item in results}

    def fetch_cpu(self, minutes_ago: int = 30) -> list:
        result = self._fetch_metrics(["CPU_USAGE"], minutes_ago)
        return result.get("CPU_USAGE", [])

    def fetch_memory(self, minutes_ago: int = 30) -> list:
        result = self._fetch_metrics(["MEMORY_USAGE_GB"], minutes_ago)
        return result.get("MEMORY_USAGE_GB", [])

    def fetch_requests(self, minutes_ago: int = 30) -> dict:
        result = self._fetch_metrics(["NETWORK_TX_GB", "NETWORK_RX_GB"], minutes_ago)
        return {
            "tx": result.get("NETWORK_TX_GB", []),
            "rx": result.get("NETWORK_RX_GB", []),
        }

    def fetch_logs(self, filter: str = None, severity: str = None) -> list:
        if filter:
            query = LOGS_QUERY_WITH_FILTER
            variables = {"environmentId": self.environment_id, "filter": filter}
        else:
            query = LOGS_QUERY
            variables = {"environmentId": self.environment_id}
        data = self._query(query, variables)
        logs = (data.get("data") or {}).get("environmentLogs", [])
        if severity:
            logs = [l for l in logs if (l.get("severity") or "").lower() == severity.lower()]
        return logs


def fetch_environments(project_id: str) -> list:
    token = os.getenv("RAILWAY_API_TOKEN")
    payload = {"query": LIST_ENVIRONMENTS_QUERY, "variables": {"id": project_id}}
    response = requests.post(
        RAILWAY_API_URL,
        json=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    response.raise_for_status()
    data = response.json()
    edges = (data.get("data") or {}).get("project", {}).get("environments", {}).get("edges", [])
    return [edge["node"] for edge in edges]
