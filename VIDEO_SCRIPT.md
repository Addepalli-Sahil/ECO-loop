# Three-minute PoC demonstration script

## 0:00–0:20 — Problem and system

Show the architecture diagram. Explain that the system observes building energy
and comfort state, lets a constrained agent select energy-conservation actions,
and records the resulting evidence.

## 0:20–0:50 — Start a validated EnergyPlus run

Show `energyplus --version`, the baseline IDF, the selected `.epw` file, and the
terminal command that starts the run. Show live output/metrics rather than a
static slide.

## 0:50–1:35 — Closed loop

Show metrics arriving (zone temperature, HVAC load, kWh and PMV/PPD), the agent's
structured action, constraint check, and the resulting setpoint/schedule update.
Narrate why the action respects PMV +/-0.5 and PPD below 20%.

## 1:35–2:25 — Dashboard evidence

Open `streamlit_app.py` on the dashboard. Show baseline/optimized kWh, peak
demand, PMV/PPD, and the action log. State whether this data is demo or validated
EnergyPlus output; never label demo data as measured output.

## 2:25–3:00 — Impact and close

Show percentage kWh reduction, cost assumption, comfort boundary compliance and
the GitHub repository. Close with the scaling approach: calibrate the IDF, map
EMS actuators zone-by-zone, and preserve audit logs.
