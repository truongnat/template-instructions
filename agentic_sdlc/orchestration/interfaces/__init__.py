"""
Interface modules for the Multi-Agent Orchestration System

This package contains interface classes for managing different aspects
of the orchestration system, including CLI process management and
communication protocols.
"""

from .cli_interface import CLIInterface, CommunicationProtocol, HeartbeatConfig

__all__ = [
    "CLIInterface",
    "CommunicationProtocol", 
    "HeartbeatConfig"
]