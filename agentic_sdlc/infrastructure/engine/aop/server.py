"""
Agent Orchestration Protocol (AOP) - Server.

Provides a REST-like interface for agent discovery and task execution.
Uses standard http.server for zero-dependency portability.
"""

import json
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, List, Any
from .models import AgentRegistration, AgentTask, AgentResponse, AgentStatus, to_dict

# In-memory registry for demo purposes
REGISTRY: Dict[str, AgentRegistration] = {}
TASKS: Dict[str, AgentTask] = {}
RESULTS: Dict[str, AgentResponse] = {}


class AOPRequestHandler(BaseHTTPRequestHandler):
    """Handler for AOP requests."""

    def _send_json(self, data: Any, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_GET(self):
        """Handle discovery and status checks."""
        if self.path == "/agents":
            # List all registered agents
            agents = [to_dict(a) for a in REGISTRY.values()]
            self._send_json({"agents": agents})
            
        elif self.path.startswith("/results/"):
            task_id = self.path.split("/")[-1]
            if task_id in RESULTS:
                self._send_json(to_dict(RESULTS[task_id]))
            else:
                self._send_json({"error": "Task not found"}, 404)
        
        else:
            self._send_json({"status": "AOP Server Online", "version": "1.0.0"})

    def do_POST(self):
        """Handle agent registration and task submission."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        data = json.loads(body)

        if self.path == "/register":
            agent = AgentRegistration(
                id=data.get("id", str(uuid.uuid4())),
                role=data.get("role", "generic"),
                capabilities=data.get("capabilities", []),
                endpoint=data.get("endpoint", "")
            )
            REGISTRY[agent.id] = agent
            self._send_json({"status": "Registered", "agent_id": agent.id})

        elif self.path == "/execute":
            # Submit a task
            task = AgentTask(
                id=str(uuid.uuid4()),
                objective=data.get("objective", ""),
                priority=data.get("priority", "medium"),
                context=data.get("context", {})
            )
            TASKS[task.id] = task
            # In a real system, we would route this to an agent
            self._send_json({"status": "Task Submitted", "task_id": task.id})

        else:
            self._send_json({"error": "Not Found"}, 404)


def run_server(port: int = 8000):
    server_address = ("", port)
    httpd = HTTPServer(server_address, AOPRequestHandler)
    print(f"🚀 AOP Server starting on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping AOP Server...")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
