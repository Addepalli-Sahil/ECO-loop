# System Architecture

## Overview

The Eco-Loop Building Agents system implements a closed-loop control architecture that continuously optimizes building operations through AI-driven decision making.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLOSED-LOOP CONTROL SYSTEM                   │
└─────────────────────────────────────────────────────────────────┘

                    ┌────────────────────────────┐
                    │  EnergyPlus Simulation     │
                    │  (Building Physics Model)  │
                    └────────────┬───────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  Metrics Collection     │
                    │ - Zone Temperatures     │
                    │ - HVAC Load             │
                    │ - Energy Consumption    │
                    │ - Occupancy             │
                    │ - Thermal Comfort (PMV) │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────▼──────────────────┐
              │      LLM Agent (Analysis)           │
              │  ┌────────────────────────────┐    │
              │  │ 1. Analyze Metrics        │    │
              │  │ 2. Evaluate Constraints   │    │
              │  │ 3. Identify Opportunities │    │
              │  │ 4. Generate Actions       │    │
              │  └────────────────────────────┘    │
              └──────────────┬───────────────────────┘
                             │
                ┌────────────▼────────────┐
                │  Control Actions        │
                │ - Setpoint Updates      │
                │ - Schedule Modifications│
                │ - Equipment Overrides   │
                └────────────┬────────────┘
                             │
              ┌──────────────▼───────────────┐
              │  Simulation Update           │
              │ (Action Injection)           │
              └──────────────┬───────────────┘
                             │
              (LOOP CONTINUES - 5 minute intervals)
```

## Core Components

### 1. **EnergyPlus Wrapper** (`energyplus_wrapper.py`)

**Responsibilities:**
- Spawn and manage EnergyPlus simulation process
- Parse and feed IDF building model files
- Collect real-time simulation metrics
- Stream sensor data to the LLM agent
- Execute control actions (setpoint updates, schedule changes)
- Handle simulation errors and restart logic

**Key Methods:**
- `start_simulation(duration)`: Initialize and run building simulation
- `get_current_metrics()`: Retrieve real-time building state
- `update_setpoint(zone, temperature)`: Modify HVAC setpoints
- `modify_schedule(name, values)`: Change operational schedules

**Integration Points:**
- Input: Building model files (`.idf`)
- Output: Time-series metrics (JSON)
- Control: EMS/API calls back to simulation

### 2. **LLM Agent** (`llm_agent.py`)

**Responsibilities:**
- Analyze building performance metrics
- Reason about energy conservation measures (ECMs)
- Generate optimal control recommendations
- Enforce thermal comfort constraints
- Maintain decision history for learning
- Handle tool-calling for complex optimizations

**Key Methods:**
- `generate_control_actions(metrics)`: Main optimization routine
- `analyze_metrics(metrics)`: Parse and categorize building state
- `update_constraints(limits)`: Dynamically adjust comfort bounds

**LLM Tool-Calling Architecture:**

The agent has access to these tools:

```python
tools = {
    "analyze_comfort": "Evaluate PMV/PPD thermal comfort",
    "optimize_ecm": "Calculate energy conservation measures",
    "simulate_action": "Predict impact of control action",
    "get_baseline": "Retrieve baseline energy profile",
    "estimate_savings": "Calculate potential kWh reduction"
}
```

**Prompt Engineering Strategy:**

1. **System Prompt**: Establishes agent role and optimization objectives
2. **Context Window**: Includes recent metrics and action history
3. **Constraint Embedding**: Hard limits on temperature, humidity, occupancy
4. **Few-Shot Examples**: Demonstrates reasoning patterns
5. **Token Management**: Summarizes lengthy logs to fit context limits

Example system prompt:
```
You are an autonomous building energy optimization agent. Your objective is to 
minimize energy consumption while maintaining occupant thermal comfort 
(PMV between -0.5 and +0.5, PPD < 20%). 

You have real-time access to:
- Current zone temperatures and setpoints
- HVAC load and energy consumption
- Occupancy and comfort indices

Generate 2-3 specific energy conservation measures (ECMs) that:
1. Reduce energy consumption
2. Maintain comfort within constraints
3. Include confidence levels and rationales
```

### 3. **Closed-Loop Controller** (`controller.py`)

**Responsibilities:**
- Orchestrate the feedback loop
- Coordinate simulation execution with metric collection
- Trigger LLM analysis at regular intervals
- Execute control actions generated by the agent
- Maintain logs and metrics history
- Generate performance reports

**Control Loop Flow:**

```
1. START SIMULATION (Duration: 365 days)
2. LOOP (Every 5 minutes):
   a. Collect metrics from EnergyPlus
   b. Query LLM agent for analysis
   c. Generate control actions
   d. Apply actions to simulation
   e. Log results
