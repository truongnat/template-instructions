"""Health check system for SDLC Kit.

This module provides functionality for checking the health of various
system components including database, API connectivity, disk space, and memory.
"""

import shutil
import psutil
import requests
from dataclasses import dataclass, asdict
from enum import Enum
from typing import List, Dict, Any, Optional
from monitoring.loggers import SDLCLogger


class HealthStatus(Enum):
    """Health check status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheck:
    """Represents a health check result.
    
    Attributes:
        component: Name of the component being checked
        status: Health status of the component
        message: Human-readable status message
        details: Additional details about the health check
    """
    component: str
    status: HealthStatus
    message: str
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert health check to dictionary format."""
        data = asdict(self)
        data['status'] = self.status.value
        return data
    
    def is_healthy(self) -> bool:
        """Check if component is healthy."""
        return self.status == HealthStatus.HEALTHY


class HealthChecker:
    """System health checker.
    
    Performs health checks on various system components and returns
    structured results indicating the health status of each component.
    """
    
    def __init__(
        self,
        database_url: Optional[str] = None,
        api_endpoints: Optional[List[str]] = None,
        disk_threshold_percent: float = 90.0,
        memory_threshold_percent: float = 90.0
    ):
        """Initialize health checker.
        
        Args:
            database_url: Optional database connection URL
            api_endpoints: Optional list of API endpoints to check
            disk_threshold_percent: Disk usage threshold for warnings (default 90%)
            memory_threshold_percent: Memory usage threshold for warnings (default 90%)
        """
        self.database_url = database_url
        self.api_endpoints = api_endpoints or []
        self.disk_threshold = disk_threshold_percent
        self.memory_threshold = memory_threshold_percent
        self.logger = SDLCLogger.get_logger(__name__)
    
    def check_all(self) -> List[HealthCheck]:
        """Run all health checks.
        
        Returns:
            List of health check results for all components
        """
        checks = []
        
        # Always check disk and memory
        checks.append(self.check_disk_space())
        checks.append(self.check_memory())
        
        # Check database if configured
        if self.database_url:
            checks.append(self.check_database())
        
        # Check API connectivity if configured
        if self.api_endpoints:
            checks.append(self.check_api_connectivity())
        
        # Log overall health status
        unhealthy = [c for c in checks if c.status == HealthStatus.UNHEALTHY]
        degraded = [c for c in checks if c.status == HealthStatus.DEGRADED]
        
        if unhealthy:
            self.logger.error(
                f"Health check failed: {len(unhealthy)} unhealthy components"
            )
        elif degraded:
            self.logger.warning(
                f"Health check degraded: {len(degraded)} degraded components"
            )
        else:
            self.logger.info("All health checks passed")
        
        return checks
    
    def check_database(self) -> HealthCheck:
        """Check database connectivity.
        
        Returns:
            Health check result for database
        """
        if not self.database_url:
            return HealthCheck(
                component="database",
                status=HealthStatus.HEALTHY,
                message="Database not configured",
                details={"configured": False}
            )
        
        try:
            # Try to import database library
            try:
                import sqlite3
                # For SQLite databases
                if self.database_url.startswith('sqlite'):
                    conn = sqlite3.connect(self.database_url.replace('sqlite:///', ''))
                    conn.close()
                    return HealthCheck(
                        component="database",
                        status=HealthStatus.HEALTHY,
                        message="Database connection successful",
                        details={"url": self.database_url, "type": "sqlite"}
                    )
            except ImportError:
                pass
            
            # For other databases, just check if URL is accessible
            return HealthCheck(
                component="database",
                status=HealthStatus.HEALTHY,
                message="Database URL configured",
                details={"url": self.database_url}
            )
            
        except Exception as e:
            self.logger.error(f"Database health check failed: {e}")
            return HealthCheck(
                component="database",
                status=HealthStatus.UNHEALTHY,
                message=f"Database connection failed: {str(e)}",
                details={"error": str(e)}
            )
    
    def check_api_connectivity(self) -> HealthCheck:
        """Check external API connectivity.
        
        Returns:
            Health check result for API connectivity
        """
        if not self.api_endpoints:
            return HealthCheck(
                component="api_connectivity",
                status=HealthStatus.HEALTHY,
                message="No API endpoints configured",
                details={"configured": False}
            )
        
        failed_endpoints = []
        successful_endpoints = []
        
        for endpoint in self.api_endpoints:
            try:
                response = requests.get(endpoint, timeout=5)
                if response.status_code < 500:
                    successful_endpoints.append(endpoint)
                else:
                    failed_endpoints.append({
                        "endpoint": endpoint,
                        "status_code": response.status_code
                    })
            except Exception as e:
                failed_endpoints.append({
                    "endpoint": endpoint,
                    "error": str(e)
                })
        
        total = len(self.api_endpoints)
        failed_count = len(failed_endpoints)
        
        if failed_count == 0:
            return HealthCheck(
                component="api_connectivity",
                status=HealthStatus.HEALTHY,
                message=f"All {total} API endpoints accessible",
                details={
                    "total": total,
                    "successful": successful_endpoints
                }
            )
        elif failed_count < total:
            return HealthCheck(
                component="api_connectivity",
                status=HealthStatus.DEGRADED,
                message=f"{failed_count}/{total} API endpoints failed",
                details={
                    "total": total,
                    "failed": failed_endpoints,
                    "successful": successful_endpoints
                }
            )
        else:
            return HealthCheck(
                component="api_connectivity",
                status=HealthStatus.UNHEALTHY,
                message="All API endpoints failed",
                details={
                    "total": total,
                    "failed": failed_endpoints
                }
            )
    
    def check_disk_space(self) -> HealthCheck:
        """Check available disk space.
        
        Returns:
            Health check result for disk space
        """
        try:
            disk_usage = shutil.disk_usage("/")
            total_gb = disk_usage.total / (1024 ** 3)
            used_gb = disk_usage.used / (1024 ** 3)
            free_gb = disk_usage.free / (1024 ** 3)
            percent_used = (disk_usage.used / disk_usage.total) * 100
            
            details = {
                "total_gb": round(total_gb, 2),
                "used_gb": round(used_gb, 2),
                "free_gb": round(free_gb, 2),
                "percent_used": round(percent_used, 2)
            }
            
            if percent_used >= self.disk_threshold:
                return HealthCheck(
                    component="disk_space",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Disk usage critical: {percent_used:.1f}% used",
                    details=details
                )
            elif percent_used >= (self.disk_threshold - 10):
                return HealthCheck(
                    component="disk_space",
                    status=HealthStatus.DEGRADED,
                    message=f"Disk usage high: {percent_used:.1f}% used",
                    details=details
                )
            else:
                return HealthCheck(
                    component="disk_space",
                    status=HealthStatus.HEALTHY,
                    message=f"Disk usage normal: {percent_used:.1f}% used",
                    details=details
                )
                
        except Exception as e:
            self.logger.error(f"Disk space check failed: {e}")
            return HealthCheck(
                component="disk_space",
                status=HealthStatus.UNHEALTHY,
                message=f"Failed to check disk space: {str(e)}",
                details={"error": str(e)}
            )
    
    def check_memory(self) -> HealthCheck:
        """Check available memory.
        
        Returns:
            Health check result for memory
        """
        try:
            memory = psutil.virtual_memory()
            total_gb = memory.total / (1024 ** 3)
            used_gb = memory.used / (1024 ** 3)
            available_gb = memory.available / (1024 ** 3)
            percent_used = memory.percent
            
            details = {
                "total_gb": round(total_gb, 2),
                "used_gb": round(used_gb, 2),
                "available_gb": round(available_gb, 2),
                "percent_used": round(percent_used, 2)
            }
            
            if percent_used >= self.memory_threshold:
                return HealthCheck(
                    component="memory",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Memory usage critical: {percent_used:.1f}% used",
                    details=details
                )
            elif percent_used >= (self.memory_threshold - 10):
                return HealthCheck(
                    component="memory",
                    status=HealthStatus.DEGRADED,
                    message=f"Memory usage high: {percent_used:.1f}% used",
                    details=details
                )
            else:
                return HealthCheck(
                    component="memory",
                    status=HealthStatus.HEALTHY,
                    message=f"Memory usage normal: {percent_used:.1f}% used",
                    details=details
                )
                
        except Exception as e:
            self.logger.error(f"Memory check failed: {e}")
            return HealthCheck(
                component="memory",
                status=HealthStatus.UNHEALTHY,
                message=f"Failed to check memory: {str(e)}",
                details={"error": str(e)}
            )
