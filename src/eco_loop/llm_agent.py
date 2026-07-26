"""
LLM Agent for Building Optimization

Implements an AI agent that:
- Analyzes building performance metrics
- Reasons about energy conservation measures (ECMs)
- Generates control recommendations
- Learns from simulation feedback
- Handles errors and adapts strategies
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MetricsAnalysis(BaseModel):
    """Analysis of building metrics."""
    current_temperature: float
    target_temperature: float
    occupancy_ratio: float
    thermal_comfort_index: float
    energy_consumption_kw: float
    hvac_load_kw: float


class ControlAction(BaseModel):
    """Recommended control action."""
    action_type: str = Field(..., description="Type: setpoint_update, schedule_change, equipment_override")
    target_zone: Optional[str] = Field(None, description="Target zone if applicable")
    value: float = Field(..., description="Target value")
    confidence: float = Field(..., ge=0, le=1, description="Confidence level 0-1")
    rationale: str = Field(..., description="Explanation for the action")


class BuildingAgent:
    """
    AI Agent for autonomous building management.
    
    Uses an LLM to:
    1. Analyze current building state
    2. Identify energy-saving opportunities
    3. Generate optimal control actions
    4. Monitor thermal comfort constraints
    """
    
    def __init__(self, llm_endpoint: str = "http://localhost:11434", model: str = "llama2"):
        """
        Initialize the building agent.
        
        Args:
            llm_endpoint: URL of LLM server (Ollama default)
            model: Model name (llama2, mistral, qwen, etc.)
        """
        self.llm_endpoint = llm_endpoint
        self.model = model
        self.metrics_history = []
        self.action_history = []
        self.constraint_limits = {
            "min_temperature": 18.0,
            "max_temperature": 26.0,
            "max_ppd": 20.0,  # Max 20% dissatisfied
            "comfort_range": 0.5,  # PMV +/- 0.5
        }
        
        logger.info(f"Initialized Building Agent with model: {model}")
    
    def analyze_metrics(self, metrics: Dict[str, Any]) -> MetricsAnalysis:
        """
        Analyze current building metrics.
        
        Args:
            metrics: Dictionary of building metrics
            
        Returns:
            Structured analysis
        """
        analysis = MetricsAnalysis(
            current_temperature=metrics.get("zone_temperatures", {}).get("Zone1", 22.0),
            target_temperature=22.0,
            occupancy_ratio=metrics.get("occupancy", 0.5),
            thermal_comfort_index=metrics.get("pmv", 0.0),
            energy_consumption_kw=metrics.get("energy_consumption", 0.0),
            hvac_load_kw=metrics.get("hvac_load", 0.0),
        )
        
        self.metrics_history.append(analysis)
        logger.debug(f"Analyzed metrics: {analysis}")
        
        return analysis
    
    def generate_control_actions(
        self, 
        metrics: Dict[str, Any],
        time_of_day: Optional[str] = None
    ) -> List[ControlAction]:
        """
        Generate optimal control actions based on metrics.
        
        Uses LLM reasoning to determine energy-saving measures while
        respecting comfort constraints.
        
        Args:
            metrics: Current building metrics
            time_of_day: Optional time context (e.g., "morning", "evening")
            
        Returns:
            List of recommended control actions
        """
        analysis = self.analyze_metrics(metrics)
        
        # Build prompt for LLM
        prompt = self._build_optimization_prompt(analysis, time_of_day)
        
        try:
            # Query LLM for recommendations
            response = self._query_llm(prompt)
            actions = self._parse_llm_response(response)
            
            # Filter actions against constraints
            valid_actions = self._validate_actions_against_constraints(actions, analysis)
            
            self.action_history.extend(valid_actions)
            logger.info(f"Generated {len(valid_actions)} control actions")
            
            return valid_actions
            
        except Exception as e:
            logger.error(f"Error generating control actions: {e}")
            # Return safe default actions
            return self._get_default_actions(analysis)
    
    def update_constraints(self, new_limits: Dict[str, float]) -> None:
        """Update operational constraints."""
        self.constraint_limits.update(new_limits)
        logger.info(f"Updated constraints: {self.constraint_limits}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get summary of agent performance.
        
        Returns:
            Summary statistics about energy savings and comfort
        """
        if not self.metrics_history:
            return {"error": "No metrics history available"}
        
        return {
            "total_actions": len(self.action_history),
            "metrics_analyzed": len(self.metrics_history),
            "avg_temperature": sum(m.current_temperature for m in self.metrics_history) / len(self.metrics_history),
            "avg_energy_consumption": sum(m.energy_consumption_kw for m in self.metrics_history) / len(self.metrics_history),
            "timestamp": datetime.now().isoformat(),
        }
    
    # ===== Private Methods =====
    
    def _build_optimization_prompt(self, analysis: MetricsAnalysis, time_of_day: Optional[str]) -> str:
        """Build prompt for LLM optimization."""
        prompt = f"""
You are an autonomous building energy optimization agent. Analyze the following building state and recommend 
energy conservation measures that maintain thermal comfort.

CURRENT STATE:
- Zone Temperature: {analysis.current_temperature}°C
- Target Temperature: {analysis.target_temperature}°C
- Occupancy: {analysis.occupancy_ratio * 100}%
- Thermal Comfort (PMV): {analysis.thermal_comfort_index}
- Energy Consumption: {analysis.energy_consumption_kw} kW
- HVAC Load: {analysis.hvac_load_kw} kW
{"- Time of Day: " + time_of_day if time_of_day else ""}

CONSTRAINTS (MUST RESPECT):
- Temperature range: {self.constraint_limits['min_temperature']}°C to {self.constraint_limits['max_temperature']}°C
- Max dissatisfied: {self.constraint_limits['max_ppd']}%
- Comfort index: {self.constraint_limits['comfort_range']} PMV units

RECOMMENDATIONS:
Based on this state, provide 2-3 specific energy conservation measures (ECMs) as JSON actions.
Each action should have: action_type, target_zone, value, confidence (0-1), and rationale.

Return ONLY valid JSON array of actions, no other text.
"""
        return prompt
    
    def _query_llm(self, prompt: str) -> str:
        """Query the LLM server for recommendations."""
        import requests
        
        try:
            response = requests.post(
                f"{self.llm_endpoint}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                logger.error(f"LLM API error: {response.status_code}")
                return ""
                
        except requests.exceptions.ConnectionError:
            logger.warning(f"Cannot connect to LLM at {self.llm_endpoint}")
            return ""
    
    def _parse_llm_response(self, response: str) -> List[ControlAction]:
        """Parse LLM response into structured actions."""
        try:
            # Extract JSON from response
            json_start = response.find("[")
            json_end = response.rfind("]") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                actions_data = json.loads(json_str)
                
                actions = [ControlAction(**action) for action in actions_data]
                logger.debug(f"Parsed {len(actions)} actions from LLM response")
                return actions
                
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse LLM response: {e}")
        
        return []
    
    def _validate_actions_against_constraints(
        self, 
        actions: List[ControlAction], 
        analysis: MetricsAnalysis
    ) -> List[ControlAction]:
        """Filter actions to ensure they respect constraints."""
        valid_actions = []
        
        for action in actions:
            # Check temperature constraints
            if action.action_type == "setpoint_update":
                if not (self.constraint_limits["min_temperature"] <= action.value <= self.constraint_limits["max_temperature"]):
                    logger.warning(f"Action {action} violates temperature constraints, skipping")
                    continue
            
            valid_actions.append(action)
        
        return valid_actions
    
    def _get_default_actions(self, analysis: MetricsAnalysis) -> List[ControlAction]:
        """Return safe default actions when LLM is unavailable."""
        # Simple rules-based fallback
        actions = []
        
        if analysis.current_temperature > analysis.target_temperature + 1:
            actions.append(ControlAction(
                action_type="setpoint_update",
                target_zone="Zone1",
                value=analysis.target_temperature,
                confidence=0.6,
                rationale="Reduce setpoint due to elevated temperature"
            ))
        
        return actions