3. CONTINUE until simulation end
4. GENERATE PERFORMANCE REPORT
```

**Key Methods:**
- `start()`: Begin closed-loop operation
- `_execute_control_step()`: Single iteration of the loop
- `get_performance_report()`: Summary with energy savings

### 4. **Metrics & Logging**

**Metrics Collected:**

- **Thermal Comfort**: Zone temperatures, setpoints, PMV (Predicted Mean Vote), PPD (Predicted % Dissatisfied)
- **Energy**: HVAC load, energy consumption (kWh), peak demand
- **Occupancy**: Zone-by-zone occupancy ratio
- **System State**: Equipment status, valve positions, damper angles
- **Control History**: All actions taken and their effects

**Logging Strategy:**

```
Metrics Log:
├── Timestamp
├── Zone Temperatures
├── Occupancy
├── HVAC Load (kW)
├── Energy Consumption (kWh)
├── Thermal Comfort (PMV/PPD)
└── Metadata

Actions Log:
├── Timestamp
├── Action Type (setpoint, schedule, override)
├── Target Zone
├── Value
├── Confidence
└── Rationale
```

## Communication Protocol

### EnergyPlus ↔ Agent Communication

**Data Flow:**

1. **Metrics → LLM** (JSON):
```json
{
  "timestamp": "2024-01-15T14:30:00Z",
  "zone_temperatures": {"Zone1": 22.5, "Zone2": 21.8},
  "occupancy": 0.75,
  "hvac_load": 5.2,
  "energy_consumption": 125.7,
  "pmv": -0.3,
  "ppd": 8.5
}
```

2. **Actions → EnergyPlus** (Structured Commands):
```json
{
  "action_type": "setpoint_update",
  "target_zone": "Zone1",
  "value": 21.0,
  "confidence": 0.85,
  "rationale": "Reduce setpoint to optimize cooling load during low occupancy"
}
```

## Prompt Latency Management

**Challenge:** Long simulation logs can exceed LLM context windows

**Solutions:**

1. **Log Summarization**: Compress 24-hour logs to key statistics
2. **Sliding Window**: Maintain only recent 7-day history
3. **Feature Extraction**: Focus on significant state changes
4. **Batching**: Process multiple metrics in single LLM call

**Implementation:**

```python
def compress_metrics_log(log, window_size=7*24*60):
    """Compress log to sliding window of most recent entries."""
    if len(log) > window_size:
        return log[-window_size:]
    return log

def summarize_log_period(log, hours=24):
    """Create statistical summary for a period."""
    return {
        "period": f"last_{hours}h",
        "avg_temp": mean(log.temperatures),
        "peak_load": max(log.hvac_loads),
        "total_energy": sum(log.energy),
        "comfort_violations": count(log.ppd > 20)
    }
```

## Error Handling & Recovery

**Simulation Failures:**

- **Detection**: Monitor EnergyPlus process and stderr
- **Logging**: Record error messages and state
- **Recovery**: 
  - Attempt restart with modified parameters
  - Fall back to rule-based control
  - Alert operator if persistent

**LLM Unavailability:**

- **Fallback**: Rules-based agent provides safe defaults
- **Buffering**: Queue metrics while LLM is down
- **Graceful Degradation**: Continue with simpler strategies

**Constraint Violations:**

- **Validation**: Check all actions against hard limits
- **Filtering**: Reject unsafe recommendations
- **Logging**: Record all constraint violations

## Performance Metrics

**System Evaluation Criteria:**

1. **Stability**: Crash-free operation over extended periods
2. **Responsiveness**: Control latency < 1 minute
3. **Accuracy**: Predictions match actual simulation outcomes
4. **Efficiency**: Quantifiable energy reduction (target: >15%)
5. **Comfort**: Maintain PMV within ±0.5, PPD < 20%

## Extensibility

**Adding New Zones/Buildings:**

1. Modify `.idf` files in `models/` directory
2. Update constraint limits in agent configuration
3. Re-run controller with new model path

**Integrating Different LLMs:**

```python
# Switch LLM backend
agent = BuildingAgent(
    llm_endpoint="http://localhost:8000",
    model="mistral-7b"  # Different model
)
```

**Adding New Optimization Metrics:**

```python
class ExtendedMetrics(BaseModel):
    # Add new metrics
    co2_equivalent: float
    grid_carbon_intensity: float
    demand_charge: float
```

---

**Document Version**: 1.0  
**Last Updated**: 2024-07-26
