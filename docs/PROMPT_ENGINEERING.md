# Prompt Engineering Strategies

## Overview

Effective prompt engineering is critical for LLM-based building optimization. This document outlines strategies for:
- Constraint encoding
- Context management
- Action generation
- Error recovery
- Performance optimization

## System Prompt Template

```
You are an autonomous building energy optimization agent operating 
within Eco-Loop, an AI-driven facility management system.

PRIMARY OBJECTIVE:
Minimize building energy consumption while maintaining occupant 
thermal comfort within strict boundaries.

OPERATIONAL CONSTRAINTS (HARD LIMITS):
- Temperature Range: 18°C - 26°C (must not violate)
- Thermal Comfort Index (PMV): -0.5 to +0.5 (acceptable range)
- Maximum Dissatisfaction (PPD): < 20% (hard limit)
- Humidity Range: 30% - 60% RH

CAPABILITIES:
You have real-time access to building metrics and can execute 
control actions through the MCP tool system.

DECISION CRITERIA:
When evaluating potential actions:
1. Will this maintain comfort within constraints? (If no, REJECT)
2. What is the estimated energy savings? (Quantify)
3. What is the confidence level in the prediction? (0-1)
4. Are there any safety concerns? (List)

OUTPUT FORMAT:
Always respond with structured JSON containing recommended actions.
Include rationale and confidence for each recommendation.

TONE:
Be analytical, precise, and conservative. Prioritize comfort 
over cost when in doubt.
```

## Few-Shot Examples

Include concrete examples to guide LLM behavior:

```
EXAMPLE 1: Temperature-Based Optimization
Input:
{
  "zone_temperatures": {"Zone1": 24.2, "Zone2": 21.5},
  "target_temperature": 22.0,
  "occupancy": 0.65,
  "hvac_load": 7.8,
  "pmv": 0.3,
  "ppd": 15.2
}

Your Response:
[
  {
    "action_type": "setpoint_update",
    "target_zone": "Zone1",
    "value": 21.5,
    "confidence": 0.82,
    "rationale": "Zone1 is 2.2°C above target. Reducing setpoint by 0.7°C will bring 
                  temperature toward target while maintaining comfort (PMV still within 
                  ±0.5 bounds). Estimated savings: 1.5 kWh over 24 hours."
  }
]

EXAMPLE 2: Occupancy-Based Scheduling
Input:
{
  "current_hour": 18,
  "occupancy_forecast": [0.1, 0.05, 0.02, 0.01, 0.02, 0.05, ...],
  "current_hvac_load": 2.1,
  "baseline_setpoint": 22.0,
  "evening_energy_consumption": "elevated"
}

Your Response:
[
  {
    "action_type": "schedule_change",
    "target_schedule": "hvac_setpoint_evening",
    "value": [22, 22, 23, 24, 24, 23, ...],
    "confidence": 0.75,
    "rationale": "Building occupancy drops dramatically after 6 PM but HVAC continues 
                  full conditioning. Relaxing setpoints by 1-2°C during low-occupancy 
                  hours can save ~10% of evening energy while maintaining comfort for 
                  remaining occupants. No comfort violations expected."
  }
]
```

## Token Optimization

**Strategy**: Compress verbose context to fit within LLM context windows

### 1. Metric Summarization

Instead of sending full hourly data:

```python
# INSTEAD OF (verbose):
metrics = {
    "hours": [0,1,2,3,...,23],
    "temperatures": [18.2, 18.1, 17.9, ...],
    "hvac_load": [0.1, 0.1, 0.1, ...],
    "energy": [1.2, 1.1, 1.0, ...],
    ...
}

# USE (compressed):
metrics_summary = {
    "period": "last_24h",
    "avg_temperature": 21.4,
    "min_temp": 17.9,
    "max_temp": 24.5,
    "avg_hvac_load": 4.2,
    "peak_hvac_load": 8.1,
    "total_energy_kwh": 85.3,
    "occupancy_pattern": "standard_weekday",
    "comfort_violations": 0,
    "anomalies": ["elevated_evening_load"]
}
```

### 2. Context Windowing

Maintain only relevant time period:

```python
def get_context_for_llm(metrics_log, max_tokens=2000):
    """Extract most relevant context for LLM"""
    
    # Keep recent 7 days
    recent_metrics = metrics_log[-7*24*60:]
    
    # Identify significant events
    significant_events = [m for m in recent_metrics 
                         if m['ppd'] > 20 or m['hvac_load'] > peak_threshold]
    
    # Build minimal context
    context = {
        "summary": compress_to_summary(recent_metrics),
        "anomalies": significant_events,
        "last_action": metrics_log[-1]['last_action'],
        "cumulative_savings": calculate_savings(metrics_log)
    }
    
    return context
```

### 3. Feature Extraction

Highlight only critical features:

```python
def extract_critical_features(metrics_full):
    """Extract minimal but sufficient features"""
    
    return {
        # Thermal state
        "zones_comfortable": count_comfortable_zones(metrics_full),
        "worst_discomfort": max_discomfort_index(metrics_full),
        
        # Energy state  
        "consumption_vs_baseline": percent_change(metrics_full),
        "peak_load": max(metrics_full.hvac_loads),
        
        # Trend
        "consumption_trend": is_increasing(metrics_full),
        "comfort_trend": is_degrading(metrics_full),
        
        # Actions
        "recent_actions": last_n_actions(metrics_full, n=3),
        "action_effectiveness": evaluate_recent_actions(metrics_full)
    }
```

