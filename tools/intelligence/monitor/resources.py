import time
import random

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

class SystemResourceMonitor:
    """
    A simple monitor for system resources (CPU, Memory).
    """
    def __init__(self):
        self.cpu_usage = 0.0
        self.memory_usage = 0.0

    def get_cpu_usage(self):
        """Get current CPU usage percentage."""
        if HAS_PSUTIL:
            self.cpu_usage = psutil.cpu_percent(interval=0.1)
        else:
            # Mock data for testing if psutil is missing
            self.cpu_usage = round(random.uniform(5.0, 30.0), 2)
        return self.cpu_usage

    def get_memory_usage(self):
        """Get current Memory usage percentage."""
        if HAS_PSUTIL:
            memory = psutil.virtual_memory()
            self.memory_usage = memory.percent
        else:
            # Mock data
            self.memory_usage = round(random.uniform(40.0, 60.0), 2)
        return self.memory_usage

    def log_stats(self):
        """Print current statistics."""
        cpu = self.get_cpu_usage()
        mem = self.get_memory_usage()
        status = "🟢 Nominal" if cpu < 50 else "🟡 High"
        print(f"[{status}] CPU: {cpu}% | Memory: {mem}%")

    def run_check(self, iterations=3):
        """Run a few checks."""
        print("Starting System Resource Monitor...")
        for _ in range(iterations):
            self.log_stats()
            time.sleep(0.5)
        print("Monitoring complete.")

if __name__ == "__main__":
    monitor = SystemResourceMonitor()
    monitor.run_check()
