# MCP Protocol Implementation

## Overview

The Eco-Loop system implements the Model Context Protocol (MCP) to enable standardized, bidirectional communication between the LLM agent and external tools/services.

## MCP Server Setup

The MCP server acts as a bridge between the LLM and building control systems.

```python
# mcp_server.py
from mcp.server import MCPServer
from eco_loop.energyplus_wrapper import EnergyPlusSimulation
from eco_loop.llm_agent import BuildingAgent

class BuildingMCPServer(MCPServer):
    """MCP Server for building optimization"""
    
    def __init__(self, sim: EnergyPlusSimulation, agent: BuildingAgent):
        super().__init__()
        self.sim = sim
        self.agent = agent
        self._register_tools()
    
    def _register_tools(self):
        """Register available tools for LLM"""
        
        @self.tool()
        def get_metrics(zone: str = None) -> dict:
            """Get current building metrics"""
            return self.sim.get_current_metrics()
        
        @self.tool()
        def update_setpoint(zone: str, temperature: float) -> bool:
            """Update HVAC setpoint"""
            return self.sim.update_setpoint(zone, temperature)
        
        @self.tool()
        def analyze_comfort(metrics: dict) -> dict:
            """Analyze thermal comfort"""
            return self.agent.analyze_metrics(metrics)
        
        @self.tool()
        def forecast_energy(hours: int = 24) -> list:
            """Forecast energy consumption"""
            # Implementation
            pass
```

## Tool Definitions

The LLM has access to the following tools via MCP:

### 1. get_metrics
```
Description: Retrieve current building state
Input: 
  - zone_id (optional): Specific zone to query
Output: {
  timestamp, zone_temperatures, hvac_load, 
  energy_consumption, occupancy, pmv, ppd
}
```

### 2. update_setpoint
```
Description: Modify HVAC setpoint for a zone
Input:
  - zone_id: Target zone
  - temperature: New setpoint (°C)
Output: {success: bool, message: str}
```

### 3. get_schedule
```
Description: Retrieve current operational schedule
Input:
  - schedule_name: HVAC, lighting, occupancy, etc.
Output: [hourly_values_0_to_23]
```

### 4. modify_schedule
```
Description: Change operational schedule
Input:
  - schedule_name: Name to modify
  - new_values: [24 hourly values]
Output: {success: bool, message: str}
```

### 5. analyze_comfort
```
Description: Calculate thermal comfort indices
Input: {zone_temps, relative_humidity, air_velocity, mean_radiant_temp}
Output: {pmv: float, ppd: float, comfortable: bool}
```

### 6. get_baseline_profile
```
Description: Retrieve baseline energy profile for comparison
Input: {start_date, end_date}
Output: {
  timestamps: [...],
  baseline_energy: [...],
  baseline_temps: [...]
}
```

### 7. forecast_savings
```
Description: Estimate energy savings for a proposed control action
Input: {action_type, parameters, duration_hours}
Output: {
  estimated_savings_kwh: float,
  estimated_cost_savings: float,
  confidence: float
}
```

## Protocol Flow

```
┌──────────────┐
│  LLM Agent   │
└──────┬───────┘
       │ "I need metrics to analyze"
       │ (MCP Request)
       ▼
┌──────────────────┐
│   MCP Server     │
│  (Tool Router)   │
└──────┬───────────┘
       │ (executes: get_metrics)
       ▼
┌──────────────────┐
│ EnergyPlus Sim   │
└──────┬───────────┘
       │ {metrics JSON}
       ▼
┌──────────────────┐
│   MCP Server     │
│  (Format Result) │
└──────┬───────────┘
       │ (MCP Response)
       ▼
┌──────────────────┐
│  LLM Agent       │
│  (Processes)     │
└──────────────────┘
```

## LLM Tool-Calling Examples

### Example 1: Analyze Current State

```
LLM (System): Analyze the current building state and recommend optimizations.

LLM (Internal Reasoning): 
I need to get current metrics first to understand the building state.

LLM Tool Call: get_metrics()
MCP Response: {
  "zone_temperatures": {"Zone1": 23.5, "Zone2": 22.1},
  "occupancy": 0.8,
  "hvac_load": 6.2,
  "energy_consumption": 145.3,
  "pmv": 0.2,
  "ppd": 12.5
}

LLM (Analysis):
Current state shows:
- Zone1 is slightly warm (23.5°C)
- High occupancy (80%)
- Energy consumption is elevated
- Comfort is acceptable (PMV +0.2)

Recommendation: Reduce setpoint by 1°C to optimize cooling load

LLM Tool Call: forecast_savings(
  action_type="setpoint_update",
  parameters={"zone": "Zone1", "target": 22.5},
  duration_hours=24
)
MCP Response: {
  "estimated_savings_kwh": 8.5,
  "estimated_cost_savings": 1.23,
  "confidence": 0.85
}

LLM (Decision):
The forecasted savings (8.5 kWh) with high confidence (85%) and maintained 
comfort suggest this is a good action. Apply it.

LLM Tool Call: update_setpoint(
  zone="Zone1",
  temperature=22.5
)
MCP Response: {"success": true, "message": "Setpoint updated"}
```

### Example 2: Schedule Optimization

```
LLM (Observation): 
Evening hours show sustained high energy despite low occupancy.

LLM Tool Call: get_schedule(schedule_name="occupancy")
MCP Response: [1,1,1,0.5,0.2,0.1,0.1,0.1,0.5,1,1,1,1,1,1,1,0.5,0.3,0.2,0.1,0,0,0]

LLM (Analysis):
Occupancy drops significantly at hour 18 (6 PM) but current HVAC 
schedule likely continues at full capacity.

LLM Tool Call: get_schedule(schedule_name="hvac_cooling")
MCP Response: [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0.5,0.3,0.1,0.1,0.1]

LLM (Insight):
HVAC runs at full capacity until 7 PM (hour 19) even though occupancy 
drops at 6 PM. This is inefficient.

LLM Tool Call: modify_schedule(
  schedule_name="hvac_cooling",
  new_values=[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0.8,0.5,0.3,0.2,0.1,0.1,0.1,0.1]
)

LLM (Verification):
Schedule updated. This should reduce evening energy consumption by ~5%.
```

## Error Handling in MCP

**Tool Execution Errors:**

```python
class ToolError(Exception):
    """Raised when tool execution fails"""
    pass

@self.tool()
def update_setpoint(zone: str, temperature: float):
    try:
        result = self.sim.update_setpoint(zone, temperature)
        if not result:
            raise ToolError(f"Failed to update setpoint for {zone}")
        return {"success": True, "zone": zone, "temperature": temperature}
    except Exception as e:
        # LLM receives error details
        return {
            "success": False, 
            "error": str(e),
            "suggestion": "Check zone name and temperature range"
        }
```

**LLM Recovery Strategy:**

When tools fail, LLM can:
1. Retry with adjusted parameters
2. Try alternative tools
3. Request diagnostics
4. Fall back to rule-based control

## Monitoring & Logging

**Tool Call Tracking:**

```python
@self.middleware()
def log_tool_calls(tool_name, inputs, outputs):
    """Log all tool calls for audit trail"""
    logger.info(f"MCP Tool: {tool_name}")
    logger.debug(f"  Inputs: {inputs}")
    logger.debug(f"  Outputs: {outputs}")
```

**Performance Metrics:**

- Tool execution latency
- Success/failure rate per tool
- LLM decision quality
- Energy savings achieved

---

**Version**: 1.0  
**Last Updated**: 2024-07-26
