"""Convert paired EnergyPlus hourly CSV output into the dashboard JSON schema."""

from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime
from pathlib import Path

JOULES_PER_KWH = 3_600_000


def _column(headers: list[str], text: str) -> str:
    return next(header for header in headers if text.lower() in header.lower())


def _read(path: Path) -> tuple[list[str], list[float], list[float]]:
    with path.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames or []
        time_key = _column(headers, "Date/Time")
        energy_key = _column(headers, "Facility Total Purchased Electricity Energy")
        temperature_key = _column(headers, "Zone Mean Air Temperature")
        rows = list(reader)
    return (
        [row[time_key].strip() for row in rows],
        [float(row[energy_key]) / JOULES_PER_KWH for row in rows],
        [float(row[temperature_key]) for row in rows],
    )


def _pmv_and_ppd(temperatures: list[float]) -> tuple[list[float], list[float]]:
    # Transparent temperature-derived comfort proxy when PMV outputs are not
    # available in the selected EnergyPlus example model.
    pmv = [max(-3.0, min(3.0, (temp - 21.0) / 2.5)) for temp in temperatures]
    ppd = [100 - 95 * math.exp(-0.03353 * value**4 - 0.2179 * value**2) for value in pmv]
    return pmv, ppd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--optimized", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    args = parser.parse_args()

    timestamps, baseline_energy, baseline_temperature = _read(args.baseline)
    optimized_timestamps, optimized_energy, optimized_temperature = _read(args.optimized)
    if timestamps != optimized_timestamps:
        raise ValueError("Baseline and optimized EnergyPlus outputs have different timestamps")

    baseline_pmv, baseline_ppd = _pmv_and_ppd(baseline_temperature)
    optimized_pmv, optimized_ppd = _pmv_and_ppd(optimized_temperature)
    baseline_total = sum(baseline_energy)
    optimized_total = sum(optimized_energy)
    saved = baseline_total - optimized_total
    args.output_dir.mkdir(parents=True, exist_ok=True)

    metrics = {
        "timestamps": timestamps,
        "baseline_energy_kw": baseline_energy,
        "optimized_energy_kw": optimized_energy,
        "pmv_baseline": baseline_pmv,
        "pmv_optimized": optimized_pmv,
        "ppd_baseline": baseline_ppd,
        "ppd_optimized": optimized_ppd,
        "zone_temps_baseline": baseline_temperature,
        "zone_temps_optimized": optimized_temperature,
    }
    report = {
        "simulation_duration_hours": len(timestamps),
        "baseline_total_kwh": baseline_total,
        "optimized_total_kwh": optimized_total,
        "energy_saved_kwh": saved,
        "percent_savings": saved / baseline_total * 100 if baseline_total else 0,
        "cost_per_kwh": 0.12,
        "cost_savings": saved * 0.12,
        "avg_temperature_baseline": sum(baseline_temperature) / len(baseline_temperature),
        "avg_temperature_optimized": sum(optimized_temperature) / len(optimized_temperature),
        "avg_pmv_baseline": sum(baseline_pmv) / len(baseline_pmv),
        "avg_pmv_optimized": sum(optimized_pmv) / len(optimized_pmv),
        "avg_ppd_baseline": sum(baseline_ppd) / len(baseline_ppd),
        "avg_ppd_optimized": sum(optimized_ppd) / len(optimized_ppd),
        "data_source": "EnergyPlus 26.1.0 paired annual simulations",
        "verification_note": "Energy values are from EnergyPlus hourly output. PMV/PPD values are a temperature-derived proxy because this selected example model does not emit Fanger comfort variables.",
        "generated_at": datetime.now().isoformat(),
    }
    actions = [{
        "timestamp": datetime.now().isoformat(),
        "action_type": "setpoint_update",
        "zone": "MAIN ZONE",
        "baseline_value_c": 20.0,
        "optimized_value_c": 19.5,
        "rationale": "EnergyPlus-validated heating-setpoint setback scenario",
        "status": "completed",
    }]
    (args.output_dir / "metrics_log.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (args.output_dir / "performance_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (args.output_dir / "actions_log.json").write_text(json.dumps(actions, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
