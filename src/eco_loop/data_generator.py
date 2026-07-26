"""
Data Generator for Building Simulation Results

Creates realistic simulation data for demonstration and testing.
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path


def generate_simulation_results(duration_days=365, output_dir="results"):
    """
    Generate realistic building simulation results.
    
    Args:
        duration_days: Number of days to simulate
        output_dir: Directory to save results
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Create date range
    dates = pd.date_range(start='2024-01-01', periods=duration_days*24, freq='h')
    
    # Generate baseline energy profile
    baseline_energy = []
    hours_array = []
    dow_array = []
    months_array = []
    
    for i, dt in enumerate(dates):
        hours_array.append(dt.hour)
        dow_array.append(dt.dayofweek)
        months_array.append(dt.month)
        
        hour = dt.hour
        day_of_week = dt.dayofweek
        month = dt.month
        
        # Components of building load
        base_load = 15 + 5 * (month / 12)  # HVAC minimum + seasonal variation
        
        # Occupancy-driven load (9-5 on weekdays)
        if day_of_week < 5 and 9 <= hour < 17:
            occupancy_load = 30 + 10 * (1 - abs(hour - 13) / 8)
        else:
            occupancy_load = 5  # Reduced evening/weekend load
        
        # Weather effect
        weather_factor = 5 * np.sin((month - 1) / 12 * 2 * np.pi)
        
        # Random variation
        noise = np.random.normal(0, 2)
        
        total = base_load + occupancy_load + weather_factor + noise
        baseline_energy.append(max(5, total))
    
    baseline_energy = np.array(baseline_energy)
    hours_array = np.array(hours_array)
    
    # AI-optimized energy (15% reduction)
    optimized_energy = baseline_energy * 0.85 + np.random.normal(0, 1, len(baseline_energy))
    optimized_energy = np.maximum(optimized_energy, 3)
    
    # Thermal comfort metrics
    pmv_baseline = np.random.normal(0.15, 0.35, len(dates))
    pmv_optimized = np.random.normal(0.05, 0.25, len(dates))
    
    ppd_baseline = np.maximum(5 + 3 * np.abs(pmv_baseline), 0)
    ppd_optimized = np.maximum(5 + 3 * np.abs(pmv_optimized), 0)
    
    # Zone temperatures
    zone_temps_baseline = 21 + 2.5 * np.sin((hours_array - 12) / 12 * np.pi) + np.random.normal(0, 1.2, len(dates))
    zone_temps_optimized = 21 + 2 * np.sin((hours_array - 12) / 12 * np.pi) + np.random.normal(0, 0.9, len(dates))
    
    # Control actions log
    actions_log = []
    for i in range(0, len(dates), 60):  # Every 5 hours, log some actions
        if i < len(dates):
            actions_log.append({
                "timestamp": dates[i].isoformat(),
                "action_type": "setpoint_update",
                "zone": "Zone1",
                "value": float(20 + 2 * np.sin(dates[i].hour / 24 * 2 * np.pi)),
                "confidence": 0.85 + np.random.random() * 0.1,
                "rationale": "Optimized for energy efficiency"
            })
    
    # Save metrics log
    metrics_log = {
        "timestamps": [dt.isoformat() for dt in dates],
        "baseline_energy_kw": baseline_energy.tolist(),
        "optimized_energy_kw": optimized_energy.tolist(),
        "pmv_baseline": pmv_baseline.tolist(),
        "pmv_optimized": pmv_optimized.tolist(),
        "ppd_baseline": ppd_baseline.tolist(),
        "ppd_optimized": ppd_optimized.tolist(),
        "zone_temps_baseline": zone_temps_baseline.tolist(),
        "zone_temps_optimized": zone_temps_optimized.tolist(),
    }
    
    # Save reports
    performance_report = {
        "simulation_duration_days": duration_days,
        "simulation_duration_hours": len(dates),
        "total_metrics_collected": len(dates),
        "total_actions_executed": len(actions_log),
        "baseline_total_kwh": float(baseline_energy.sum()),
        "optimized_total_kwh": float(optimized_energy.sum()),
        "energy_saved_kwh": float(baseline_energy.sum() - optimized_energy.sum()),
        "percent_savings": float((baseline_energy.sum() - optimized_energy.sum()) / baseline_energy.sum() * 100),
        "cost_per_kwh": 0.12,
        "cost_savings": float((baseline_energy.sum() - optimized_energy.sum()) * 0.12),
        "avg_temperature_baseline": float(zone_temps_baseline.mean()),
        "avg_temperature_optimized": float(zone_temps_optimized.mean()),
        "avg_pmv_baseline": float(pmv_baseline.mean()),
        "avg_pmv_optimized": float(pmv_optimized.mean()),
        "avg_ppd_baseline": float(ppd_baseline.mean()),
        "avg_ppd_optimized": float(ppd_optimized.mean()),
        "peak_load_baseline_kw": float(baseline_energy.max()),
        "peak_load_optimized_kw": float(optimized_energy.max()),
        "generated_at": datetime.now().isoformat(),
    }
    
    # Write files
    with open(output_path / "metrics_log.json", "w") as f:
        json.dump(metrics_log, f, indent=2)
    
    with open(output_path / "performance_report.json", "w") as f:
        json.dump(performance_report, f, indent=2)
    
    with open(output_path / "actions_log.json", "w") as f:
        json.dump(actions_log, f, indent=2)
    
    print(f"✅ Generated simulation results in {output_path}")
    print(f"   - Energy Saved: {performance_report['energy_saved_kwh']:,.0f} kWh ({performance_report['percent_savings']:.1f}%)")
    print(f"   - Cost Savings: ${performance_report['cost_savings']:,.2f}")
    print(f"   - Comfort Improvement: PMV {performance_report['avg_pmv_baseline']:.2f} → {performance_report['avg_pmv_optimized']:.2f}")
    
    return performance_report


if __name__ == "__main__":
    # Generate sample data
    generate_simulation_results(duration_days=365, output_dir="results")
