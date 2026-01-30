"""
Sandbox Executor - Safe code execution in isolated environments.

Part of Layer 3: Infrastructure Layer.
Supports Docker for local isolation and E2B for cloud sandboxing.
"""

import json
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# Try to import docker, provide fallback
try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False


@dataclass
class ExecutionResult:
    """Result of a sandboxed code execution."""
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float
    timed_out: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration_ms": self.duration_ms,
            "timed_out": self.timed_out,
            "metadata": self.metadata
        }


class SandboxExecutor:
    """
    Executes agent-generated code in isolated environments.
    
    Features:
    - Docker isolation (local)
    - Resource limits (CPU, Memory)
    - Network isolation
    - Timeout management
    - Support for Python, JS, and Shell
    """
    
    DEFAULT_TIMEOUT = 30  # seconds
    DEFAULT_MEMORY = "512m"
    DEFAULT_CPU = 0.5
    
    def __init__(self, mode: str = "docker"):
        self.mode = mode
        if mode == "docker" and DOCKER_AVAILABLE:
            try:
                self.client = docker.from_env()
                self._ensure_images()
            except Exception as e:
                print(f"⚠️ Docker connection failed: {e}")
                self.mode = "subprocess" # Fallback to unsafe subprocess (not recommended)
        else:
            self.mode = "subprocess"
            
    def _ensure_images(self):
        """Ensure required docker images are available."""
        required = ["python:3.10-slim", "node:18-slim"]
        for img in required:
            try:
                self.client.images.get(img)
            except docker.errors.ImageNotFound:
                print(f"📥 Pulling image {img}...")
                self.client.images.pull(img)

    def execute_python(
        self,
        code: str,
        timeout: Optional[int] = None,
        requirements: List[str] = None
    ) -> ExecutionResult:
        """Execute Python code in sandbox."""
        if self.mode == "docker":
            return self._execute_docker("python:3.10-slim", ["python", "-c", code], timeout)
        else:
            return self._execute_unsafe_subprocess(["python", "-c", code], timeout)

    def execute_nodejs(
        self,
        code: str,
        timeout: Optional[int] = None
    ) -> ExecutionResult:
        """Execute Node.js code in sandbox."""
        if self.mode == "docker":
            return self._execute_docker("node:18-slim", ["node", "-e", code], timeout)
        else:
            return self._execute_unsafe_subprocess(["node", "-e", code], timeout)

    def _execute_docker(
        self,
        image: str,
        command: List[str],
        timeout: Optional[int] = None
    ) -> ExecutionResult:
        """Execute command in Docker container."""
        timeout = timeout or self.DEFAULT_TIMEOUT
        start_time = time.time()
        
        try:
            container = self.client.containers.run(
                image=image,
                command=command,
                mem_limit=self.DEFAULT_MEMORY,
                nano_cpus=int(self._cpu_to_nanocpus(self.DEFAULT_CPU)),
                network_disabled=True,
                detach=True,
                read_only=False, # Need for some scripts to write temporary files
            )
            
            try:
                result = container.wait(timeout=timeout)
                exit_code = result["StatusCode"]
                stdout = container.logs(stdout=True, stderr=False).decode()
                stderr = container.logs(stdout=False, stderr=True).decode()
                timed_out = False
            except Exception:
                # Timeout occurred
                container.kill()
                exit_code = -1
                stdout = ""
                stderr = f"Execution timed out after {timeout}s"
                timed_out = True
            finally:
                container.remove(force=True)
                
            duration = (time.time() - start_time) * 1000
            
            return ExecutionResult(
                success=exit_code == 0,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                duration_ms=duration,
                timed_out=timed_out
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                exit_code=1,
                stdout="",
                stderr=str(e),
                duration_ms=(time.time() - start_time) * 1000
            )

    def _execute_unsafe_subprocess(
        self,
        command: List[str],
        timeout: Optional[int] = None
    ) -> ExecutionResult:
        """
        FALLBACK: Execute command via subprocess.
        WARNING: This is NOT isolated and only used as a last resort fallback.
        """
        import subprocess
        
        print("⚠️ WARNING: Executing code via UNSAFE subprocess fallback.")
        
        timeout = timeout or self.DEFAULT_TIMEOUT
        start_time = time.time()
        
        try:
            proc = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            try:
                stdout, stderr = proc.communicate(timeout=timeout)
                exit_code = proc.returncode
                timed_out = False
            except subprocess.TimeoutExpired:
                proc.kill()
                stdout, stderr = proc.communicate()
                exit_code = -1
                timed_out = True
                stderr += f"\n[TIMEOUT] Execution killed after {timeout}s"
                
            duration = (time.time() - start_time) * 1000
            
            return ExecutionResult(
                success=exit_code == 0,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                duration_ms=duration,
                timed_out=timed_out,
                metadata={"engine": "subprocess"}
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                exit_code=1,
                stdout="",
                stderr=str(e),
                duration_ms=(time.time() - start_time) * 1000,
                metadata={"engine": "subprocess"}
            )

    def _cpu_to_nanocpus(self, cpu: float) -> int:
        """Convert fractional CPUs to nano_cpus for Docker API."""
        return int(cpu * 1_000_000_000)


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sandbox Executor - Safe Code Execution")
    parser.add_argument("--lang", choices=["python", "nodejs"], default="python", help="Script language")
    parser.add_argument("--code", required=True, help="Code string or path to file")
    parser.add_argument("--timeout", type=int, default=30, help="Execution timeout in seconds")
    parser.add_argument("--mode", choices=["docker", "subprocess"], default="docker", help="Execution mode")
    
    args = parser.parse_args()
    
    code = args.code
    if Path(code).exists():
        code = Path(code).read_text(encoding='utf-8')
        
    executor = SandboxExecutor(mode=args.mode)
    
    if args.lang == "python":
        result = executor.execute_python(code, timeout=args.timeout)
    else:
        result = executor.execute_nodejs(code, timeout=args.timeout)
        
    print(json.dumps(result.to_dict(), indent=2))


if __name__ == "__main__":
    main()
