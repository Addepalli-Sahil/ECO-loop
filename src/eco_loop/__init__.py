"""
Eco-Loop Building Agents: Autonomous AI-driven building management system

This package provides an integrated framework for:
- High-fidelity building energy simulations (EnergyPlus)
- AI-driven decision making (Open-Source LLMs)
- Closed-loop control and optimization (MCP)
- Real-time performance monitoring and dashboards

Version: 0.1.0
"""

__version__ = "0.1.0"
__author__ = "Eco-Loop Team"

from .energyplus_wrapper import EnergyPlusSimulation
from .llm_agent import BuildingAgent
from .controller import ClosedLoopController
from .mcp_server import BuildingToolRegistry

__all__ = [
    "EnergyPlusSimulation",
    "BuildingAgent", 
    "ClosedLoopController",
    "BuildingToolRegistry",
]
