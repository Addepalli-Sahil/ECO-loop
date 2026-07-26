"""
Utility functions for Eco-Loop system.
"""

import logging
from typing import Dict, List, Any
from datetime import datetime
import json


def setup_logging(log_level: str = "INFO") -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def save_metrics_to_json(metrics: List[Dict[str, Any]], filepath: str) -> bool:
    """Save metrics log to JSON file."""
    try:
        with open(filepath, 'w') as f:
            json.dump(metrics, f, indent=2, default=str)
        return True
    except Exception as e:
        logging.error(f"Error saving metrics to {filepath}: {e}")
        return False


def load_metrics_from_json(filepath: str) -> List[Dict[str, Any]]:
    """Load metrics from JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading metrics from {filepath}: {e}")
        return []


def calculate_energy_savings(baseline: List[float], optimized: List[float]) -> Dict[str, float]:
    """
    Calculate energy savings between baseline and optimized scenarios.
    
    Args:
        baseline: List of baseline energy values
        optimized: List of optimized energy values
        
    Returns:
        Dictionary with savings metrics
    """
    if not baseline or not optimized or len(baseline) != len(optimized):
        return {}
    
    total_baseline = sum(baseline)
    total_optimized = sum(optimized)
    absolute_savings = total_baseline - total_optimized
    percent_savings = (absolute_savings / total_baseline * 100) if total_baseline > 0 else 0
    
    return {
        "total_baseline_kwh": total_baseline,
        "total_optimized_kwh": total_optimized,
        "absolute_savings_kwh": absolute_savings,
        "percent_savings": percent_savings,
    }


def format_performance_summary(report: Dict[str, Any]) -> str:
    """Format performance report for display."""
    summary = []
    summary.append("=" * 60)
    summary.append("BUILDING OPTIMIZATION PERFORMANCE REPORT")
    summary.append("=" * 60)
    
    for key, value in report.items():
        if isinstance(value, (int, float)):
            summary.append(f"{key.replace('_', ' ').title()}: {value:.2f}")
        else:
            summary.append(f"{key.replace('_', ' ').title()}: {value}")
    
    summary.append("=" * 60)
    return "\n".join(summary)
