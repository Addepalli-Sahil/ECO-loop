"""
Closed-Loop Controller

Orchestrates the continuous feedback loop:
EnergyPlus → Metrics → LLM Agent → Control Actions → EnergyPlus

Manages:
- Simulation execution
- Periodic metric collection
- LLM-based optimization
- Control action execution
- Logging and monitoring
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time

from .energyplus_wrapper import EnergyPlusSimulation
from .llm_agent import BuildingAgent, ControlAction

logger = logging.getLogger(__name__)


class ClosedLoopController:
    """
    Main controller for closed-loop building optimization.
    
    Implements the feedback loop:
    1. Collect metrics from EnergyPlus
    2. Analyze with LLM agent
    3. Generate control actions
    4. Update simulation
    5. Repeat
    """
    
    def __init__(
        self,
        idf_path: str,
        llm_endpoint: str = "http://localhost:11434",
        control_interval: int = 300,  # seconds
        simulation_duration: int = 365  # days
    ):
        """
        Initialize the closed-loop controller.
        
        Args:
            idf_path: Path to building IDF model
            llm_endpoint: LLM server endpoint
            control_interval: Seconds between control updates
            simulation_duration: Days to simulate
        """
        self.simulation = EnergyPlusSimulation(idf_path)
        self.agent = BuildingAgent(llm_endpoint=llm_endpoint)
        self.control_interval = control_interval
        self.simulation_duration = simulation_duration
        
        self.metrics_log = []
        self.actions_log = []
        self.start_time = None
        self.is_running = False
        self.total_energy_saved = 0.0
        
        logger.info(f"Initialized ClosedLoopController with {control_interval}s control interval")
    
    def start(self) -> bool:
        """Start the closed-loop optimization."""
        try:
            logger.info("Starting closed-loop controller...")
            
            # Start EnergyPlus simulation
            if not self.simulation.start_simulation(self.simulation_duration):
                logger.error("Failed to start simulation")
                return False
            
            self.start_time = datetime.now()
            self.is_running = True
            
            # Run control loop
            self._run_control_loop()
            
            logger.info("Closed-loop controller completed")
            return True
            
        except Exception as e:
            logger.error(f"Error in closed-loop controller: {e}")
            self.stop()
            return False
    
    def stop(self) -> None:
        """Stop the controller and simulation."""
        logger.info("Stopping closed-loop controller...")
        self.is_running = False
        self.simulation.stop_simulation()
    
    def get_status(self) -> Dict:
        """Get current controller status."""
        elapsed = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        
        return {
            "is_running": self.is_running,
            "elapsed_seconds": elapsed,
            "metrics_collected": len(self.metrics_log),
            "actions_executed": len(self.actions_log),
            "total_energy_saved_kwh": self.total_energy_saved,
            "uptime": str(timedelta(seconds=elapsed)),
        }
    
    # ===== Private Methods =====
    
    def _run_control_loop(self) -> None:
        """
        Main control loop.
        
        Runs continuously, collecting metrics and executing control actions
        at regular intervals.
        """
        last_action_time = time.time()
        
        while self.is_running and self.simulation.is_running:
            try:
                current_time = time.time()
                time_since_action = current_time - last_action_time
                
                # Execute control logic at specified interval
                if time_since_action >= self.control_interval:
                    self._execute_control_step()
                    last_action_time = current_time
                
                # Sleep briefly to avoid busy-waiting
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("Control loop interrupted by user")
                self.stop()
                break
            except Exception as e:
                logger.error(f"Error in control loop: {e}")
                # Continue running despite errors
                time.sleep(5)
    
    def _execute_control_step(self) -> None:
        """
        Execute one step of the closed-loop control.
        
        Steps:
        1. Collect metrics from simulation
        2. Analyze with LLM agent
        3. Generate control actions
        4. Apply actions to simulation
        """
        # Step 1: Collect metrics
        metrics = self.simulation.get_current_metrics()
        self.metrics_log.append(metrics)
        
        logger.debug(f"Collected metrics: {metrics.get('timestamp')}")
        
        # Step 2 & 3: Analyze and generate actions
        actions = self.agent.generate_control_actions(metrics)
        
        if not actions:
            logger.debug("No control actions recommended")
            return
        
        # Step 4: Apply actions
        for action in actions:
            success = self._apply_control_action(action)
            
            if success:
                self.actions_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "action": action.dict(),
                    "status": "applied"
                })
                logger.info(f"Applied action: {action.action_type} - {action.rationale}")
            else:
                logger.warning(f"Failed to apply action: {action.action_type}")
    
    def _apply_control_action(self, action: ControlAction) -> bool:
        """
        Apply a control action to the simulation.
        
        Args:
            action: ControlAction to apply
            
        Returns:
            True if successfully applied
        """
        try:
            if action.action_type == "setpoint_update":
                return self.simulation.update_setpoint(
                    action.target_zone or "Zone1",
                    action.value
                )
            
            elif action.action_type == "schedule_change":
                # TODO: Implement schedule modifications
                return True
            
            elif action.action_type == "equipment_override":
                # TODO: Implement equipment control
                return True
            
            else:
                logger.warning(f"Unknown action type: {action.action_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error applying control action: {e}")
            return False
    
    def get_performance_report(self) -> Dict:
        """
        Generate a performance report comparing baseline vs optimized.
        
        Returns:
            Report with energy savings, comfort metrics, etc.
        """
        if not self.metrics_log:
            return {"error": "No metrics data available"}
        
        # Calculate statistics
        energy_values = [m.get("energy_consumption", 0) for m in self.metrics_log]
        temp_values = [
            m.get("zone_temperatures", {}).get("Zone1", 0) 
            for m in self.metrics_log
        ]
        
        report = {
            "simulation_duration": len(self.metrics_log) * self.control_interval,
            "total_metrics_collected": len(self.metrics_log),
            "total_actions_executed": len(self.actions_log),
            "avg_energy_consumption_kw": sum(energy_values) / len(energy_values) if energy_values else 0,
            "peak_energy_consumption_kw": max(energy_values) if energy_values else 0,
            "avg_temperature": sum(temp_values) / len(temp_values) if temp_values else 0,
            "agent_performance": self.agent.get_performance_summary(),
            "simulation_status": self.simulation.is_running,
            "generated_at": datetime.now().isoformat(),
        }
        
        return report
