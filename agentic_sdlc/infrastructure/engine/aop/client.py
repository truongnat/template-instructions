"""
Agent Orchestration Protocol (AOP) - Client.

Client-side library for interacting with the AOP server.
Enables agents to register themselves and the Brain to dispatch tasks.
"""

import json
import urllib.request
from typing import Any, Dict, List, Optional


class AOPClient:
    """Client for AOP server interaction."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def _request(self, path: str, method: str = "GET", data: Optional[Dict] = None) -> Dict:
        url = f"{self.base_url}{path}"
        headers = {"Content-Type": "application/json"}
        
        req_data = json.dumps(data).encode("utf-8") if data else None
        req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            try:
                # Try to read the error body
                return json.loads(e.read().decode("utf-8"))
            except:
                return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    def register_agent(self, role: str, capabilities: List[str], endpoint: str) -> Dict:
        """Register an agent with the server."""
        return self._request("/register", "POST", {
            "role": role,
            "capabilities": capabilities,
            "endpoint": endpoint
        })

    def list_agents(self) -> List[Dict]:
        """List all available agents."""
        res = self._request("/agents")
        return res.get("agents", [])

    def execute_task(self, objective: str, context: Optional[Dict] = None) -> Dict:
        """Dispatch a task to the swarm."""
        return self._request("/execute", "POST", {
            "objective": objective,
            "context": context or {}
        })

    def get_result(self, task_id: str) -> Dict:
        """Poll for a task result."""
        return self._request(f"/results/{task_id}")


if __name__ == "__main__":
    # Example usage
    client = AOPClient()
    print("Listing agents...")
    print(client.list_agents())
    
    print("\nRegistering mock agent...")
    res = client.register_agent("SA", ["architecture", "design"], "http://agent-sa:8080")
    print(res)
    
    print("\nExecuting test task...")
    task_res = client.execute_task("Design a new microservice for payments")
    print(task_res)