## Constraint Embedding

Strategies to prevent constraint violations:

### Hard Constraints (Always Enforced)

```python
HARD_CONSTRAINTS = {
    "min_temperature": 18.0,
    "max_temperature": 26.0,
    "max_ppd": 20.0,
    "min_occupancy_comfort": "maintained"
}

# Embed in prompt
constraint_text = f"""
MANDATORY HARD LIMITS (Do not exceed):
- Temperature: {HARD_CONSTRAINTS['min_temperature']}°C - {HARD_CONSTRAINTS['max_temperature']}°C
- Comfort violation threshold: {HARD_CONSTRAINTS['max_ppd']}% PPD

Any action that would violate these limits MUST be rejected.
"""
```

### Soft Constraints (Prefer but Allow)

```python
SOFT_CONSTRAINTS = {
    "preferred_pmv_range": (-0.5, 0.5),
    "humidity_range": (30, 60),
    "noise_level": "low"
}

# Include in evaluation criteria
evaluation_prompt = """
OPTIMIZATION PREFERENCES (desirable but not mandatory):
- Maintain PMV between -0.5 and +0.5 (very comfortable)
- Maintain humidity between 30-60% RH
- Minimize HVAC noise during evening hours

Balance these preferences against energy savings.
"""
```

## Recursive Reasoning Patterns

**Chain-of-Thought Prompting:**

```
Encourage step-by-step reasoning:

"Let me think through this step by step:
1. What is the current thermal state? [analyze]
2. What are the constraints I must respect? [list]
3. What are potential energy-saving actions? [brainstorm]
4. For each action, will it violate constraints? [validate]
5. Which action has highest confidence? [rank]
6. What is the projected impact? [quantify]"
```

**Self-Verification:**

```
Include verification step:

"After generating a recommendation, verify:
- Will this maintain temperature within [min, max]?
- Will this maintain PMV within ±0.5?
- Is confidence level reasonable for this action?
- Have I considered unintended consequences?"
```

## Error Recovery Prompts

**Handling Simulation Errors:**

```
If simulation error detected:

"The building simulation has encountered an error. 
Error details: [error message]

Your task:
1. Identify what went wrong
2. Suggest a modified control action that might avoid this issue
3. Recommend reverting to the previously successful configuration
4. Request simulation diagnostics"
```

**Handling Conflicting Objectives:**

```
If energy savings vs. comfort conflict:

"You have two conflicting objectives:
- Reduce energy consumption (current load: 8.2 kW)
- Maintain thermal comfort (current PPD: 22%)

Given the hard constraint that PPD must be < 20%:
1. How would you resolve this conflict?
2. Which zones should be prioritized?
3. What is the minimum acceptable energy level?
4. Should occupancy constraints be relaxed?"
```

## Evaluation Metrics for Prompt Quality

**Metric 1: Constraint Compliance Rate**
```
violations = count(actions where constraints violated)
compliance_rate = 1 - (violations / total_actions)
Target: > 99%
```

**Metric 2: Energy Savings Accuracy**
```
predicted_savings = LLM forecast
actual_savings = measured in simulation
accuracy = 1 - abs(predicted - actual) / actual
Target: > 90%
```

**Metric 3: Comfort Maintenance**
```
baseline_ppd = 8.5%
optimized_ppd = mean(PPD across all hours)
quality = (baseline_ppd - optimized_ppd) / baseline_ppd
Target: > 0 (improvement or no degradation)
```

**Metric 4: Response Latency**
```
ttl = time to generate recommendation
Target: < 30 seconds for real-time control
```

## Advanced Techniques

### 1. Retrieval-Augmented Generation (RAG)

Include domain-specific knowledge:

```python
def enrich_prompt_with_rag(base_prompt, building_type):
    """Add relevant knowledge about similar buildings"""
    
    knowledge_base = {
        "office": "Typical office cooling loads peak at 2-4 PM...",
        "retail": "Retail spaces typically allow wider setpoint ranges...",
        "hospital": "Hospital ventilation rates are critical for infection control..."
    }
    
    enriched = base_prompt + "\n\nRELEVANT DOMAIN KNOWLEDGE:\n"
    enriched += knowledge_base.get(building_type, "")
    
    return enriched
```

### 2. Multi-Turn Optimization

Use conversational turns for refinement:

```
Turn 1 (Agent): Recommend initial optimizations
LLM: [generates 5 possible actions]

Turn 2 (Agent): "Which of these has highest confidence 
                 and lowest risk?"
LLM: [ranks and selects top 2]

Turn 3 (Agent): "Combine these into a unified strategy"
LLM: [creates integrated action plan]
```

### 3. Adversarial Prompt Testing

Validate prompt robustness:

```python
# Test: What if setpoint is already at limit?
test_case = {
    "target_temperature": 26.0,  # Already at max
    "current_temperature": 25.9,
    "occupancy": 1.0,
    "hvac_load": 9.5
}

# LLM should respond: "Already at maximum allowable temperature.
# Consider non-temperature strategies (ventilation, shading, etc.)"
```

---

**Version**: 1.0  
**Last Updated**: 2024-07-26
